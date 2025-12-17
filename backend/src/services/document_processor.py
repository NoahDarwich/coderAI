"""
Document processing service for parsing PDF, DOCX, and TXT files.

This service extracts text content from uploaded documents using PyMuPDF (for PDFs)
and python-docx (for Word documents).
"""
import io
from typing import BinaryIO

import fitz  # PyMuPDF
from docx import Document as DocxDocument


class DocumentProcessingError(Exception):
    """Raised when document processing fails."""
    pass


def parse_pdf(file: BinaryIO) -> str:
    """
    Parse PDF file and extract text content.

    Uses PyMuPDF (fitz) for fast and accurate text extraction with layout preservation.

    Args:
        file: Binary file object (PDF)

    Returns:
        Extracted text content

    Raises:
        DocumentProcessingError: If PDF parsing fails
    """
    try:
        # Read file content
        file_content = file.read()

        # Open PDF document
        pdf_document = fitz.open(stream=file_content, filetype="pdf")

        # Extract text from all pages
        text_content = []
        for page_num in range(pdf_document.page_count):
            page = pdf_document[page_num]
            text = page.get_text()

            # Add page separator for multi-page documents
            if page_num > 0:
                text_content.append(f"\n\n--- Page {page_num + 1} ---\n\n")

            text_content.append(text)

        pdf_document.close()

        # Combine all pages
        full_text = "".join(text_content).strip()

        if not full_text:
            raise DocumentProcessingError("PDF contains no extractable text (may be scanned image)")

        return full_text

    except fitz.fitz.FileDataError as e:
        raise DocumentProcessingError(f"Invalid PDF file: {str(e)}")
    except Exception as e:
        raise DocumentProcessingError(f"Failed to parse PDF: {str(e)}")


def parse_docx(file: BinaryIO) -> str:
    """
    Parse DOCX file and extract text content.

    Uses python-docx to extract text from Word documents, preserving paragraph structure.

    Args:
        file: Binary file object (DOCX)

    Returns:
        Extracted text content

    Raises:
        DocumentProcessingError: If DOCX parsing fails
    """
    try:
        # Open DOCX document
        doc = DocxDocument(file)

        # Extract text from all paragraphs
        paragraphs = []
        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            if text:  # Skip empty paragraphs
                paragraphs.append(text)

        # Extract text from tables
        for table in doc.tables:
            for row in table.rows:
                row_text = " | ".join([cell.text.strip() for cell in row.cells])
                if row_text:
                    paragraphs.append(row_text)

        # Combine all paragraphs
        full_text = "\n\n".join(paragraphs).strip()

        if not full_text:
            raise DocumentProcessingError("DOCX contains no extractable text")

        return full_text

    except Exception as e:
        raise DocumentProcessingError(f"Failed to parse DOCX: {str(e)}")


def parse_txt(file: BinaryIO) -> str:
    """
    Parse plain text file.

    Args:
        file: Binary file object (TXT)

    Returns:
        Text content

    Raises:
        DocumentProcessingError: If TXT parsing fails
    """
    try:
        # Try UTF-8 first
        content = file.read()

        try:
            text = content.decode('utf-8')
        except UnicodeDecodeError:
            # Fallback to latin-1 if UTF-8 fails
            try:
                text = content.decode('latin-1')
            except UnicodeDecodeError:
                raise DocumentProcessingError("Unable to decode text file (unsupported encoding)")

        text = text.strip()

        if not text:
            raise DocumentProcessingError("Text file is empty")

        return text

    except DocumentProcessingError:
        raise
    except Exception as e:
        raise DocumentProcessingError(f"Failed to parse text file: {str(e)}")


def chunk_text(text: str, max_words: int = 5000) -> list[str]:
    """
    Split text into chunks for processing large documents.

    Args:
        text: Full document text
        max_words: Maximum words per chunk (default: 5000 words ~= 7000 tokens)

    Returns:
        List of text chunks
    """
    words = text.split()

    if len(words) <= max_words:
        return [text]

    chunks = []
    current_chunk = []
    current_count = 0

    for word in words:
        current_chunk.append(word)
        current_count += 1

        if current_count >= max_words:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_count = 0

    # Add remaining words
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def get_content_preview(text: str, max_length: int = 500) -> str:
    """
    Get preview of document content (first N characters).

    Args:
        text: Full document text
        max_length: Maximum preview length

    Returns:
        Preview text (truncated with "..." if needed)
    """
    if len(text) <= max_length:
        return text

    return text[:max_length] + "..."
