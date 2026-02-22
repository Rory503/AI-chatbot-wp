"""
Vercel serverless function handler for FastAPI
Maps Vercel requests to FastAPI app
"""

from src.api.main import app

async def handler(request):
    """Vercel serverless handler"""
    return await app(request)
