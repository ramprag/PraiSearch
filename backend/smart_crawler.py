# backend/smart_crawler.py - Fixed version with better error handling
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, unquote
import logging
import time
import random
from typing import List, Dict, Set
import hashlib
import re

logger = logging.getLogger(__name__)

class SmartCrawler:
    def __init__(self, rag_system, crawl_topics: List[str] = None, blocked_domains: List[str] = None):
        self.rag_system = rag_system
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

        self.crawl_topics = crawl_topics or [
            "artificial intelligence basics",
            "machine learning tutorial",
            "cloud computing guide"
        ]

        self.blocked_domains = blocked_domains or [
            'facebook.com', 'twitter.com', 'instagram.com',
            'youtube.com', 'linkedin.com', 'reddit.com'
        ]

        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        ]
        self.crawled_urls = set()

    def anonymize_query(self, query: str) -> str:
        """Hash the query for privacy logging"""
        return hashlib.sha256(query.encode()).hexdigest()[:16]

    def get_search_urls(self, query: str, num_results: int = 3) -> List[str]:
        """Get curated URLs based on query topic - no external search needed"""
        logger.info(f"Getting curated URLs for topic: '{query}'")

        # Curated high-quality URLs by topic
        url_mapping = {
            "artificial intelligence": [
                "https://en.wikipedia.org/wiki/Artificial_intelligence",
                "https://www.ibm.com/topics/artificial-intelligence",
                "https://builtin.com/artificial-intelligence"
            ],
            "machine learning": [
                "https://en.wikipedia.org/wiki/Machine_learning",
                "https://www.ibm.com/topics/machine-learning",
                "https://developers.google.com/machine-learning/guides"
            ],
            "cloud computing": [
                "https://en.wikipedia.org/wiki/Cloud_computing",
                "https://aws.amazon.com/what-is-cloud-computing/",
                "https://azure.microsoft.com/en-us/overview/what-is-cloud-computing/"
            ],
            "python programming": [
                "https://docs.python.org/3/tutorial/",
                "https://realpython.com/python-basics/",
                "https://www.w3schools.com/python/"
            ],
            "climate change": [
                "https://en.wikipedia.org/wiki/Climate_change",
                "https://climate.nasa.gov/evidence/",
                "https://www.ipcc.ch/report/ar6/wg1/"
            ]
        }

        # Find matching URLs based on query keywords
        query_lower = query.lower()
        selected_urls = []

        for topic, urls in url_mapping.items():
            if any(keyword in query_lower for keyword in topic.split()):
                selected_urls.extend(urls)
                break

        # Default fallback URLs if no match
        if not selected_urls:
            selected_urls = [
                "https://en.wikipedia.org/wiki/Artificial_intelligence",
                "https://en.wikipedia.org/wiki/Machine_learning",
                "https://en.wikipedia.org/wiki/Cloud_computing"
            ]

        # Return valid URLs
        valid_urls = [url for url in selected_urls if self.is_valid_url(url)]
        result_urls = valid_urls[:num_results]

        logger.info(f"Selected {len(result_urls)} curated URLs for crawling")
        return result_urls

    def is_valid_url(self, url: str) -> bool:
        """Validate URL and check if it's crawlable"""
        try:
            parsed = urlparse(url)
            if not parsed.scheme or not parsed.netloc:
                return False
            domain = parsed.netloc.lower()
            return not any(blocked in domain for blocked in self.blocked_domains)
        except Exception:
            return False

    def extract_content(self, url: str) -> Dict[str, str]:
        """Extract content from URL with better error handling"""
        if url in self.crawled_urls:
            return None

        try:
            time.sleep(random.uniform(1, 2))  # Shorter delay
            self.session.headers['User-Agent'] = random.choice(self.user_agents)

            response = self.session.get(url, timeout=10, allow_redirects=True)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remove unwanted elements
            for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                tag.decompose()

            # Extract title
            title_tag = soup.find('title')
            title = title_tag.get_text().strip() if title_tag else "Unknown Title"

            # Extract main content - more aggressive
            content = ""

            # Try multiple content selectors
            content_selectors = ['article', 'main', '.content', '[role="main"]', 'section', 'div.post']
            for selector in content_selectors:
                elements = soup.select(selector)
                if elements:
                    content = ' '.join([elem.get_text().strip() for elem in elements])
                    if len(content) > 100:  # Good content found
                        break

            # Fallback: get all paragraph text
            if len(content) < 100:
                paragraphs = soup.find_all('p')
                content = ' '.join([p.get_text().strip() for p in paragraphs])

            # Final fallback: body text
            if len(content) < 100:
                body = soup.find('body')
                if body:
                    content = body.get_text(separator=' ', strip=True)

            # Clean content
            content = ' '.join(content.split())  # Remove extra whitespace
            content = re.sub(r'\s+', ' ', content)  # Normalize whitespace

            # Validate content quality
            if len(content) < 50:
                logger.warning(f"Low quality content from {url}: {len(content)} chars")
                return None

            self.crawled_urls.add(url)

            result = {
                'title': title[:200],
                'content': content[:3000],  # Reasonable limit
                'url': url,
                'domain': urlparse(url).netloc
            }

            logger.info(f"Successfully extracted content from {url}: {len(content)} chars")
            return result

        except requests.exceptions.Timeout:
            logger.warning(f"Timeout extracting {url}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"Request error for {url}: {e}")
        except Exception as e:
            logger.warning(f"Error extracting content from {url}: {e}")

        return None

    def sanitize_content(self, article: Dict[str, str]) -> Dict[str, str]:
        """Remove potentially sensitive information"""
        # Remove email addresses
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        article['content'] = re.sub(email_pattern, '[EMAIL]', article['content'])

        # Remove phone numbers
        phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
        article['content'] = re.sub(phone_pattern, '[PHONE]', article['content'])

        return article

    def crawl_for_query(self, query: str, max_articles: int = 2) -> List[Dict[str, str]]:
        """Crawl web for query with privacy protection"""
        logger.info(f"Starting crawl for: {self.anonymize_query(query)}")

        urls = self.get_search_urls(query, num_results=max_articles * 2)
        articles = []

        for url in urls:
            if len(articles) >= max_articles:
                break

            article = self.extract_content(url)
            if article:
                article = self.sanitize_content(article)
                articles.append(article)

        logger.info(f"Successfully crawled {len(articles)} articles for query")
        return articles

    def run(self):
        """Main crawler entry point - with better error handling"""
        logger.info("🚀 Starting crawl to populate knowledge base...")

        total_added = 0
        for topic in self.crawl_topics:
            try:
                articles = self.crawl_for_query(topic, max_articles=2)
                if articles:
                    self.rag_system.store_documents(articles)
                    total_added += len(articles)
                    logger.info(f"Added {len(articles)} articles for topic: {topic}")
                else:
                    logger.warning(f"No articles found for topic: {topic}")
            except Exception as e:
                logger.error(f"Error crawling topic '{topic}': {e}")
                continue

        logger.info(f"✅ Crawl finished. Total articles added: {total_added}")

        # If no articles were added, log warning
        if total_added == 0:
            logger.warning("No articles were successfully crawled. Check network connectivity and dependencies.")