# backend/search.py (Refactored to be a lightweight suggestion helper)
import re
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
import os
import logging

logger = logging.getLogger(__name__)

def search_query(query_str: str):
    """
    Performs a basic Whoosh index search.
    This is intended as a fallback or for simple local document retrieval.
    """
    results_list = []
    try:
        # Ensure the index directory exists relative to this file
        index_dir = os.path.join(os.path.dirname(__file__), "whoosh_index")
        if not os.path.exists(index_dir):
            logger.warning(f"Whoosh index directory not found at {index_dir}. Cannot perform fallback search.")
            return [], "Local index not available."

        ix = open_dir(index_dir)
        with ix.searcher() as searcher:
            parser = QueryParser("content", ix.schema)
            query = parser.parse(query_str)
            results = searcher.search(query)
            for hit in results:
                results_list.append(hit.fields())
        return results_list, "Search completed."
    except Exception as e:
        logger.error(f"Whoosh search error: {e}", exc_info=True)
        return [], "Error during local index search."

def get_suggestions(query):
    """Generate simple, pattern-based search suggestions without a heavy model."""
    if len(query) < 2:
        return []

    query_lower = query.lower().strip()
    suggestions = set()

    # Common question patterns
    patterns = [
        f"What is {query}?",
        f"How does {query} work?",
        f"Explain {query}",
        f"{query} applications",
        f"{query} examples"
    ]

    for pattern in patterns:
        if len(pattern) < 60:  # Keep suggestions a reasonable length
            suggestions.add(pattern)

    # Convert to list and limit
    suggestion_list = list(suggestions)[:5]

    return suggestion_list