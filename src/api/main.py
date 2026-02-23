import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from dotenv import load_dotenv

# Import our modules
from src.db import get_db
from src.ingestion.embedding_manager import EmbeddingManager
from src.rag.engine import RAGEngine

load_dotenv()

# FastAPI app
app = FastAPI(title="Nonprofit AI Chatbot API", version="1.0.0")

# CORS middleware - be more permissive for static files
allowed_origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000').split(',')
allowed_origins = [origin.strip() for origin in allowed_origins]  # Clean whitespace
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for widget
widget_path = Path(__file__).resolve().parents[2] / "widget"
if widget_path.exists():
    app.mount("/static", StaticFiles(directory=str(widget_path)), name="static")

# Request/Response models
class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    answer: str
    sources: list
    confidence: float
    query: str

def _get_state_clients():
    db = getattr(app.state, "db", None)
    embedding_manager = getattr(app.state, "embedding_manager", None)
    rag_engine = getattr(app.state, "rag_engine", None)
    return db, embedding_manager, rag_engine

@app.get("/")
def root():
    """Root endpoint"""
    return {"status": "online", "service": "nonprofit-chatbot-api", "endpoints": ["/health", "/chat", "/widget.js"]}

@app.get("/health")
def health_check():
    """Health check endpoint for Vercel"""
    return {"status": "healthy", "service": "nonprofit-chatbot-api"}

@app.get("/widget.js")
def widget_script():
    """Serve the WordPress widget JavaScript"""
    widget_path = Path(__file__).resolve().parents[2] / "widget" / "widget.js"
    if not widget_path.exists():
        raise HTTPException(status_code=404, detail="Widget not found")
    response = FileResponse(widget_path, media_type="application/javascript; charset=utf-8")
    response.headers["Cache-Control"] = "public, max-age=3600"
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    """Main chat endpoint - RAG-powered query answering"""
    try:
        db, embedding_manager, rag_engine = _get_state_clients()
        if db is None or embedding_manager is None or rag_engine is None:
            raise HTTPException(status_code=503, detail="Service not initialized")

        query = request.query.strip()
        
        if not query or len(query) < 2:
            raise HTTPException(status_code=400, detail="Query too short")
        
        # Generate embedding for query
        query_embedding = embedding_manager.embed_text(query)
        
        # Retrieve relevant context
        context_chunks = rag_engine.retrieve_context(query_embedding)
        
        # Generate grounded answer
        answer, sources, confidence = rag_engine.generate_answer(query, context_chunks)
        
        # Format sources for response
        formatted_sources = [
            {
                "source": c['source'],
                "similarity": round(c['similarity'], 3),
                "excerpt": c['content'][:200] + "..."
            }
            for c in sources
        ]
        
        return ChatResponse(
            answer=answer,
            sources=formatted_sources,
            confidence=round(confidence, 3),
            query=query
        )
    
    except Exception as e:
        print(f"✗ Chat error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/ingest")
def ingest_documents():
    """Admin endpoint to ingest and index documents"""
    try:
        from src.ingestion.content_ingester import ContentIngester

        db, embedding_manager, _ = _get_state_clients()
        if db is None or embedding_manager is None:
            raise HTTPException(status_code=503, detail="Service not initialized")
        
        # Clear existing documents
        db.clear_documents()
        
        # Crawl WordPress and parse PDFs
        print("Ingesting content...")
        pages = ContentIngester.crawl_wordpress_pages()
        pdfs = ContentIngester.parse_pdf_files()
        all_docs = pages + pdfs
        
        # Chunk content
        chunks = ContentIngester.chunk_content(all_docs)
        
        # Generate embeddings
        embedded_chunks = embedding_manager.embed_chunks(chunks)
        
        # Store in vector DB
        for chunk in embedded_chunks:
            db.insert_document(
                content=chunk['text'],
                embedding=chunk['embedding'],
                source=chunk['source'],
                page_number=chunk.get('page_number'),
                metadata=chunk.get('metadata')
            )
        
        return {
            "status": "success",
            "documents_processed": len(all_docs),
            "chunks_created": len(chunks),
            "chunks_embedded": len(embedded_chunks)
        }
    
    except Exception as e:
        print(f"✗ Ingestion error: {e}")
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@app.on_event("startup")
async def startup_event():
    print("✓ Chatbot API starting up...")
    app.state.db = get_db()
    app.state.embedding_manager = EmbeddingManager()
    app.state.rag_engine = RAGEngine(app.state.db)

@app.on_event("shutdown")
async def shutdown_event():
    db = getattr(app.state, "db", None)
    if db:
        db.close()
    print("✓ Chatbot API shutting down...")

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv('API_PORT', 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
