
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.services.retrieval_service import search_similar_chunks


router = APIRouter(
    prefix="/api/v1/retrieval",
    tags=["Retrieval"]
)


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    limit: int = Field(default=5, ge=1, le=20)


@router.post("/search")
def search_documents(request: SearchRequest):

    try:
        results = search_similar_chunks(
            query=request.query,
            limit=request.limit
        )

        return {
            "query": request.query,
            "total_results": len(results),
            "results": results
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=f"Search failed: {str(error)}"
        )
