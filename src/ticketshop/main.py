from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel

from src.ticketshop.core.config import settings
from src.ticketshop.core.broker import broker
from src.ticketshop.api.v1.router import api_router
from src.ticketshop.messaging.subscribers.user_registered import router as user_registered_router
from src.ticketshop.db.session import engine

import src.ticketshop.db.base

broker.include_router(user_registered_router)

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
STATIC_DIR = PROJECT_ROOT / "static"


async def _create_tables() -> None:
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await broker.start()
    try:
        await _create_tables()
    except Exception:
        pass
    yield
    await broker.stop()

def create_app() -> FastAPI:
    app = FastAPI(title="Ticket shop", lifespan=lifespan)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api/v1")

    if STATIC_DIR.is_dir():
        app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

        @app.get("/")
        async def spa_index():
            return FileResponse(STATIC_DIR / "index.html")

    return app

app = create_app()