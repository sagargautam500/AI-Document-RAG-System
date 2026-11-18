
from uuid import uuid4

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db

from app.services.qdrant_service import store_chunks
from app.services.metadata_service import save_document_metadata

from app.services.document_service import (
    extract_text_from_pdf,
    extract_text_from_txt
)

from app.services.chunking_service import (
    fixed_size_chunking,
    recursive_character_chunking
)

from app.services.embedding_service import generate_embeddings


router = APIRouter(
    prefix="/api/v1/documents",
    tags=["Documents"]
)


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    chunking_strategy: str = "fixed",
    chunk_size: int = 500,
    overlap: int = 50,
    db: Session = Depends(get_db)
):

    filename = file.filename or ""
    file_extension = filename.split(".")[-1].lower()

    if file_extension not in ["pdf", "txt"]:
        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are supported."
        )

    file_content = await file.read()

    if not file_content:
        raise HTTPException(
            status_code=400,
            detail="Uploaded file is empty."
        )

    # Extract document text
    try:
        if file_extension == "pdf":
            extracted_text = extract_text_from_pdf(file_content)
        else:
            extracted_text = extract_text_from_txt(file_content)

    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Unable to extract text from the uploaded file."
        )

    if not extracted_text:
        raise HTTPException(
            status_code=400,
            detail="No readable text found in the document."
        )

    # Chunk document text
    try:
        if chunking_strategy == "fixed":
            chunks = fixed_size_chunking(
                extracted_text,
                chunk_size,
                overlap
            )

        elif chunking_strategy == "recursive":
            chunks = recursive_character_chunking(
                extracted_text,
                chunk_size,
                overlap
            )

        else:
            raise HTTPException(
                status_code=400,
                detail="Invalid chunking strategy. Use fixed or recursive."
            )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    # Generate embeddings
    embeddings = generate_embeddings(chunks)

    embedding_dimension = (
        len(embeddings[0]) if embeddings else 0
    )

    # Generate unique document ID
    document_id = str(uuid4())

    # Store chunks and embeddings in Qdrant
    try:
        stored_count = store_chunks(
            document_id=document_id,
            filename=filename,
            chunks=chunks,
            embeddings=embeddings,
            chunking_strategy=chunking_strategy
        )

        # Store document metadata in PostgreSQL
        metadata = save_document_metadata(
            db=db,
            document_id=document_id,
            filename=filename,
            file_type=file_extension,
            chunking_strategy=chunking_strategy,
            total_chunks=len(chunks)
        )

    except Exception as error:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=f"Document storage failed: {str(error)}"
        )

    return {
        "document_id": document_id,
        "filename": filename,
        "file_type": file_extension,
        "chunking_strategy": chunking_strategy,
        "total_characters": len(extracted_text),
        "total_chunks": len(chunks),

        "vector_database": "Qdrant",
        "collection_name": "documents",
        "stored_vectors": stored_count,

        "metadata_database": "PostgreSQL",
        "metadata": {
            "document_id": metadata.document_id,
            "filename": metadata.filename,
            "file_type": metadata.file_type,
            "chunking_strategy": metadata.chunking_strategy,
            "total_chunks": metadata.total_chunks,
            "created_at": metadata.created_at.isoformat()
        },

        "embedding_model": "all-MiniLM-L6-v2",
        "embedding_dimension": embedding_dimension,

        "chunks": [
            {
                "chunk_id": index,
                "text": chunk,
                "character_count": len(chunk),
                "embedding_preview": embeddings[index][:5]
            }
            for index, chunk in enumerate(chunks)
        ]
    }
