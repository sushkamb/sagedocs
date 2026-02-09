import os
import uuid
from datetime import datetime
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader


class DocumentProcessor:
    """Handles document parsing, chunking, and preparation for embedding."""

    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 200):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def process_file(self, file_path: str, title: str, tenant: str) -> list[dict]:
        """Process a file and return a list of chunk dicts ready for ChromaDB."""

        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".pdf":
            text = self._extract_pdf(file_path)
        elif ext in (".html", ".htm"):
            text = self._extract_html(file_path)
        elif ext in (".md", ".txt"):
            text = self._extract_text(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

        chunks = self.splitter.split_text(text)
        filename = os.path.basename(file_path)

        return [
            {
                "id": f"{tenant}_{filename}_{i}_{uuid.uuid4().hex[:8]}",
                "text": chunk,
                "metadata": {
                    "tenant": tenant,
                    "title": title,
                    "filename": filename,
                    "chunk_index": i,
                    "total_chunks": len(chunks),
                    "uploaded_at": datetime.utcnow().isoformat(),
                },
            }
            for i, chunk in enumerate(chunks)
        ]

    def _extract_pdf(self, file_path: str) -> str:
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
            text += "\n\n"
        return text.strip()

    def _extract_html(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            html = f.read()
        # Simple HTML tag stripping — sufficient for help docs
        import re
        text = re.sub(r"<[^>]+>", " ", html)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def _extract_text(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()
