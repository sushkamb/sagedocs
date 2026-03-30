import logging
import os
import re
import uuid
import base64
from datetime import datetime
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.services.llm_service import LLMService
from app.config import settings

logger = logging.getLogger(__name__)

# Minimum image dimensions to consider (skip tiny icons/spacers)
MIN_IMAGE_WIDTH = 80
MIN_IMAGE_HEIGHT = 80

# Directory where extracted images are saved for serving
IMAGES_DIR = os.path.join(settings.chroma_persist_dir, "..", "images")


class DocumentProcessor:
    """Handles document parsing, chunking, and preparation for embedding.
    Extracts images from PDFs and HTML, describes them via vision model,
    and bakes descriptions into the text for richer RAG context.
    Images are also saved to disk so they can be served in chat responses."""

    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size or settings.chunk_size,
            chunk_overlap=chunk_overlap or settings.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        self.llm = LLMService(model=settings.llm_model)

    def process_file(self, file_path: str, title: str, tenant: str) -> list[dict]:
        """Process a file and return a list of chunk dicts ready for ChromaDB."""

        self._current_tenant = tenant
        ext = os.path.splitext(file_path)[1].lower()
        logger.info("Processing file: type=%s title=%r path=%s", ext, title, file_path)

        if ext == ".pdf":
            text = self._extract_pdf(file_path)
        elif ext in (".html", ".htm"):
            text = self._extract_html(file_path)
        elif ext in (".md", ".txt"):
            text = self._extract_text(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

        logger.info("Extracted %d chars of text from %s", len(text), os.path.basename(file_path))
        if len(text.strip()) < 10:
            logger.warning("Very little text extracted from %s — check file content", file_path)

        chunks = self.splitter.split_text(text)
        filename = os.path.basename(file_path)
        logger.info("Split into %d chunks (chunk_size=%d, overlap=%d)",
                     len(chunks), self.splitter._chunk_size, self.splitter._chunk_overlap)

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

    def _save_image(self, image_bytes: bytes, tenant: str, ext: str = "png") -> str:
        """Save image to disk and return the filename."""
        tenant_dir = os.path.join(IMAGES_DIR, tenant)
        os.makedirs(tenant_dir, exist_ok=True)

        filename = f"img_{uuid.uuid4().hex[:12]}.{ext}"
        filepath = os.path.join(tenant_dir, filename)

        with open(filepath, "wb") as f:
            f.write(image_bytes)

        return filename

    def _extract_pdf(self, file_path: str) -> str:
        """Extract text and image descriptions from a PDF using PyMuPDF."""
        import fitz  # PyMuPDF

        doc = fitz.open(file_path)
        full_text = ""
        # Determine tenant from the file path context (passed via process_file)
        tenant = getattr(self, "_current_tenant", "default")

        for page_num, page in enumerate(doc):
            # Extract page text
            page_text = page.get_text() or ""

            # Extract images from this page
            image_entries = []
            image_list = page.get_images(full=True)

            for img_info in image_list:
                try:
                    xref = img_info[0]
                    base_image = doc.extract_image(xref)
                    if not base_image:
                        continue

                    image_bytes = base_image["image"]
                    width = base_image.get("width", 0)
                    height = base_image.get("height", 0)
                    img_ext = base_image.get("ext", "png")

                    # Skip tiny images (icons, spacers, decorative elements)
                    if width < MIN_IMAGE_WIDTH or height < MIN_IMAGE_HEIGHT:
                        continue

                    # Save image to disk
                    img_filename = self._save_image(image_bytes, tenant, img_ext)

                    # Get a snippet of surrounding text for context
                    context_snippet = page_text[:200] if page_text else ""

                    description = self.llm.describe_image(image_bytes, context_snippet)
                    image_entries.append((img_filename, description))

                except Exception as e:
                    logger.warning("Failed to extract PDF image xref=%s: %s", img_info[0], e)
                    continue

            # Build the page content with image descriptions baked in
            full_text += page_text.strip()

            if image_entries:
                full_text += "\n\n"
                for img_filename, desc in image_entries:
                    full_text += f"[Screenshot: {img_filename} | {desc}]\n\n"

            full_text += "\n\n"

        doc.close()
        return full_text.strip()

    def _extract_html(self, file_path: str) -> str:
        """Extract text and image descriptions from HTML."""
        from bs4 import BeautifulSoup

        with open(file_path, "r", encoding="utf-8") as f:
            html = f.read()

        logger.debug("HTML file size: %d bytes", len(html))
        soup = BeautifulSoup(html, "html.parser")
        doc_dir = os.path.dirname(os.path.abspath(file_path))

        # Process <img> tags — describe each and replace with text marker
        img_tags = soup.find_all("img")
        logger.info("Found %d images in HTML", len(img_tags))
        described = 0
        for img_tag in img_tags:
            description = self._describe_html_image(img_tag, doc_dir)
            if description:
                marker = soup.new_string(f"\n\n[Screenshot: {description}]\n\n")
                img_tag.replace_with(marker)
                described += 1
            else:
                img_tag.decompose()
        logger.info("Described %d/%d images", described, len(img_tags))

        # Extract clean text from the modified HTML
        text = soup.get_text(separator="\n")
        # Collapse excessive whitespace but keep paragraph breaks
        text = re.sub(r"\n{3,}", "\n\n", text)
        text = re.sub(r"[ \t]+", " ", text)
        return text.strip()

    def _describe_html_image(self, img_tag, doc_dir: str) -> str | None:
        """Extract image bytes from an HTML <img> tag, save to disk, and describe it."""
        src = img_tag.get("src", "")
        if not src:
            return None

        image_bytes = None
        img_ext = "png"

        # Case 1: Base64 data URI
        if src.startswith("data:image"):
            try:
                header, b64_data = src.split(",", 1)
                image_bytes = base64.b64decode(b64_data)
                # Extract extension from data URI (e.g. data:image/jpeg;base64)
                if "jpeg" in header or "jpg" in header:
                    img_ext = "jpg"
                elif "gif" in header:
                    img_ext = "gif"
            except Exception:
                return None

        # Case 2: Local file path (relative to the HTML document)
        elif not src.startswith(("http://", "https://")):
            img_path = os.path.join(doc_dir, src)
            if os.path.exists(img_path):
                try:
                    with open(img_path, "rb") as f:
                        image_bytes = f.read()
                    img_ext = os.path.splitext(src)[1].lstrip(".") or "png"
                except Exception:
                    return None

        if not image_bytes:
            # Fall back to alt text if we can't load the image
            alt = img_tag.get("alt", "")
            return f"Image: {alt}" if alt else None

        # Check image size (rough check via bytes — skip very small images)
        if len(image_bytes) < 2000:  # < 2KB likely a tiny icon
            alt = img_tag.get("alt", "")
            return f"Icon: {alt}" if alt else None

        tenant = getattr(self, "_current_tenant", "default")

        # Save image to disk
        img_filename = self._save_image(image_bytes, tenant, img_ext)

        # Get surrounding text for context
        context = ""
        prev_text = img_tag.find_previous(string=True)
        if prev_text:
            context = prev_text.strip()[:200]

        description = self.llm.describe_image(image_bytes, context)
        return f"{img_filename} | {description}"

    def _extract_text(self, file_path: str) -> str:
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read().strip()
