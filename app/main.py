import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.core.config import get_settings
from app.core.logger import setup_logger, logger
from app.core.exception import PRReviewBaseException, global_exception_handler
from app.api.webhook import router as webhook_router

settings = get_settings()

# Create logs dir if not exists
os.makedirs("logs", exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_logger()
    logger.info("🚀 PR Review Agent starting")
    logger.info(f"   Environment : {settings.app_env}")
    logger.info(f"   Model       : {settings.openai_model}")
    yield
    logger.info("🛑 PR Review Agent shutting down")


app = FastAPI(
    title="AI PR Review Agent",
    description="Multi-agent code review system powered by Claude + LangGraph",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if not settings.is_production else None,
)

# Global exception handler
app.add_exception_handler(PRReviewBaseException, global_exception_handler)

# Routes
app.include_router(webhook_router, prefix="/api", tags=["Webhook"])


@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "env": settings.app_env,
        "model": settings.openai_model,
    }