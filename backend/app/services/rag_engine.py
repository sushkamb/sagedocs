import json
import logging
import os
import re

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import settings
from app.services.llm_service import LLMService
from app.services.document_processor import DocumentProcessor

logger = logging.getLogger(__name__)

# Pattern to extract image filenames from [Screenshot: filename | description] markers
SCREENSHOT_PATTERN = re.compile(r"\[Screenshot:\s*(img_[a-f0-9]+\.\w+)\s*\|")


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
            metadata={"hnsw:space": "cosine"},
        )

    def _load_tenant_config(self, tenant: str) -> dict:
        """Load per-tenant configuration from JSON file."""
        config_path = os.path.join(settings.chroma_persist_dir, "..", "tenants", f"{tenant}.json")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                return json.load(f)
        return {}

    def _rerank(self, question: str, candidates: list[dict]) -> list[dict]:
        """Rerank candidates using combined embedding distance + keyword overlap score."""
        # Extract question keywords (lowercase, 3+ chars, no stopwords)
        stopwords = {"the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
                     "have", "has", "had", "do", "does", "did", "will", "would", "could",
                     "should", "may", "might", "can", "shall", "for", "and", "but", "or",
                     "nor", "not", "so", "yet", "both", "either", "neither", "each", "every",
                     "all", "any", "few", "more", "most", "other", "some", "such", "than",
                     "too", "very", "just", "how", "what", "when", "where", "which", "who",
                     "why", "this", "that", "these", "those", "with", "from", "into", "about"}

        words = re.findall(r'\b\w+\b', question.lower())
        keywords = [w for w in words if len(w) >= 3 and w not in stopwords]

        if not keywords:
            # Fall back to distance-only ranking
            return sorted(candidates, key=lambda c: c["distance"])

        for candidate in candidates:
            # Distance score: 0 (worst) to 1 (best)
            distance_score = 1.0 - candidate["distance"]

            # Keyword overlap score
            chunk_lower = candidate["text"].lower()
            matches = sum(1 for kw in keywords if kw in chunk_lower)
            keyword_score = matches / len(keywords)

            # Combined score (distance weighted more heavily)
            candidate["score"] = distance_score * 0.7 + keyword_score * 0.3

        return sorted(candidates, key=lambda c: c["score"], reverse=True)

    def ingest_document(self, file_path: str, title: str, tenant: str) -> int:
        """Process and store a document. Returns the number of chunks created."""

        logger.info("Ingesting document: tenant=%s title=%r file=%s", tenant, title, file_path)
        chunks = self.doc_processor.process_file(file_path, title, tenant)
        logger.info("Document chunked: %d chunks from %r", len(chunks), title)

        collection = self._get_collection(tenant)

        ids = [c["id"] for c in chunks]
        documents = [c["text"] for c in chunks]
        metadatas = [c["metadata"] for c in chunks]

        # Generate embeddings
        logger.info("Generating embeddings for %d chunks", len(chunks))
        embeddings = [self.llm.get_embedding(doc) for doc in documents]

        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings,
        )
        logger.info("Stored %d chunks in ChromaDB for tenant=%s", len(chunks), tenant)

        return len(chunks)

    def delete_document(self, tenant: str, filename: str):
        """Delete all chunks for a specific document."""
        collection = self._get_collection(tenant)
        # Query for all chunks with this filename
        results = collection.get(where={"filename": filename})
        if results["ids"]:
            collection.delete(ids=results["ids"])

    def query(self, tenant: str, question: str, top_k: int = None) -> dict:
        """Answer a question using RAG with similarity filtering and reranking."""
        logger.info("RAG query: tenant=%s question=%r", tenant, question[:120])
        tenant_config = self._load_tenant_config(tenant)

        final_k = top_k or tenant_config.get("rag_top_k") or settings.rag_top_k
        retrieval_k = settings.rag_retrieval_k
        threshold = tenant_config.get("similarity_threshold") or settings.similarity_threshold
        temperature = tenant_config.get("help_temperature") or settings.help_temperature
        logger.debug("RAG params: top_k=%d retrieval_k=%d threshold=%.2f temp=%.2f",
                      final_k, retrieval_k, threshold, temperature)

        collection = self._get_collection(tenant)
        question_embedding = self.llm.get_embedding(question)

        results = collection.query(
            query_embeddings=[question_embedding],
            n_results=retrieval_k,
            where={"tenant": tenant},
            include=["documents", "metadatas", "distances"],
        )

        total_retrieved = len(results["documents"][0]) if results["documents"] and results["documents"][0] else 0
        logger.info("ChromaDB returned %d candidates", total_retrieved)

        if not results["documents"] or not results["documents"][0]:
            logger.warning("No documents found in collection for tenant=%s", tenant)
            return {
                "reply": "I don't have any documentation to answer that question yet. Please contact support for help.",
                "sources": [],
                "images": [],
            }

        # Log all candidate distances for debugging
        all_distances = results["distances"][0]
        logger.info("Candidate distances: min=%.4f max=%.4f median=%.4f threshold=%.2f",
                     min(all_distances), max(all_distances),
                     sorted(all_distances)[len(all_distances) // 2], threshold)

        # Filter by similarity threshold and rerank
        candidates = []
        filtered_out = 0
        for i, doc in enumerate(results["documents"][0]):
            distance = results["distances"][0][i]
            if distance > threshold:
                filtered_out += 1
                continue
            meta = results["metadatas"][0][i]
            candidates.append({
                "text": doc,
                "metadata": meta,
                "distance": distance,
            })

        logger.info("After threshold filter: %d kept, %d filtered out (threshold=%.2f)",
                     len(candidates), filtered_out, threshold)

        if not candidates:
            logger.warning("All candidates filtered out — consider lowering SIMILARITY_THRESHOLD (currently %.2f)", threshold)
            return {
                "reply": "I couldn't find documentation closely matching your question. Could you rephrase it, or contact support for help?",
                "sources": [],
                "images": [],
            }

        # Rerank: combined score of embedding distance + keyword overlap
        ranked = self._rerank(question, candidates)
        top_chunks = ranked[:final_k]

        logger.info("Top %d chunks after reranking:", len(top_chunks))
        for i, chunk in enumerate(top_chunks):
            meta = chunk["metadata"]
            logger.info("  [%d] score=%.4f dist=%.4f file=%s chunk=%d",
                        i, chunk.get("score", 0), chunk["distance"],
                        meta.get("filename", "?"), meta.get("chunk_index", 0))

        # Build context ordered by relevance
        context_parts = []
        sources = []
        image_filenames = []
        for i, chunk in enumerate(top_chunks):
            meta = chunk["metadata"]
            relevance = "HIGH" if i < 3 else "MEDIUM"
            context_parts.append(f"[Source: {meta.get('title', 'Unknown')} | Relevance: {relevance}]\n{chunk['text']}")
            sources.append({
                "title": meta.get("title", "Unknown"),
                "filename": meta.get("filename", ""),
                "chunk_index": meta.get("chunk_index", 0),
            })
            for match in SCREENSHOT_PATTERN.finditer(chunk["text"]):
                img_file = match.group(1)
                if img_file not in image_filenames:
                    image_filenames.append(img_file)

        context = "\n\n---\n\n".join(context_parts)

        # Build system prompt with per-tenant customization
        tenant_display = tenant_config.get("display_name", tenant)
        custom_instructions = tenant_config.get("system_prompt", "")

        system_prompt = (
            f"You are SageDocs, an expert support assistant for {tenant_display}. "
            "Your role is to help users by answering questions accurately using the provided documentation.\n\n"
        )

        if custom_instructions:
            system_prompt += f"## Additional Instructions\n{custom_instructions}\n\n"

        system_prompt += (
            "## Rules\n"
            "- Answer ONLY based on the documentation provided below. Do not use outside knowledge.\n"
            "- If the documentation does not contain enough information to fully answer, clearly state what "
            "you found and what is missing, then suggest contacting support.\n"
            "- Structure your response with clear visual hierarchy:\n"
            "  - Use **bold** for key terms, UI labels, button names, and important values.\n"
            "  - Use `##` or `###` headings when covering multiple distinct topics or long answers.\n"
            "  - Use numbered steps (1. 2. 3.) for procedures and bullet points for lists.\n"
            "  - Use markdown tables when comparing options, features, or settings.\n"
            "  - Use blockquotes (> ) for important notes, warnings, or tips.\n"
            "  - Format navigation paths as: **Settings > Billing > Plans**\n"
            "- Keep responses concise — prefer structured formatting over long paragraphs.\n"
            "- When documentation includes [Screenshot: ...] markers, reference those visual descriptions "
            "to give specific UI guidance (e.g., 'click the blue **Save** button in the top-right corner').\n"
            "- Quote specific UI labels, button names, and menu paths exactly as they appear.\n"
            "- If multiple sources cover the topic, synthesize into a coherent answer.\n"
            "- Chunks marked HIGH relevance are most likely to contain the answer.\n\n"
            f"## Documentation (ordered by relevance)\n{context}"
        )

        logger.debug("System prompt length: %d chars, context length: %d chars",
                     len(system_prompt), len(context))
        result = self.llm.chat(system_prompt, question, temperature=temperature)
        logger.info("LLM reply length: %d chars, sources: %d, images: %d",
                     len(result["reply"]), len(sources), len(image_filenames))

        # Deduplicate sources
        seen = set()
        unique_sources = []
        for s in sources:
            key = s["filename"]
            if key not in seen:
                seen.add(key)
                unique_sources.append(s)

        image_urls = [f"/data/images/{tenant}/{img}" for img in image_filenames]

        return {
            "reply": result["reply"],
            "sources": unique_sources,
            "images": image_urls,
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
