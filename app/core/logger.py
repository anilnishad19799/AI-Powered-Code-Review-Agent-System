import sys
from loguru import logger
from app.core.config import get_settings

settings = get_settings()


def setup_logger() -> None:
    logger.remove()  # Remove default handler

    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )

    # Console handler
    logger.add(
        sys.stdout,
        format=log_format,
        level=settings.log_level,
        colorize=True,
        backtrace=True,
        diagnose=settings.is_development,
    )

    # File handler — rotates daily, keeps 7 days
    logger.add(
        "logs/pr_review_{time:YYYY-MM-DD}.log",
        format=log_format,
        level="DEBUG",
        rotation="00:00",
        retention="7 days",
        compression="zip",
        backtrace=True,
        diagnose=False,  # Never True in prod (leaks secrets)
    )

    logger.info(f"Logger initialized | env={settings.app_env} | level={settings.log_level}")


# Re-export so all files do: from app.core.logger import logger
__all__ = ["logger", "setup_logger"]