# backend/mistral_rag.py - Contains the PrivacyRAGSystem (RAG logic)
import ollama
import chromadb
import os
import hashlib
import logging
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
import re # For cleaning LLM output

logger = logging.getLogger(__name__)

class PrivacyRAGSystem: # Renamed from MistralRAG for clarity
    def __init__(self):
        # Make the Ollama host configurable via an environment variable
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.client = ollama.Client(host=ollama_host)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        # Use os.path.join for cross-platform compatibility and relative path
        db_path = os.path.join(os.path.dirname(__file__), "chroma_db")
        self.chroma_client = chromadb.PersistentClient(path=db_path)
        self.collection = self.chroma_client.get_or_create_collection(name="documents")
        logger.info("ChromaDB and Embedding Model initialized.")

    def store_documents(self, documents: List[Dict[str, str]]):
        """Stores processed documents into ChromaDB."""
        if not documents:
            logger.warning("No documents provided to store.")
            return

        ids = []
        metadatas = []
        documents_content = []

        for doc in documents:
            # Use URL as ID or hash content if URL is missing
            doc_id = doc.get('url', hashlib.sha256(doc['content'].encode()).hexdigest())
            
            # Check if document already exists to prevent duplicates
            if self.collection.get(ids=[doc_id])['ids']:
                logger.info(f"Document with ID {doc_id} already exists, skipping.")
                continue

            ids.append(doc_id)
            metadatas.append({
                "title": doc.get('title', 'No Title'),
                "url": doc.get('url', 'No URL'),
                "domain": doc.get('domain', 'No Domain')
            })
            documents_content.append(doc['content'])

        if not ids:
            logger.info("All provided documents already exist in the collection.")
            return

        embeddings = self.embedding_model.encode(documents_content).tolist()

        self.collection.add(
            embeddings=embeddings,
            documents=documents_content,
            metadatas=metadatas,
            ids=ids
        )
        logger.info(f"Stored {len(ids)} new documents in ChromaDB.")

    def search_documents(self, query: str, max_results: int = 5) -> List[Dict[str, str]]:
        """Searches ChromaDB for relevant documents based on query."""
        if self.collection.count() == 0:
            logger.warning("ChromaDB collection is empty, no documents to search.")
            return []

        query_embedding = self.embedding_model.encode(query).tolist()
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=max_results,
            include=['documents', 'metadatas', 'distances'] # Include distances to calculate score
        )

        found_documents = []
        if results and results['documents']:
            for i in range(len(results['documents'][0])):
                doc_content = results['documents'][0][i]
                metadata = results['metadatas'][0][i]
                distance = results['distances'][0][i]
                score = 1 - distance # Convert distance to a similarity score (0 to 1)
                found_documents.append({
                    "title": metadata.get('title', 'No Title'),
                    "content": doc_content,
                    "url": metadata.get('url', 'No URL'),
                    "domain": metadata.get('domain', 'No Domain'),
                    "score": score,
                    "source": "local_chroma_db"
                })
        logger.info(f"Found {len(found_documents)} relevant documents in ChromaDB for query.")
        return found_documents

    def generate_answer(self, query: str, documents: List[Dict[str, str]]) -> str:
        """Generates an answer using Ollama based on query and retrieved documents."""
        context = "\n".join([doc['content'] for doc in documents])
        if not context:
            logger.warning("No context provided for answer generation.")
            return "I couldn't find enough relevant information in the knowledge base to answer your question."

        prompt = f"Using the following context, answer the question concisely and accurately. If the answer is not in the context, state that you don't know.\n\nContext:\n{context}\n\nQuestion: {query}\nAnswer:"

        try:
            response = self.client.chat(
                model=os.getenv("OLLAMA_MODEL", "gemma:2b"), # Use gemma:2b as default for lower RAM
                messages=[{'role': 'user', 'content': prompt}],
                stream=False
            )
            answer = response['message']['content'].strip()
            # Clean up common LLM artifacts
            answer = re.sub(r"Based on the context, ", "", answer, flags=re.IGNORECASE)
            answer = re.sub(r"Based on the provided context, ", "", answer, flags=re.IGNORECASE)
            answer = re.sub(r"Based on the information provided, ", "", answer, flags=re.IGNORECASE)
            answer = re.sub(r"I don't have enough information to answer that question based on the provided context.", "I don't have enough information in my knowledge base to answer that question.", answer)
            return answer
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            return "I apologize, but I encountered an error trying to generate an answer. Please try again."

    def get_knowledge_base_stats(self) -> Dict[str, Any]:
        """Returns statistics about the ChromaDB knowledge base."""
        stats = {
            "total_documents": self.collection.count(),
            "storage_type": "local_chroma_db"
        }
        logger.info(f"Knowledge base stats: {stats}")
        return stats

    def search_and_answer(self, query: str, max_web_results: int = 3) -> (list, str, dict):
        """
        A single method to perform the entire RAG process: search, generate, and return stats.
        """
        logger.info(f"Performing RAG search for query: '{query}'")

        # 1. Search for relevant documents in the knowledge base
        documents = self.search_documents(query, max_results=max_web_results) # Use the passed parameter

        # 2. Generate an answer using the retrieved documents
        answer = self.generate_answer(query, documents)

        # 3. Compile statistics about the operation
        stats = self.get_knowledge_base_stats()
        stats["documents_found_for_query"] = len(documents)
        stats["answer_length"] = len(answer)
        logger.info(f"RAG search completed for '{query}'. Docs found: {len(documents)}, Answer length: {len(answer)}")
        return documents, answer, stats