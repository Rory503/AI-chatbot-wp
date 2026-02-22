import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Tuple

load_dotenv()

class RAGEngine:
    """Retrieve context and generate grounded answers with citations"""
    
    def __init__(self, db_client):
        self.db = db_client
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.llm_model = os.getenv('LLM_MODEL', 'gpt-4o-mini')
        self.confidence_threshold = float(os.getenv('CONFIDENCE_THRESHOLD', 0.5))
        self.max_context_chunks = int(os.getenv('MAX_CONTEXT_CHUNKS', 5))
    
    def retrieve_context(self, query_embedding: list) -> List[dict]:
        """Find relevant documents by vector similarity"""
        results = self.db.search_by_embedding(
            query_embedding=query_embedding,
            limit=self.max_context_chunks,
            threshold=self.confidence_threshold
        )
        return results
    
    def generate_answer(self, query: str, context_chunks: List[dict]) -> Tuple[str, List[dict], float]:
        """Generate grounded answer with citations and confidence score"""
        
        # Check if we have sufficient context
        if not context_chunks:
            return "I don't have information to answer that question. Please try asking about content on our site.", [], 0.0
        
        # Calculate average confidence
        avg_confidence = sum([c['similarity'] for c in context_chunks]) / len(context_chunks)
        
        if avg_confidence < self.confidence_threshold:
            return "I'm not confident enough in my sources to answer this accurately. Could you rephrase your question?", context_chunks, avg_confidence
        
        # Build context string with source attribution
        context_text = "\n\n".join([
            f"[Source: {c['source']} - Similarity: {c['similarity']:.2f}]\n{c['content']}"
            for c in context_chunks
        ])
        
        # Build prompt for grounded answering
        system_prompt = """You are a helpful assistant answering questions based on provided documents.
IMPORTANT RULES:
1. Answer ONLY using the provided context.
2. If the context doesn't support an answer, say "I don't know" rather than guessing.
3. Include citations like [Source: document_name] after facts.
4. Be concise and accurate.
5. If unsure about something, acknowledge it."""
        
        user_prompt = f"""Context from our documents:
{context_text}

Question: {query}

Please answer based ONLY on the provided context. Include citations."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.llm_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3,  # Lower temperature for factual accuracy
                max_tokens=500
            )
            
            answer = response.choices[0].message.content
            return answer, context_chunks, avg_confidence
            
        except Exception as e:
            print(f"✗ Answer generation failed: {e}")
            return "I encountered an error processing your question. Please try again.", context_chunks, 0.0
