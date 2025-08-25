# backend/smart_crawler.py - Contains the SmartCrawler logic
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, unquote
import logging
import time
import random
from typing import List, Dict, Set
import hashlib
import re
from duckduckgo_search import DDGS # Import the library

# Import the RAG system to interact with the knowledge base
# Assuming the RAG system class is named PrivacyRAGSystem in mistral_rag.py
from mistral_rag import PrivacyRAGSystem

logger = logging.getLogger(__name__) # Use getLogger for consistency

class SmartCrawler:
    def __init__(self,
                 rag_system: PrivacyRAGSystem, # Dependency injection for RAG system
                 crawl_topics: List[str] = None,
                 blocked_domains: List[str] = None):

        self.rag_system = rag_system
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        # Make topics and blocked domains configurable with sensible defaults
        self.crawl_topics = crawl_topics or ["latest advancements in AI", "python programming best practices", "climate change solutions"]
        self.blocked_domains = blocked_domains or [
            'facebook.com', 'twitter.com', 'instagram.com',
            'youtube.com', 'linkedin.com', 'reddit.com',
            'pinterest.com', 'tiktok.com'
        ]

        # Privacy: Use rotating user agents and delays
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
        ]
        self.crawled_urls = set() # To avoid re-crawling the same URL in a session

    def anonymize_query(self, query: str) -> str:
        """Hash the query for privacy logging"""
        return hashlib.sha256(query.encode()).hexdigest()[:16]

    def get_search_urls(self, query: str, num_results: int = 5) -> List[str]:
        """Get search results from DuckDuckGo (privacy-focused search) using DDGS library."""
        logger.info(f"Searching for URLs related to: '{query}'")
        try:
            with DDGS() as ddgs:
                # Fetch a few more results than needed to account for filtering
                results = [r['href'] for r in ddgs.text(query, max_results=num_results * 2)]
            
            # Filter for valid, non-blocked URLs
            valid_urls = [url for url in results if self.is_valid_url(url)]
            urls = list(dict.fromkeys(valid_urls)) # Remove duplicates
            
            logger.info(f"Found {len(urls)} URLs via DDGS for query: '{query}'")
            return urls[:num_results]

        except Exception as e:
            logger.error(f"Error getting search URLs: {e}")
            return []

    def is_valid_url(self, url: str) -> bool:
        """Validate URL and check if it's crawlable"""
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False

            domain = parsed.netloc.lower()
            return not any(blocked in domain for blocked in self.blocked_domains)

        except Exception as e: # Catch specific exceptions if possible, e.g., ValueError for urlparse
            logger.warning(f"Invalid URL or parsing error for {url}: {e}")
            return False

    def extract_content(self, url: str) -> Dict[str, str]:
        """Extract content from URL with privacy protection"""
        if url in self.crawled_urls:
            logger.info(f"Skipping already crawled URL: {url}")
            return None

        try:
            # Add random delay for privacy (avoid detection)
            time.sleep(random.uniform(1, 3))

            # Rotate user agent
            self.session.headers['User-Agent'] = random.choice(self.user_agents)

            response = self.session.get(url, timeout=15, allow_redirects=True)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove unwanted elements
            for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement']):
                tag.decompose()

            # Extract title
            title_tag = soup.find('title')
            title = title_tag.get_text().strip() if title_tag else "Unknown Title"

            # Extract main content
            content_selectors = [
                'article', 'main', '.content', '.post-content',
                '.entry-content', '.article-content', 'section', 'p' # Added 'p' for more general content
            ]

            content = ""
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    content = ' '.join([elem.get_text().strip() for elem in elements])
                    if content: # Break if content is found
                        break

            # Fallback: extract from body
            if not content:
                body = soup.find('body')
                if body:
                    content = body.get_text(separator=' ', strip=True) # Get all text from body

            # Clean content
            content = ' '.join(content.split())  # Remove extra whitespace

            # Validate content quality
            if len(content) < 100:
                logger.warning(f"Low quality content from {url}")
                return None

            self.crawled_urls.add(url) # Mark as crawled
            return {
                'title': title[:200],  # Limit title length
                'content': content[:4000],  # Limit content length (increased for better context)
                'url': url,
                'domain': urlparse(url).netloc
            }

        except requests.exceptions.RequestException as req_e:
            logger.error(f"Network error extracting {url}: {req_e}")
            return None
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {e}")
            return None

    def crawl_for_query(self, query: str, max_articles: int = 3) -> List[Dict[str, str]]:
        """Crawl web for query with privacy protection"""
        logger.info(f"Starting privacy-first crawl for: {self.anonymize_query(query)}")

        # Get search URLs
        urls = self.get_search_urls(query, num_results=max_articles * 2) # Fetch more URLs than needed

        articles = []
        for url in urls:
            if len(articles) >= max_articles:
                break

            article = self.extract_content(url)
            if article:
                # Privacy: Remove personal information patterns
                article = self.sanitize_content(article)
                articles.append(article)

        logger.info(f"Successfully crawled {len(articles)} articles for query: {self.anonymize_query(query)}")
        return articles

    def sanitize_content(self, article: Dict[str, str]) -> Dict[str, str]:
        """Remove potentially sensitive information"""
        # This method is called from crawl_for_query, so re-importing re here is fine.
        # However, it's better to import it once at the top of the file.
        # import re # Already imported at the top

        # Remove email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        article['content'] = re.sub(email_pattern, '[EMAIL]', article['content'])

        # Remove phone numbers
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        article['content'] = re.sub(phone_pattern, '[PHONE]', article['content'])

        # Remove excessive personal references
        # This pattern is very aggressive and might remove useful context.
        # Consider if this level of sanitization is truly necessary or if it degrades content quality too much.
        article['content'] = re.sub(r'\b(my|I am|I was|personally)\b', '', article['content'], flags=re.IGNORECASE)

        return article

    def run(self):
        """
        The main entry point for the crawler, to be called by the scheduler.
        This method defines topics, crawls them, and stores the results.
        """
        logger.info("🚀 Starting scheduled crawl to populate knowledge base...")
        
        # Define a list of diverse topics to keep the knowledge base fresh
        # These topics are now configurable via __init__
        
        for topic in self.crawl_topics:
            articles = self.crawl_for_query(topic, max_articles=2)
            if articles:
                self.rag_system.store_documents(articles)
        
        logger.info("✅ Scheduled crawl finished.")