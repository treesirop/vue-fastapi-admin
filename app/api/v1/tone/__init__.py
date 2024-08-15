from fastapi import APIRouter

from .tone import router

tone_router = APIRouter()
tone_router.include_router(router, tags=["音色模块"])

__all__ = ["roles_router"]
