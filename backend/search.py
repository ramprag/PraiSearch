# backend/search.py (Refactored to be a lightweight suggestion helper)
import re

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