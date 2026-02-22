import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

class EmbeddingManager:
    """Generate embeddings and manage vector storage"""
    
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.embedding_model = os.getenv('EMBEDDING_MODEL', 'text-embedding-3-small')
    
    def embed_text(self, text: str) -> list:
        """Generate embedding for a text chunk"""
        try:
            response = self.client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            print(f"✗ Embedding failed for text: {e}")
            raise
    
    def embed_chunks(self, chunks: list) -> list:
        """Embed multiple chunks with batch processing"""
        embedded_chunks = []
        
        for i, chunk in enumerate(chunks):
            embedding = self.embed_text(chunk['text'])
            embedded_chunks.append({
                **chunk,
                'embedding': embedding
            })
            
            if (i + 1) % 10 == 0:
                print(f"  Embedded {i + 1}/{len(chunks)} chunks")
        
        print(f"✓ Embedded {len(embedded_chunks)} chunks")
        return embedded_chunks
