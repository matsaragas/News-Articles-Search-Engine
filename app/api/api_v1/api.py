from fastapi import APIRouter

from app.api.api_v1.endpoints import search_engine

api_router = APIRouter()
api_router.include_router(search_engine.api_router, prefix="/search", tags=["Search Engine"])

