from contextlib import asynccontextmanager

from fastapi import FastAPI
from tortoise import Tortoise
from fastapi.staticfiles import StaticFiles
from app.core.exceptions import SettingNotFound
from app.core.init_app import (
    init_scheduler,
    init_superuser,
    make_middlewares,
    register_exceptions,
    register_routers,
)

try:
    from app.settings.config import settings
except ImportError:
    raise SettingNotFound("Can not import settings")


@asynccontextmanager
async def lifespan(app: FastAPI):
    await Tortoise.init(config=settings.TORTOISE_ORM)
    await Tortoise.generate_schemas()
    await init_superuser()
    await init_scheduler(app)
    yield
    await Tortoise.close_connections()


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_TITLE,
        description=settings.APP_DESCRIPTION,
        version=settings.VERSION,
        openapi_url="/openapi.json",
        middleware=make_middlewares(),
        lifespan=lifespan,
    )
    app.mount("/static_avatar", StaticFiles(directory="app/utils/avatars"), name="static")
    app.mount("/static_audio", StaticFiles(directory="app/utils/save_audios"), name="static")
    
    register_exceptions(app)
    register_routers(app, prefix="/api")
    return app


app = create_app()
