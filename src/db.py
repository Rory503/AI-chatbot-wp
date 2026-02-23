import os
from supabase import create_client, Client
from dotenv import load_dotenv
import json

load_dotenv()

class SupabaseClient:
    """Connect to Supabase using REST API"""
    
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL", "").strip()
        supabase_service_key = os.getenv("SUPABASE_SERVICE_KEY", "").strip()

        if not supabase_url:
            raise ValueError("SUPABASE_URL is not set")
        if not supabase_service_key:
            raise ValueError("SUPABASE_SERVICE_KEY is not set")

        self.url = supabase_url
        self.key = supabase_service_key
        self.client: Client = None
    
    def connect(self):
        """Establish connection to Supabase"""
        try:
            self.client = create_client(self.url, self.key)
            print("✓ Connected to Supabase")
            self._init_pgvector()
        except Exception as e:
            print(f"✗ Supabase connection failed: {e}")
            raise
    
    def _init_pgvector(self):
        """Initialize pgvector extension and documents table via SQL"""
        try:
            # Execute SQL to create table and extension
            sql = """
            CREATE EXTENSION IF NOT EXISTS vector;
            
            CREATE TABLE IF NOT EXISTS documents (
                id SERIAL PRIMARY KEY,
                content TEXT NOT NULL,
                metadata JSONB,
                embedding vector(1536),
                source VARCHAR(255),
                page_number INT,
                created_at TIMESTAMP DEFAULT NOW()
            );
            
            CREATE INDEX IF NOT EXISTS embedding_idx 
            ON documents USING ivfflat (embedding vector_cosine_ops)
            WITH (lists = 100);
            """
            
            # Use RPC to execute raw SQL
            self.client.rpc('exec_sql', {'sql': sql}).execute()
            print("✓ pgvector tables initialized")
        except Exception as e:
            # Tables might already exist, that's okay
            print(f"ℹ pgvector init: {e}")
    
    def insert_document(self, content: str, embedding: list, source: str, page_number: int = None, metadata: dict = None):
        """Insert a document chunk with its embedding"""
        try:
            data = {
                "content": content,
                "embedding": embedding,
                "source": source,
                "page_number": page_number,
                "metadata": metadata or {}
            }
            self.client.table("documents").insert(data).execute()
        except Exception as e:
            print(f"✗ Insert failed: {e}")
            raise
    
    def search_by_embedding(self, query_embedding: list, limit: int = 5, threshold: float = 0.5):
        """Search documents by vector similarity using RPC"""
        try:
            # Use RPC function for vector similarity search
            result = self.client.rpc(
                'match_documents',
                {
                    'query_embedding': query_embedding,
                    'match_threshold': threshold,
                    'match_count': limit
                }
            ).execute()
            
            return result.data if result.data else []
        except Exception as e:
            print(f"✗ Search failed: {e}")
            # Fallback: get all documents and filter manually
            return self._manual_search(query_embedding, limit, threshold)
    
    def _manual_search(self, query_embedding: list, limit: int, threshold: float):
        """Fallback manual search if RPC function doesn't exist"""
        try:
            # Get all documents
            result = self.client.table("documents").select("*").execute()
            docs = result.data
            
            # Calculate cosine similarity manually
            import numpy as np
            
            results = []
            for doc in docs:
                if doc.get('embedding'):
                    # Cosine similarity calculation
                    emb = np.array(doc['embedding'])
                    query = np.array(query_embedding)
                    similarity = np.dot(emb, query) / (np.linalg.norm(emb) * np.linalg.norm(query))
                    
                    if similarity > threshold:
                        results.append({
                            'id': doc['id'],
                            'content': doc['content'],
                            'source': doc['source'],
                            'page_number': doc['page_number'],
                            'similarity': float(similarity)
                        })
            
            # Sort by similarity and limit
            results.sort(key=lambda x: x['similarity'], reverse=True)
            return results[:limit]
        except Exception as e:
            print(f"✗ Manual search failed: {e}")
            return []
    
    def clear_documents(self):
        """Clear all documents (for reingestion)"""
        try:
            self.client.table("documents").delete().neq('id', 0).execute()
            print("✓ Documents cleared")
        except Exception as e:
            print(f"✗ Clear failed: {e}")
            raise
    
    def close(self):
        """Close connection (not needed for REST API)"""
        pass


# Singleton instance
_db_client = None

def get_db():
    global _db_client
    if _db_client is None:
        _db_client = SupabaseClient()
        _db_client.connect()
    return _db_client
