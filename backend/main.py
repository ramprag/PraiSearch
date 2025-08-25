# backend/main.py - Integrated with privacy-first RAG
from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
import os
from datetime import datetime
import logging
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
import hashlib

from mistral_rag import PrivacyRAGSystem # Direct import for clarity
from smart_crawler import SmartCrawler
from apscheduler.schedulers.background import BackgroundScheduler
from privacy_log import log_query
from search import get_suggestions, search_query as fallback_search # Import fallback search

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Startup: Initialize resources ---
    logger.info("Initializing application resources...")
    rag_system = PrivacyRAGSystem()
    app.state.rag_system = rag_system
    app.state.crawler = SmartCrawler(rag_system=rag_system) # Pass the RAG system to the crawler
    app.state.scheduler = BackgroundScheduler()

    # --- Synchronous Initial Crawl ---
    logger.info("Performing initial synchronous crawl to ensure data is available...")
    app.state.crawler.run()
    logger.info("Initial crawl complete. Knowledge base is ready.")

    # --- Post-Crawl Verification ---
    post_crawl_stats = rag_system.get_knowledge_base_stats()
    if post_crawl_stats.get("total_documents", 0) == 0:
        logger.warning("CRITICAL: Initial crawl finished, but the knowledge base is still empty. The crawler may be unable to find or process articles.")
    # --- End Verification ---

    # --- Schedule Subsequent Crawls ---
    app.state.scheduler.add_job(app.state.crawler.run, 'interval', hours=4, id="periodic_crawl")
    app.state.scheduler.start()
    logger.info("📰 Smart Crawler scheduled to run every 4 hours.")

    yield  # Application is running

    # --- Shutdown: Clean up resources ---
    logger.info("Shutting down application resources...")
    app.state.scheduler.shutdown()

app = FastAPI(title="SafeQuery: Privacy-First RAG Search", version="2.0", lifespan=lifespan)

# CORS configuration
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
async def search(query: Query, request: Request, background_tasks: BackgroundTasks):
    """Main search endpoint with privacy-first RAG"""
    try:
        # Input validation
        if not query.query or len(query.query.strip()) < 2:
            raise HTTPException(status_code=400, detail="Query must be at least 2 characters long")

        query_text = query.query.strip()

        # Log query anonymously
        background_tasks.add_task(log_query, query_text)

        logger.info(f"Processing search query (length: {len(query_text)})")

        try:
            # Use the RAG system from the application state for consistency
            results, answer, stats = request.app.state.rag_system.search_and_answer(query_text, max_web_results=3)

            # Format results for frontend
            formatted_results = []
            for result in results:
                formatted_results.append({
                    'title': result.get('title', 'Unknown Title'),
                    'content': result.get('content', '')[:500] + '...' if len(result.get('content', '')) > 500 else result.get('content', ''),
                    'url': result.get('url', ''),
                    'score': result.get('score', 0.0), # Now correctly gets the score
                    'source': result.get('source', 'unknown') # Now correctly gets the source
                })

            # Privacy log message
            privacy_log = f"Query processed with privacy protection. Found {stats['documents_found_for_query']} relevant results from {stats['storage_type']} storage. Total documents in knowledge base: {stats['total_documents']}"

            response = {
                "results": formatted_results,
                "answer": answer,
                "privacy_log": privacy_log,
                "stats": {
                    "total_results": len(formatted_results),
                    "knowledge_base_size": stats.get('total_documents', 0),
                    "storage_type": stats['storage_type']
                }
            }

            logger.info(f"Search completed: {len(formatted_results)} results, answer length: {len(answer)}")
            return response

        except Exception as rag_error:
            logger.error(f"RAG search error: {rag_error}")
            import traceback
            traceback.print_exc() # Print full traceback for debugging

            # Fallback to basic Whoosh index search
            logger.warning("RAG system failed. Attempting fallback to local Whoosh index.")
            fallback_results, fallback_status = fallback_search(query_text)
            
            # Format fallback results to match the expected structure
            formatted_fallback = [{'title': r.get('title', ''), 'content': r.get('content', ''), 'url': r.get('url', '')} for r in fallback_results]

            return {
                "results": formatted_fallback,
                "answer": f"Could not generate an AI answer. The following is from a local index search: {fallback_status}",
                "privacy_log": "Query processed with local index search due to RAG system failure. [Fallback mode]",
                "stats": {"mode": "fallback"}
            }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Search endpoint error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error during search")

@app.get("/suggest")
async def suggest(query: str, request: Request):
    """Get search suggestions"""
    try:
        if not query or len(query.strip()) < 1:
            return {"suggestions": []}

        suggestions = []

        # Basic question patterns
        base_suggestions = [
            f"What is {query}?",
            f"How does {query} work?",
            f"{query} applications",
            f"Explain {query}"
        ]

        # Try to get suggestions from knowledge base
        try:
            existing_docs = request.app.state.rag_system.search_documents(query, max_results=3)

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
async def get_stats(request: Request):
    """Get knowledge base statistics"""
    try:
        stats = request.app.state.rag_system.get_knowledge_base_stats()

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
async def health_check(request: Request):
    """Health check endpoint"""
    try:
        # Test RAG system
        stats = request.app.state.rag_system.get_knowledge_base_stats()

        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "knowledge_base_size": stats.get('total_documents', 0), # Correctly uses total_documents
            "storage_type": stats.get('storage_type', 'unknown') # Correctly uses storage_type
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