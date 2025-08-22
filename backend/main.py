from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from search import search_query, get_suggestions
import os
from datetime import datetime

app = FastAPI()

# It's a good practice to manage allowed origins via environment variables.
# When you deploy your frontend, you'll set its public URL here.
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
CLOUDFLARE_URL = "https://prai-search.vercel.app"
allowed_origins_str = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173")

# Split the string into a list of actual origins.
allowed_origins = [origin.strip() for origin in allowed_origins_str.split(',')]


app.add_middleware(
    CORSMiddleware,
    # Add your deployed frontend URL to the list of allowed origins.
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    query: str

class Feedback(BaseModel):
    feedback: str

@app.get("/")
def read_root():
    return {"message": "SafeQuery: Privacy-First AI Search. Access the web app at http://localhost:3000 or use POST /search for queries."}

@app.post("/search")
async def search(query: Query):
    results, answer, privacy_log = search_query(query.query)
    return {"results": results, "answer": answer, "privacy_log": privacy_log}

@app.get("/suggest")
async def suggest(query: str):
    suggestions = get_suggestions(query)
    return {"suggestions": suggestions}

@app.post("/feedback")
async def receive_feedback(feedback: Feedback):
    feedback_text = feedback.feedback.strip()
    if not feedback_text:
        raise HTTPException(status_code=400, detail="Feedback cannot be empty.")

    # Store feedback in a simple text file with a timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] Feedback received:\n{feedback_text}\n{'-'*20}\n\n"

    try:
        with open("feedback_log.txt", "a", encoding="utf-8") as f:
            f.write(log_entry)
        return {"message": "Feedback received successfully."}
    except Exception as e:
        print(f"Error writing feedback: {e}")
        raise HTTPException(status_code=500, detail="Could not store feedback.")