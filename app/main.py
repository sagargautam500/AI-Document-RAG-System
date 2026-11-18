
from fastapi import FastAPI
from app.api.documents import router as documents_router
from app.api.retrieval import router as retrieval_router
from app.api.chat import router as chat_router

app = FastAPI(
    title="AI Document RAG System",
    description="Document-based Conversational AI Backend",
    version="1.0.0"
)


@app.get("/")
def home():
    return {"message": "AI Document RAG API is running!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


app.include_router(documents_router)
app.include_router(retrieval_router)
app.include_router(chat_router)
