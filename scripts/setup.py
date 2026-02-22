#!/usr/bin/env python3
"""
Setup script for local development
Initializes database and ingests initial content
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def setup():
    print("🚀 Setting up Nonprofit Chatbot...")
    
    # Check environment variables
    required_vars = ['OPENAI_API_KEY', 'SUPABASE_URL', 'SUPABASE_KEY', 'SUPABASE_DB_PASSWORD']
    missing = [v for v in required_vars if not os.getenv(v)]
    
    if missing:
        print(f"❌ Missing environment variables: {', '.join(missing)}")
        print("   Copy .env.example to .env and fill in your secrets")
        return False
    
    # Initialize database
    print("\n📦 Initializing database...")
    try:
        from src.db import get_db
        db = get_db()
        print("✓ Database connected and pgvector initialized")
    except Exception as e:
        print(f"❌ Database setup failed: {e}")
        return False
    
    # Ingest content
    print("\n📚 Ingesting content...")
    print("   Make sure your PDFs are in ./pdfs/ and WORDPRESS_CRAWL_URLS is set in .env")
    
    try:
        from src.ingestion.content_ingester import ContentIngester
        from src.ingestion.embedding_manager import EmbeddingManager
        
        embedding_mgr = EmbeddingManager()
        
        # Clear existing
        db.clear_documents()
        
        # Ingest
        pages = ContentIngester.crawl_wordpress_pages()
        pdfs = ContentIngester.parse_pdf_files()
        all_docs = pages + pdfs
        
        if not all_docs:
            print("⚠ No content found. Add WordPress URLs and PDFs, then run again.")
            return True
        
        chunks = ContentIngester.chunk_content(all_docs)
        embedded = embedding_mgr.embed_chunks(chunks)
        
        # Store in DB
        for chunk in embedded:
            db.insert_document(
                content=chunk['text'],
                embedding=chunk['embedding'],
                source=chunk['source'],
                page_number=chunk.get('page_number'),
                metadata=chunk.get('metadata')
            )
        
        print(f"✓ Ingested {len(all_docs)} documents → {len(embedded)} chunks")
        
    except Exception as e:
        print(f"❌ Ingestion failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n✅ Setup complete!")
    print("\nNext steps:")
    print("  1. Start the API: python -m src.api.main")
    print("  2. Test the endpoint: curl -X POST http://localhost:8000/chat -H 'Content-Type: application/json' -d '{\"query\": \"Your question here\"}'")
    print("  3. Embed widget on WordPress: Copy widget code and set API_URL to your deployment")
    return True

if __name__ == '__main__':
    success = setup()
    sys.exit(0 if success else 1)
