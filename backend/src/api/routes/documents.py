"""
API routes for document management (upload, list, delete).
"""
from typing import List
from uuid import UUID

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    UploadFile,
    status,
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_db
from src.models.document import ContentType, Document
from src.models.project import Project
from src.schemas.document import (
    Document as DocumentSchema,
    DocumentDetail,
    TextDocumentCreate,
)
from src.services.document_processor import (
    DocumentProcessingError,
    get_content_preview,
    parse_docx,
    parse_pdf,
    parse_txt,
)

router = APIRouter(tags=["documents"])


@router.post(
    "/api/v1/projects/{project_id}/documents",
    response_model=DocumentSchema,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    project_id: UUID,
    file: UploadFile = File(..., description="Document file (PDF, DOCX, or TXT)"),
    db: AsyncSession = Depends(get_db),
) -> DocumentSchema:
    """
    Upload and process a document.

    Args:
        project_id: Project UUID
        file: Uploaded file (multipart/form-data)
        db: Database session

    Returns:
        Created document

    Raises:
        HTTPException: 404 if project not found
        HTTPException: 400 if file type unsupported or processing fails
        HTTPException: 413 if file too large
    """
    # Verify project exists
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )

    # Validate file size (max 10MB)
    file_content = await file.read()
    file_size = len(file_content)

    if file_size > 10485760:  # 10MB
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File size exceeds 10MB limit",
        )

    if file_size == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File is empty",
        )

    # Determine content type from file extension
    filename = file.filename or "unknown"
    file_ext = filename.lower().split(".")[-1]

    if file_ext == "pdf":
        content_type = ContentType.PDF
        parser = parse_pdf
    elif file_ext in ["docx", "doc"]:
        content_type = ContentType.DOCX
        parser = parse_docx
    elif file_ext == "txt":
        content_type = ContentType.TXT
        parser = parse_txt
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type: {file_ext}. Supported: PDF, DOCX, TXT",
        )

    # Parse document and extract text
    try:
        # Create file-like object from bytes
        from io import BytesIO

        file_obj = BytesIO(file_content)
        extracted_text = parser(file_obj)
    except DocumentProcessingError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )

    # Create document record
    document = Document(
        project_id=project_id,
        name=filename,
        content=extracted_text,
        content_type=content_type,
        size_bytes=file_size,
    )

    db.add(document)
    await db.commit()
    await db.refresh(document)

    return DocumentSchema.model_validate(document)


@router.post(
    "/api/v1/projects/{project_id}/documents/text",
    response_model=DocumentSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_text_document(
    project_id: UUID,
    document_data: TextDocumentCreate,
    db: AsyncSession = Depends(get_db),
) -> DocumentSchema:
    """
    Create a document from raw text input (MVP feature).

    Args:
        project_id: Project UUID
        document_data: Text document data
        db: Database session

    Returns:
        Created document

    Raises:
        HTTPException: 404 if project not found
        HTTPException: 400 if text is empty or too large
    """
    # Verify project exists
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )

    # Validate text content
    text_content = document_data.content.strip()

    if not text_content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Text content cannot be empty",
        )

    # Calculate size in bytes
    content_bytes = text_content.encode('utf-8')
    size_bytes = len(content_bytes)

    if size_bytes > 10485760:  # 10MB
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Text content exceeds 10MB limit",
        )

    # Create document record
    document = Document(
        project_id=project_id,
        name=document_data.name,
        content=text_content,
        content_type=ContentType.TXT,
        size_bytes=size_bytes,
    )

    db.add(document)
    await db.commit()
    await db.refresh(document)

    return DocumentSchema.model_validate(document)


@router.get("/api/v1/projects/{project_id}/documents", response_model=List[DocumentSchema])
async def list_documents(
    project_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> List[DocumentSchema]:
    """
    List all documents for a project.

    Args:
        project_id: Project UUID
        db: Database session

    Returns:
        List of documents

    Raises:
        HTTPException: 404 if project not found
    """
    # Verify project exists
    result = await db.execute(select(Project).where(Project.id == project_id))
    project = result.scalar_one_or_none()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with id {project_id} not found",
        )

    # Get all documents for project
    result = await db.execute(
        select(Document)
        .where(Document.project_id == project_id)
        .order_by(Document.uploaded_at.desc())
    )
    documents = result.scalars().all()

    return [DocumentSchema.model_validate(doc) for doc in documents]


@router.get("/api/v1/documents/{document_id}", response_model=DocumentDetail)
async def get_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> DocumentDetail:
    """
    Get document details with content preview.

    Args:
        document_id: Document UUID
        db: Database session

    Returns:
        Document details with content preview

    Raises:
        HTTPException: 404 if document not found
    """
    # Get document
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with id {document_id} not found",
        )

    # Build response with preview
    document_dict = document.__dict__.copy()
    document_dict["content_preview"] = get_content_preview(document.content)

    return DocumentDetail.model_validate(document_dict)


@router.delete("/api/v1/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete a document and all related extractions (cascading delete).

    Args:
        document_id: Document UUID
        db: Database session

    Raises:
        HTTPException: 404 if document not found
    """
    # Get document
    result = await db.execute(
        select(Document).where(Document.id == document_id)
    )
    document = result.scalar_one_or_none()

    if not document:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Document with id {document_id} not found",
        )

    # Delete document (cascade deletes related records)
    await db.delete(document)
    await db.commit()
