import os
from urllib.parse import urlparse
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

load_dotenv()

class SupabaseClient:
    """Connect to Supabase (PostgreSQL + pgvector)"""
    
    def __init__(self):
        supabase_url = os.getenv("SUPABASE_URL", "").strip()
        supabase_password = os.getenv("SUPABASE_DB_PASSWORD", "").strip()
        db_host = os.getenv("SUPABASE_DB_HOST", "").strip()
        db_port = os.getenv("SUPABASE_DB_PORT", "").strip() or "5432"
        db_user = os.getenv("SUPABASE_DB_USER", "").strip() or "postgres"
        db_name = os.getenv("SUPABASE_DB_NAME", "").strip() or "postgres"

        if not supabase_url:
            raise ValueError("SUPABASE_URL is not set")
        if not supabase_password:
            raise ValueError("SUPABASE_DB_PASSWORD is not set")

        if db_host:
            host = db_host
        else:
            parsed = urlparse(supabase_url)
            host = parsed.netloc or parsed.path

        if not host:
            raise ValueError("SUPABASE_URL is invalid (missing host)")

        self.connection_string = f"postgresql://{db_user}:{supabase_password}@{host}:{db_port}/{db_name}"
        self.conn = None
    
    def connect(self):
        """Establish connection to Supabase"""
        try:
            self.conn = psycopg2.connect(self.connection_string, sslmode="require")
            print("✓ Connected to Supabase")
            self._init_pgvector()
        except Exception as e:
            print(f"✗ Supabase connection failed: {e}")
            raise
    
    def _init_pgvector(self):
        """Initialize pgvector extension and documents table"""
        with self.conn.cursor() as cur:
            # Enable pgvector extension
            cur.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            
            # Create documents table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS documents (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL,
                    metadata JSONB,
                    embedding vector(1536),
                    source VARCHAR(255),
                    page_number INT,
                    created_at TIMESTAMP DEFAULT NOW()
                );
            """)
            
            # Create index for vector similarity search
            cur.execute("""
                CREATE INDEX IF NOT EXISTS embedding_idx 
                ON documents USING ivfflat (embedding vector_cosine_ops)
                WITH (lists = 100);
            """)
            
            self.conn.commit()
            print("✓ pgvector tables initialized")
    
    def insert_document(self, content: str, embedding: list, source: str, page_number: int = None, metadata: dict = None):
        """Insert a document chunk with its embedding"""
        with self.conn.cursor() as cur:
            cur.execute("""
                INSERT INTO documents (content, embedding, source, page_number, metadata)
                VALUES (%s, %s, %s, %s, %s)
            """, (content, embedding, source, page_number, metadata))
            self.conn.commit()
    
    def search_by_embedding(self, query_embedding: list, limit: int = 5, threshold: float = 0.5):
        """Search documents by vector similarity"""
        with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("""
                SELECT id, content, source, page_number, 
                       1 - (embedding <=> %s::vector) as similarity
                FROM documents
                WHERE 1 - (embedding <=> %s::vector) > %s
                ORDER BY similarity DESC
                LIMIT %s
            """, (embedding, embedding, threshold, limit))
            return cur.fetchall()
    
    def clear_documents(self):
        """Clear all documents (for reingestion)"""
        with self.conn.cursor() as cur:
            cur.execute("DELETE FROM documents;")
            self.conn.commit()
            print("✓ Documents cleared")
    
    def close(self):
        if self.conn:
            self.conn.close()


# Singleton instance
_db_client = None

def get_db():
    global _db_client
    if _db_client is None:
        _db_client = SupabaseClient()
        _db_client.connect()
    return _db_client
