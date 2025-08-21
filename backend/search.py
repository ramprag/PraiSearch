# backend/search.py (Simplified version without web scraping)
from whoosh.index import open_dir
from whoosh.qparser import QueryParser
from transformers import pipeline, GPT2LMHeadModel, GPT2Tokenizer
import torch
import re
from privacy_log import log_query
import os

# Initialize the model and tokenizer
device = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {device}")

# Initialize GPT-2 with better configuration
try:
    tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
    model = GPT2LMHeadModel.from_pretrained("gpt2")
    tokenizer.pad_token = tokenizer.eos_token

    qa_pipeline = pipeline(
        "text-generation",
        model=model,
        tokenizer=tokenizer,
        device=0 if torch.cuda.is_available() else -1
    )
    print("GPT-2 model loaded successfully")
except Exception as e:
    print(f"Error loading model: {e}")
    qa_pipeline = None

def search_local_index(query):
    """Search the local Whoosh index"""
    try:
        if not os.path.exists("indexdir"):
            print("Index directory not found. Please run 'python index.py' first.")
            return []

        ix = open_dir("indexdir")
        with ix.searcher() as searcher:
            # Try multiple search approaches for better results
            search_results = []

            # 1. Try exact phrase search first
            from whoosh.qparser import MultifieldParser, OrGroup
            parser = MultifieldParser(["title", "content"], ix.schema, group=OrGroup)

            try:
                parsed_query = parser.parse(query)
                results = searcher.search(parsed_query, limit=10)

                for result in results:
                    search_results.append({
                        'title': result['title'],
                        'content': result['content'],
                        'url': result['url'],
                        'score': result.score
                    })
            except Exception as e:
                print(f"Parsed query failed: {e}")

            # 2. If no results, try keyword search
            if not search_results:
                from whoosh.qparser import QueryParser
                content_parser = QueryParser("content", ix.schema)
                try:
                    content_query = content_parser.parse(query)
                    results = searcher.search(content_query, limit=10)

                    for result in results:
                        search_results.append({
                            'title': result['title'],
                            'content': result['content'],
                            'url': result['url'],
                            'score': result.score
                        })
                except Exception as e:
                    print(f"Content query failed: {e}")

            # 3. If still no results, try individual word search
            if not search_results:
                query_words = query.lower().split()
                for word in query_words:
                    if len(word) > 2:  # Skip very short words
                        try:
                            word_query = content_parser.parse(word)
                            results = searcher.search(word_query, limit=5)

                            for result in results:
                                # Check if we already have this result
                                if not any(r['title'] == result['title'] for r in search_results):
                                    search_results.append({
                                        'title': result['title'],
                                        'content': result['content'],
                                        'url': result['url'],
                                        'score': result.score
                                    })
                        except Exception as e:
                            print(f"Word query failed for '{word}': {e}")

            # 4. Last resort: get all documents and search manually
            if not search_results:
                print("No Whoosh results found, trying manual search...")
                all_docs = list(searcher.documents())
                query_lower = query.lower()

                for doc in all_docs:
                    title = doc.get('title', '').lower()
                    content = doc.get('content', '').lower()

                    # Simple keyword matching
                    if (query_lower in title or query_lower in content or
                            any(word in title or word in content for word in query_lower.split() if len(word) > 2)):
                        search_results.append({
                            'title': doc.get('title', ''),
                            'content': doc.get('content', ''),
                            'url': doc.get('url', ''),
                            'score': 1.0
                        })

            print(f"Found {len(search_results)} local results for: {query}")
            return search_results

    except Exception as e:
        print(f"Local search error: {e}")
        import traceback
        traceback.print_exc()
        return []

def generate_answer(query, search_results):
    """Generate an answer using extractive approach for better accuracy"""

    if not search_results:
        return "I couldn't find any relevant information in the knowledge base. Please try a different query or add more content to the index."

    # For better accuracy, use extractive approach instead of generative
    best_answer = extract_best_answer(query, search_results)

    # Only try generative approach as fallback if extractive fails
    if len(best_answer.strip()) < 20:
        return generate_with_model(query, search_results)

    return best_answer

def extract_best_answer(query, search_results):
    """Extract the most relevant information directly from search results"""

    query_words = set(query.lower().split())
    # Remove common stop words
    stop_words = {'what', 'is', 'how', 'does', 'can', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'about'}
    query_keywords = query_words - stop_words

    best_sentences = []

    for result in search_results[:3]:  # Use top 3 results
        content = result['content']
        title = result['title']

        # Split content into sentences
        sentences = re.split(r'[.!?]+', content)

        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:  # Skip very short sentences
                continue

            sentence_words = set(sentence.lower().split())

            # Calculate relevance score
            keyword_matches = len(query_keywords.intersection(sentence_words))
            sentence_score = keyword_matches / max(len(query_keywords), 1)

            # Bonus for title matches
            title_words = set(title.lower().split())
            if query_keywords.intersection(title_words):
                sentence_score += 0.3

            # Prefer longer, more informative sentences
            if len(sentence) > 50:
                sentence_score += 0.1

            if sentence_score > 0.2:  # Minimum relevance threshold
                best_sentences.append((sentence, sentence_score, title))

    if not best_sentences:
        # Fallback: use the first substantial sentence from the best result
        best_result = search_results[0]
        sentences = re.split(r'[.!?]+', best_result['content'])
        for sentence in sentences:
            if len(sentence.strip()) > 30:
                return f"Based on the information about {best_result['title']}: {sentence.strip()}."
        return f"According to the search results: {best_result['content'][:200]}..."

    # Sort by score and get the best sentences
    best_sentences.sort(key=lambda x: x[1], reverse=True)

    # Combine the best sentences for a comprehensive answer
    answer_parts = []
    used_content = set()

    for sentence, score, title in best_sentences[:3]:  # Use up to 3 best sentences
        sentence_clean = sentence.strip()
        if sentence_clean not in used_content and len(sentence_clean) > 20:
            answer_parts.append(sentence_clean)
            used_content.add(sentence_clean)

    if answer_parts:
        answer = '. '.join(answer_parts)
        # Ensure it ends with proper punctuation
        if not answer.endswith(('.', '!', '?')):
            answer += '.'
        return answer

    return ""

def generate_with_model(query, search_results):
    """Use the language model as a fallback for answer generation"""

    if not qa_pipeline:
        return generate_fallback_answer(query, search_results)

    # Use only the most relevant content
    best_result = search_results[0]
    context = f"{best_result['title']}: {best_result['content'][:400]}"

    # Simpler, more direct prompt
    prompt = f"Based on this information: {context}\n\nQuestion: {query}\nGive a direct answer:"

    try:
        # More conservative generation parameters
        inputs = tokenizer.encode(prompt, return_tensors='pt', max_length=400, truncation=True)

        with torch.no_grad():
            outputs = model.generate(
                inputs,
                max_length=inputs.shape[1] + 60,  # Allow for 60 new tokens
                num_return_sequences=1,
                temperature=0.5,  # Lower temperature for more focused answers
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
                no_repeat_ngram_size=2,
                early_stopping=True,
                eos_token_id=tokenizer.encode('.')[0]  # Stop at period
            )

        generated_text = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Better extraction of answer
        if "Give a direct answer:" in generated_text:
            answer_part = generated_text.split("Give a direct answer:")[-1].strip()
        else:
            answer_part = generated_text[len(prompt):].strip()

        # Clean and format the answer
        answer = re.sub(r'\n+', ' ', answer_part)
        answer = re.sub(r'\s+', ' ', answer)

        # Ensure complete sentences
        sentences = re.split(r'[.!?]', answer)
        if len(sentences) > 1:
            # Take first complete sentence
            answer = sentences[0].strip() + '.'

        if len(answer.strip()) > 10:
            return answer
        else:
            return generate_fallback_answer(query, search_results)

    except Exception as e:
        print(f"Model generation error: {e}")
        return generate_fallback_answer(query, search_results)

def generate_fallback_answer(query, search_results):
    """Generate a comprehensive fallback answer when model generation fails"""
    if not search_results:
        return f"I couldn't find specific information about '{query}' in the local knowledge base. Please try rephrasing your question or adding more relevant content to the index."

    # Get the best result
    best_result = search_results[0]
    title = best_result['title']
    content = best_result['content']

    # Look for the most relevant paragraph or section
    query_words = set(query.lower().split())
    stop_words = {'what', 'is', 'how', 'does', 'can', 'the', 'a', 'an', 'and', 'or', 'but'}
    query_keywords = query_words - stop_words

    # Split content into sentences and find the best continuous section
    sentences = re.split(r'[.!?]+', content)
    best_section = []
    current_section = []
    max_score = 0
    current_score = 0

    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) < 15:
            continue

        sentence_words = set(sentence.lower().split())
        matches = len(query_keywords.intersection(sentence_words))
        sentence_score = matches / max(len(query_keywords), 1)

        current_section.append(sentence)
        current_score += sentence_score

        # If we have 2-3 sentences, evaluate this section
        if len(current_section) >= 2:
            avg_score = current_score / len(current_section)
            if avg_score > max_score:
                max_score = avg_score
                best_section = current_section.copy()

            # Slide the window
            if len(current_section) > 3:
                removed = current_section.pop(0)
                # Recalculate score for removed sentence
                removed_words = set(removed.lower().split())
                removed_matches = len(query_keywords.intersection(removed_words))
                removed_score = removed_matches / max(len(query_keywords), 1)
                current_score -= removed_score

    # Format the answer
    if best_section:
        answer = '. '.join(best_section)
        if not answer.endswith('.'):
            answer += '.'

        # Add context about the source
        if title.lower() not in answer.lower():
            answer = f"Regarding {title}: {answer}"

        return answer

    # Final fallback: use first substantial part of content
    if len(content) > 100:
        # Find a good stopping point
        truncated = content[:300]
        last_period = truncated.rfind('.')
        if last_period > 100:
            truncated = truncated[:last_period + 1]

        return f"According to the information on {title}: {truncated}"

    return f"Based on the available information: {content}"

def get_suggestions(query):
    """Generate search suggestions based on local index content and common patterns"""
    if len(query) < 2:
        return []

    try:
        suggestions = set()  # Use set to avoid duplicates

        # Add question-based suggestions
        query_lower = query.lower().strip()

        # Common question patterns
        patterns = [
            f"What is {query}?",
            f"How does {query} work?",
            f"Explain {query}",
            f"Define {query}",
            f"{query} applications",
            f"{query} benefits",
            f"{query} examples"
        ]

        # Add patterns that make sense
        for pattern in patterns:
            if len(pattern) < 50:  # Reasonable length
                suggestions.add(pattern)

        # Search for related terms in index
        try:
            local_results = search_local_index(query)

            for result in local_results[:2]:  # Top 2 results only
                title = result['title']

                # Add title-based suggestions
                if query_lower not in title.lower():
                    suggestions.add(f"What is {title}?")

                # Extract key terms from content
                content_words = result['content'].split()[:50]  # First 50 words
                for word in content_words:
                    word_clean = re.sub(r'[^\w]', '', word)
                    if (len(word_clean) > 4 and
                            word_clean.lower().startswith(query_lower[:3]) and
                            word_clean.lower() != query_lower):
                        suggestions.add(f"What is {word_clean}?")

        except Exception as e:
            print(f"Error generating suggestions from index: {e}")

        # Convert to list and limit
        suggestion_list = list(suggestions)[:6]

        # If no suggestions found, provide defaults
        if not suggestion_list:
            suggestion_list = [
                f"What is {query}?",
                f"Explain {query}",
                f"How does {query} work?"
            ]

        return suggestion_list

    except Exception as e:
        print(f"Suggestion error: {e}")
        return [f"What is {query}?", f"Explain {query}"]

def debug_index():
    """Debug function to check index contents"""
    try:
        if not os.path.exists("indexdir"):
            print("❌ Index directory 'indexdir' does not exist!")
            return False

        ix = open_dir("indexdir")
        with ix.searcher() as searcher:
            # Get total number of documents
            doc_count = searcher.doc_count()
            print(f"📊 Index contains {doc_count} documents")

            # List all documents
            docs = list(searcher.documents())
            print("📄 Documents in index:")
            for i, doc in enumerate(docs[:5]):  # Show first 5
                title = doc.get('title', 'No title')
                content_preview = doc.get('content', '')[:100] + "..."
                print(f"  {i+1}. {title}")
                print(f"     Content: {content_preview}")
                print()

            if len(docs) > 5:
                print(f"     ... and {len(docs) - 5} more documents")

            return len(docs) > 0

    except Exception as e:
        print(f"❌ Error checking index: {e}")
        import traceback
        traceback.print_exc()
        return False

def search_query(query):
    """Main search function"""
    try:
        # Log the query for privacy tracking
        log_query(query)

        print(f"🔍 Searching for: '{query}'")

        # Debug: Check index first
        if not debug_index():
            return [], "Index is empty or corrupted. Please run 'python index.py' to create the index.", "Error: Index not found."

        # Search local index
        results = search_local_index(query)
        print(f"📋 Search returned {len(results)} results")

        if results:
            for i, result in enumerate(results[:3]):
                print(f"  Result {i+1}: {result['title']} (Score: {result['score']:.2f})")

        # Generate answer based on search results
        answer = generate_answer(query, results)
        print(f"💡 Generated answer: {answer[:100]}...")

        # Privacy log message
        num_results = len(results)
        privacy_log = f"Query processed locally with privacy protection. Found {num_results} relevant documents in local index."

        return results, answer, privacy_log

    except Exception as e:
        print(f"❌ Search query error: {e}")
        import traceback
        traceback.print_exc()
        return [], f"An error occurred while processing your query: {str(e)}", "Error in query processing."