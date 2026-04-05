"""fahimni FastAPI application factory."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fahimni.core.config import settings

logging.basicConfig(level=settings.log_level)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(
        title="fahimni API",
        version="0.1.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # tighten in production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers here as you build them:
    # from fahimni.api.v1 import auth, users, courses
    # app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    logger.info("fahimni application created")
    return app


app = create_app()