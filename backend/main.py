# backend/main.py - Integrated with privacy-first RAG
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from datetime import datetime
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="SafeQuery: Privacy-First RAG Search", version="2.0")

# CORS configuration
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173,https://prai-search.vercel.app")
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(',')]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class Query(BaseModel):
    query: str
    max_results: Optional[int] = 5

class Feedback(BaseModel):
    feedback: str

# Global RAG system (initialized lazily)
rag_system = None

def get_rag_system():
    """Get or initialize RAG system"""
    global rag_system
    if rag_system is None:
        from mistral_rag import PrivacyRAGSystem
        rag_system = PrivacyRAGSystem()
    return rag_system

@app.get("/")
def read_root():
    return {
        "message": "SafeQuery: Privacy-First RAG Search Engine",
        "version": "2.0",
        "description": "Dynamic web crawling with privacy protection",
        "endpoints": {
            "search": "POST /search - Main search with RAG",
            "suggest": "GET /suggest - Get search suggestions",
            "feedback": "POST /feedback - Submit user feedback",
            "stats": "GET /stats - Get knowledge base statistics"
        }
    }

@app.post("/search")
async def search(query: Query, background_tasks: BackgroundTasks):
    """Main search endpoint with privacy-first RAG"""
    try:
        # Input validation
        if not query.query or len(query.query.strip()) < 2:
            raise HTTPException(status_code=400, detail="Query must be at least 2 characters long")

        query_text = query.query.strip()

        # Log query anonymously
        from privacy_log import log_query
        background_tasks.add_task(log_query, query_text)

        logger.info(f"Processing search query (length: {len(query_text)})")

        # Use RAG system for search and answer generation
        from mistral_rag import search_and_answer

        try:
            results, answer, stats = search_and_answer(query_text, max_web_results=3)

            # Format results for frontend
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'title': result.get('title', 'Unknown Title'),
                    'content': result.get('content', '')[:500] + '...' if len(result.get('content', '')) > 500 else result.get('content', ''),
                    'url': result.get('url', ''),
                    'score': result.get('score', 0.0),
                    'source': result.get('metadata', {}).get('source', 'local')
                })

            # Privacy log message
            privacy_log = f"Query processed with privacy protection. Found {len(formatted_results)} results from {stats['storage_type']} storage. Total documents: {stats['total_documents']}"

            response = {
                "results": formatted_results,
                "answer": answer,
                "privacy_log": privacy_log,
                "stats": {
                    "total_results": len(formatted_results),
                    "knowledge_base_size": stats['total_documents'],
                    "storage_type": stats['storage_type']
                }
            }

            logger.info(f"Search completed: {len(formatted_results)} results, answer length: {len(answer)}")
            return response

        except Exception as rag_error:
            logger.error(f"RAG search error: {rag_error}")

            # Fallback to basic search
            from search import search_query
            results, answer, privacy_log = search_query(query_text)

            return {
                "results": results,
                "answer": answer + " (Note: Using fallback search due to system limitations)",
                "privacy_log": privacy_log + " [Fallback mode]",
                "stats": {"mode": "fallback"}
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during search")

@app.get("/suggest")
async def suggest(query: str):
    """Get search suggestions"""
    try:
        if not query or len(query.strip()) < 1:
            return {"suggestions": []}

        # Generate smart suggestions based on query
        suggestions = []

        # Basic question patterns
        base_suggestions = [
            f"What is {query}?",
            f"How does {query} work?",
            f"Explain {query}",
            f"{query} examples",
            f"{query} definition"
        ]

        # Try to get suggestions from knowledge base
        try:
            rag = get_rag_system()
            existing_docs = rag.search_documents(query, max_results=3)

            for doc in existing_docs:
                title = doc.get('title', '')
                if query.lower() not in title.lower() and len(title) > 0:
                    suggestions.append(f"What is {title}?")
        except:
            pass

        # Combine and limit suggestions
        all_suggestions = base_suggestions + suggestions
        unique_suggestions = list(dict.fromkeys(all_suggestions))  # Remove duplicates

        return {"suggestions": unique_suggestions[:6]}

    except Exception as e:
        logger.error(f"Suggestion error: {e}")
        return {"suggestions": [f"What is {query}?", f"Explain {query}"]}

@app.post("/feedback")
async def receive_feedback(feedback: Feedback):
    """Receive user feedback"""
    try:
        feedback_text = feedback.feedback.strip()
        if not feedback_text:
            raise HTTPException(status_code=400, detail="Feedback cannot be empty.")

        # Store feedback with privacy protection
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Anonymize feedback for privacy
        import hashlib
        feedback_hash = hashlib.sha256(feedback_text.encode()).hexdigest()[:16]

        log_entry = f"[{timestamp}] Feedback ID: {feedback_hash}\nLength: {len(feedback_text)} chars\n{'-'*20}\n\n"

        with open("feedback_log.txt", "a", encoding="utf-8") as f:
            f.write(log_entry)

        logger.info(f"Feedback received: ID {feedback_hash}")
        return {"message": "Feedback received successfully.", "feedback_id": feedback_hash}

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Feedback error: {e}")
        raise HTTPException(status_code=500, detail="Could not store feedback.")

@app.get("/stats")
async def get_stats():
    """Get knowledge base statistics"""
    try:
        rag = get_rag_system()
        stats = rag.get_knowledge_base_stats()

        return {
            "knowledge_base": stats,
            "privacy_features": [
                "Anonymous query logging",
                "Content sanitization",
                "User data anonymization",
                "Privacy-first web crawling",
                "Local data processing"
            ],
            "capabilities": [
                "Dynamic web content crawling",
                "Multi-document RAG search",
                "Real-time knowledge base updates",
                "Diverse topic handling"
            ]
        }

    except Exception as e:
        logger.error(f"Stats error: {e}")
        return {"error": "Could not retrieve statistics"}

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test RAG system
        rag = get_rag_system()
        stats = rag.get_knowledge_base_stats()

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "knowledge_base_size": stats.get('total_documents', 0),
            "storage_type": stats.get('storage_type', 'unknown')
        }
    except Exception as e:
        return {
            "status": "degraded",
            "timestamp": datetime.now().isoformat(),
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)