import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import settings
from app.services.llm_service import LLMService
from app.services.document_processor import DocumentProcessor


class RAGEngine:
    """RAG pipeline: document storage + retrieval + LLM answer generation."""

    def __init__(self):
        self.chroma_client = chromadb.PersistentClient(
            path=settings.chroma_persist_dir,
            settings=ChromaSettings(anonymized_telemetry=False),
        )
        self.doc_processor = DocumentProcessor()
        self.llm = LLMService(model=settings.llm_model_fast)  # Use fast model for help queries

    def _get_collection(self, tenant: str):
        """Get or create a ChromaDB collection for a tenant."""
        return self.chroma_client.get_or_create_collection(
            name=f"tenant_{tenant}",
            metadata={"description": f"Help documents for {tenant}"},
        )

    def ingest_document(self, file_path: str, title: str, tenant: str) -> int:
        """Process and store a document. Returns the number of chunks created."""

        chunks = self.doc_processor.process_file(file_path, title, tenant)
        collection = self._get_collection(tenant)

        ids = [c["id"] for c in chunks]
        documents = [c["text"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]

        # Generate embeddings
        embeddings = [self.llm.get_embedding(doc) for doc in documents]

        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )

        return len(chunks)

    def delete_document(self, tenant: str, filename: str):
        """Delete all chunks for a specific document."""
        collection = self._get_collection(tenant)
        # Query for all chunks with this filename
        results = collection.get(where={"filename": filename})
        if results["ids"]:
            collection.delete(ids=results["ids"])

    def query(self, tenant: str, question: str, top_k: int = 5) -> dict:
        """Answer a question using RAG. Returns { reply, sources }."""

        collection = self._get_collection(tenant)

        # Embed the question and retrieve relevant chunks
        question_embedding = self.llm.get_embedding(question)

        results = collection.query(
            query_embeddings=[question_embedding],
            n_results=top_k,
            where={"tenant": tenant},
        )

        if not results["documents"] or not results["documents"][0]:
            return {
                "reply": "I don't have any documentation to answer that question yet. Please contact support for help.",
                "sources": [],
            }

        # Build context from retrieved chunks
        context_parts = []
        sources = []
        for i, doc in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i]
            context_parts.append(f"[Source: {meta.get('title', 'Unknown')}]\n{doc}")
            sources.append({
                "title": meta.get("title", "Unknown"),
                "filename": meta.get("filename", ""),
                "chunk_index": meta.get("chunk_index", 0),
            })

        context = "\n\n---\n\n".join(context_parts)

        system_prompt = (
            "You are ForteAI, a helpful assistant. Answer the user's question "
            "using ONLY the following documentation. If the answer is not in the "
            "documentation, say so clearly and suggest contacting support.\n\n"
            "Be concise and direct. Use bullet points for step-by-step instructions.\n\n"
            f"Documentation:\n{context}"
        )

        result = self.llm.chat(system_prompt, question)

        # Deduplicate sources
        seen = set()
        unique_sources = []
        for s in sources:
            key = s["filename"]
            if key not in seen:
                seen.add(key)
                unique_sources.append(s)

        return {
            "reply": result["reply"],
            "sources": unique_sources,
        }

    def get_document_list(self, tenant: str) -> list[dict]:
        """List all documents for a tenant with chunk counts."""
        collection = self._get_collection(tenant)
        all_items = collection.get(where={"tenant": tenant})

        docs = {}
        for meta in all_items["metadatas"]:
            filename = meta.get("filename", "unknown")
            if filename not in docs:
                docs[filename] = {
                    "filename": filename,
                    "title": meta.get("title", ""),
                    "chunk_count": 0,
                    "uploaded_at": meta.get("uploaded_at", ""),
                }
            docs[filename]["chunk_count"] += 1

        return list(docs.values())
