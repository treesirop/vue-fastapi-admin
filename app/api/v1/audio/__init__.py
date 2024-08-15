from fastapi import APIRouter

from .audio import router

audio_router = APIRouter()
audio_router.include_router(router, tags=["音频模块"])

__all__ = ["roles_router"]
