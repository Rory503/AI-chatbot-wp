import os
import requests
from pathlib import Path
from io import BytesIO
from urllib.parse import urljoin, urlparse
from urllib.robotparser import RobotFileParser
from collections import deque
from pypdf import PdfReader
from bs4 import BeautifulSoup
from typing import List, Optional, Set
from dotenv import load_dotenv

load_dotenv()

class ContentIngester:
    """Ingest content from WordPress pages and local PDFs"""

    @staticmethod
    def _get_robot_parser(base_url: str) -> RobotFileParser:
        rp = RobotFileParser()
        robots_url = urljoin(base_url, '/robots.txt')
        rp.set_url(robots_url)
        try:
            rp.read()
        except Exception:
            # If robots.txt is unavailable, default to allowing.
            rp.parse([])
        return rp

    @staticmethod
    def _is_same_site(url: str, base_netloc: str) -> bool:
        try:
            return urlparse(url).netloc == base_netloc
        except Exception:
            return False

    @staticmethod
    def _should_skip_url(url: str) -> bool:
        lowered = url.lower()
        skip_exts = (
            '.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.ico',
            '.css', '.js', '.map', '.woff', '.woff2', '.ttf', '.eot',
            '.mp4', '.webm', '.mp3', '.wav', '.zip'
        )
        return lowered.endswith(skip_exts)

    @staticmethod
    def _get_sitemap_urls(base_url: str, session: requests.Session, rp: RobotFileParser) -> Set[str]:
        urls: Set[str] = set()
        sitemap_candidates = []

        # Try robots.txt declared sitemaps first
        try:
            for sitemap in rp.site_maps() or []:
                sitemap_candidates.append(sitemap)
        except Exception:
            pass

        # Fallback common sitemap paths
        if not sitemap_candidates:
            sitemap_candidates = [
                urljoin(base_url, '/sitemap.xml'),
                urljoin(base_url, '/sitemap_index.xml')
            ]

        for sitemap_url in sitemap_candidates:
            try:
                response = session.get(sitemap_url, timeout=15)
                if response.status_code >= 400:
                    continue
                soup = BeautifulSoup(response.content, 'xml')
                loc_tags = soup.find_all('loc')
                for loc in loc_tags:
                    loc_text = loc.get_text(strip=True)
                    if loc_text:
                        urls.add(loc_text)
            except Exception:
                continue

        return urls

    @staticmethod
    def _extract_links(html: bytes, base_url: str) -> Set[str]:
        links: Set[str] = set()
        soup = BeautifulSoup(html, 'html.parser')
        for a in soup.find_all('a', href=True):
            href = a.get('href', '').strip()
            if not href or href.startswith('#'):
                continue
            if href.startswith('mailto:') or href.startswith('tel:'):
                continue
            full_url = urljoin(base_url, href)
            links.add(full_url.split('#')[0])
        return links

    @staticmethod
    def _fetch_document(url: str, session: requests.Session) -> Optional[dict]:
        try:
            response = session.get(url, timeout=15)
            response.raise_for_status()
        except Exception:
            return None

        content_type = response.headers.get('Content-Type', '').lower()
        is_pdf = 'application/pdf' in content_type or url.lower().endswith('.pdf')

        if is_pdf:
            try:
                reader = PdfReader(BytesIO(response.content))
                pages = []
                for page in reader.pages:
                    text = page.extract_text() or ''
                    if text.strip():
                        pages.append(text)
                if not pages:
                    return None
                return {
                    'title': url.split('/')[-1],
                    'url': url,
                    'content': '\n'.join(pages),
                    'source_type': 'pdf'
                }
            except Exception:
                return None

        try:
            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.find('h1')
            title_text = title.get_text() if title else 'Unknown'
            content_div = soup.find('article') or soup.find('main') or soup.find(class_='content')
            if content_div:
                paragraphs = content_div.find_all(['p', 'h2', 'h3', 'li'])
                content = '\n'.join([p.get_text() for p in paragraphs])
            else:
                content = soup.get_text('\n')

            if not content.strip():
                return None

            return {
                'title': title_text,
                'url': url,
                'content': content,
                'source_type': 'wordpress'
            }
        except Exception:
            return None
    
    @staticmethod
    def crawl_wordpress_pages() -> List[dict]:
        """Crawl WordPress site and extract page content"""
        pages = []
        site_url = os.getenv('WORDPRESS_SITE_URL')
        crawl_urls = os.getenv('WORDPRESS_CRAWL_URLS', '').split(',')

        if not site_url:
            print("✗ WORDPRESS_SITE_URL is not set")
            return pages

        base_url = site_url.rstrip('/') + '/'
        base_netloc = urlparse(base_url).netloc
        session = requests.Session()
        session.headers.update({
            'User-Agent': f'NonProfitAI-Ingester/1.0 (+{base_url})'
        })
        rp = ContentIngester._get_robot_parser(base_url)

        max_pages = int(os.getenv('MAX_CRAWL_PAGES', '2000'))
        max_depth = int(os.getenv('MAX_CRAWL_DEPTH', '6'))
        
        crawl_urls = [u.strip() for u in crawl_urls if u.strip()]

        if crawl_urls:
            for url in crawl_urls:
                if not ContentIngester._is_same_site(url, base_netloc):
                    continue
                if ContentIngester._should_skip_url(url):
                    continue
                if not rp.can_fetch(session.headers['User-Agent'], url):
                    continue

                doc = ContentIngester._fetch_document(url, session)
                if doc:
                    pages.append(doc)
                    print(f"✓ Crawled: {url}")
            return pages

        # Auto-discovery: sitemap -> link crawl
        discovered = ContentIngester._get_sitemap_urls(base_url, session, rp)
        if discovered:
            for url in sorted(discovered):
                if len(pages) >= max_pages:
                    break
                if not ContentIngester._is_same_site(url, base_netloc):
                    continue
                if ContentIngester._should_skip_url(url):
                    continue
                if not rp.can_fetch(session.headers['User-Agent'], url):
                    continue
                doc = ContentIngester._fetch_document(url, session)
                if doc:
                    pages.append(doc)
                    print(f"✓ Crawled: {url}")
            return pages

        # Fallback: BFS crawl from base URL
        visited: Set[str] = set()
        queue = deque([(base_url, 0)])

        while queue and len(pages) < max_pages:
            current_url, depth = queue.popleft()
            if current_url in visited or depth > max_depth:
                continue
            visited.add(current_url)

            if not ContentIngester._is_same_site(current_url, base_netloc):
                continue
            if ContentIngester._should_skip_url(current_url):
                continue
            if not rp.can_fetch(session.headers['User-Agent'], current_url):
                continue

            doc = ContentIngester._fetch_document(current_url, session)
            if doc:
                pages.append(doc)
                print(f"✓ Crawled: {current_url}")

            try:
                response = session.get(current_url, timeout=15)
                response.raise_for_status()
                links = ContentIngester._extract_links(response.content, current_url)
                for link in links:
                    if link not in visited:
                        queue.append((link, depth + 1))
            except Exception:
                continue
        
        return pages
    
    @staticmethod
    def parse_pdf_files() -> List[dict]:
        """Parse local PDF files"""
        documents = []
        pdf_folder = os.getenv('PDF_FOLDER', './pdfs')
        
        if not os.path.exists(pdf_folder):
            print(f"⚠ PDF folder not found: {pdf_folder}")
            return documents
        
        for pdf_file in Path(pdf_folder).glob('*.pdf'):
            try:
                reader = PdfReader(pdf_file)
                
                for page_idx, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text.strip():
                        documents.append({
                            'title': pdf_file.stem,
                            'content': text,
                            'page_number': page_idx + 1,
                            'source_type': 'pdf',
                            'file_name': pdf_file.name
                        })
                
                print(f"✓ Parsed: {pdf_file.name} ({len(reader.pages)} pages)")
                
            except Exception as e:
                print(f"✗ Failed to parse {pdf_file.name}: {e}")
        
        return documents
    
    @staticmethod
    def chunk_content(documents: List[dict], chunk_size: int = 500, overlap: int = 100) -> List[dict]:
        """Split documents into chunks for embedding"""
        chunks = []
        
        for doc in documents:
            content = doc['content']
            words = content.split()
            
            for i in range(0, len(words), chunk_size - overlap):
                chunk_words = words[i:i + chunk_size]
                chunk_text = ' '.join(chunk_words)
                
                if len(chunk_text.strip()) > 50:  # Skip tiny chunks
                    chunks.append({
                        'text': chunk_text,
                        'source': doc.get('url') or doc.get('file_name', 'Unknown'),
                        'title': doc.get('title'),
                        'page_number': doc.get('page_number'),
                        'source_type': doc.get('source_type'),
                        'metadata': {
                            'original_title': doc.get('title'),
                            'source_type': doc.get('source_type')
                        }
                    })
        
        print(f"✓ Created {len(chunks)} chunks from {len(documents)} documents")
        return chunks
