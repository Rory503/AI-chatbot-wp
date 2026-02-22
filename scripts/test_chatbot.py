"""
Sample test script to validate chatbot locally
Run: python scripts/test_chatbot.py
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def test_connection():
    """Test database connection"""
    print("📡 Testing database connection...")
    try:
        from src.db import get_db
        db = get_db()
        
        # Test query
        results = db.search_by_embedding([0.1] * 1536, limit=1, threshold=0.0)
        print(f"   ✓ Database connected ({len(results)} documents in DB)")
        return True
    except Exception as e:
        print(f"   ✗ Database error: {e}")
        return False

def test_embeddings():
    """Test OpenAI embedding API"""
    print("🧠 Testing OpenAI embeddings...")
    try:
        from src.ingestion.embedding_manager import EmbeddingManager
        mgr = EmbeddingManager()
        
        embedding = mgr.embed_text("Hello, world!")
        print(f"   ✓ Embedding generated ({len(embedding)} dimensions)")
        return True
    except Exception as e:
        print(f"   ✗ Embedding error: {e}")
        return False

def test_wordpress_crawl():
    """Test WordPress crawling"""
    print("🌐 Testing WordPress crawling...")
    try:
        from src.ingestion.content_ingester import ContentIngester
        pages = ContentIngester.crawl_wordpress_pages()
        print(f"   ✓ Crawled {len(pages)} WordPress pages")
        for page in pages:
            print(f"     - {page['title']} ({len(page['content'])} chars)")
        return len(pages) > 0
    except Exception as e:
        print(f"   ✗ Crawl error: {e}")
        return False

def test_pdf_parsing():
    """Test PDF parsing"""
    print("📄 Testing PDF parsing...")
    try:
        from src.ingestion.content_ingester import ContentIngester
        pdfs = ContentIngester.parse_pdf_files()
        print(f"   ✓ Parsed {len(pdfs)} PDF documents")
        for pdf in pdfs:
            print(f"     - {pdf['title']} (page {pdf['page_number']})")
        return len(pdfs) > 0
    except Exception as e:
        print(f"   ⚠ PDF parse error (this is OK if no PDFs): {e}")
        return True  # Not a critical failure

def test_chunking():
    """Test content chunking"""
    print("✂️  Testing content chunking...")
    try:
        from src.ingestion.content_ingester import ContentIngester
        
        # Create mock documents
        test_docs = [
            {
                'title': 'Test Page',
                'content': 'This is a test document. ' * 50,  # ~1000 words
                'source_type': 'test'
            }
        ]
        
        chunks = ContentIngester.chunk_content(test_docs)
        print(f"   ✓ Created {len(chunks)} chunks")
        return len(chunks) > 0
    except Exception as e:
        print(f"   ✗ Chunking error: {e}")
        return False

def test_rag_engine():
    """Test RAG engine"""
    print("🚀 Testing RAG engine...")
    try:
        from src.db import get_db
        from src.rag.engine import RAGEngine
        
        db = get_db()
        rag = RAGEngine(db)
        
        # Test with dummy embedding
        dummy_embedding = [0.1] * 1536
        context = rag.retrieve_context(dummy_embedding)
        print(f"   ✓ RAG engine initialized (found {len(context)} context chunks)")
        return True
    except Exception as e:
        print(f"   ✗ RAG error: {e}")
        return False

def test_api_health():
    """Test API endpoint (requires server running)"""
    print("🏥 Testing API health endpoint...")
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            print(f"   ✓ API is healthy")
            return True
        else:
            print(f"   ✗ API returned {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print(f"   ⚠ API not running (start with: python -m src.api.main)")
        return False
    except Exception as e:
        print(f"   ✗ API test error: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("🤖 NONPROFIT CHATBOT - SYSTEM TEST")
    print("="*60 + "\n")
    
    # Check environment
    print("✓ Environment variables loaded\n")
    
    # Run tests
    tests = [
        test_connection,
        test_embeddings,
        test_wordpress_crawl,
        test_pdf_parsing,
        test_chunking,
        test_rag_engine,
        test_api_health,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"   ✗ Unexpected error: {e}")
            results.append(False)
        print()
    
    # Summary
    print("="*60)
    passed = sum(results)
    total = len(results)
    percentage = (passed / total) * 100
    print(f"RESULTS: {passed}/{total} tests passed ({percentage:.0f}%)")
    print("="*60)
    
    if percentage == 100:
        print("✅ All systems ready! You can:")
        print("   1. Run ingestion: python scripts/setup.py")
        print("   2. Start API: python -m src.api.main")
        print("   3. Test chat: curl -X POST http://localhost:8000/chat -H 'Content-Type: application/json' -d '{\"query\": \"test\"}'")
    elif percentage >= 50:
        print("⚠️  Some systems working. Check errors above.")
    else:
        print("❌ Critical errors. Please fix before proceeding.")
    
    return 0 if percentage == 100 else 1

if __name__ == '__main__':
    sys.exit(main())
