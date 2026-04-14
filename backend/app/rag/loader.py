"""Document loaders for PDF, Markdown, and plain text files."""

from __future__ import annotations

from pathlib import Path

from langchain_core.documents import Document


async def load_document(file_path: str) -> list[Document]:
    """Load a document from disk and return LangChain Document objects.

    Supports PDF, Markdown (.md), and plain text (.txt) files.

    Args:
        file_path: Path to the document file.

    Returns:
        List of LangChain Document objects with page content and metadata.

    Raises:
        ValueError: If the file type is not supported.
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        return _load_pdf(path)
    elif suffix == ".md":
        return _load_text(path, file_type="markdown")
    elif suffix == ".txt":
        return _load_text(path, file_type="text")
    else:
        raise ValueError(f"Unsupported file type: {suffix}")


def _load_pdf(path: Path) -> list[Document]:
    """Load a PDF file using pypdf."""
    from pypdf import PdfReader

    reader = PdfReader(str(path))
    documents = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if text.strip():
            documents.append(
                Document(
                    page_content=text,
                    metadata={"source": path.name, "page": i + 1, "file_type": "pdf"},
                )
            )
    return documents


def _load_text(path: Path, file_type: str) -> list[Document]:
    """Load a text-based file."""
    content = path.read_text(encoding="utf-8")
    return [
        Document(
            page_content=content,
            metadata={"source": path.name, "file_type": file_type},
        )
    ]
