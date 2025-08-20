from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from search import search_query, get_suggestions

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Query(BaseModel):
    query: str

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