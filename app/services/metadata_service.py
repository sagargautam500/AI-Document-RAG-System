from sqlalchemy.orm import Session

from app.models.document import Document


def save_document_metadata(
    db: Session,
    document_id: str,
    filename: str,
    file_type: str,
    chunking_strategy: str,
    total_chunks: int
) -> Document:
    """Save document metadata in PostgreSQL."""

    document = Document(
        document_id=document_id,
        filename=filename,
        file_type=file_type,
        chunking_strategy=chunking_strategy,
        total_chunks=total_chunks
    )

    db.add(document)
    db.commit()
    db.refresh(document)

    return document