import sys
from loguru import logger

from src.core.config import BASE_DIR


LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

logger.remove()

logger.add(
    sys.stdout,
    colorize=True,
    format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
           "<level>{level: <8}</level> | "
           "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
           "<level>{message}</level>",
    level="INFO",
)

logger.add(
    LOG_DIR / "app_info.log",
    rotation="10 MB",
    retention="10 days",
    compression="zip",
    level="INFO",
    enqueue=True,
    encoding="utf-8",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
)

logger.add(
    LOG_DIR / "app_errors.log",
    rotation="10 MB",
    retention="10 days",
    compression="zip",
    level="ERROR",
    # serialize=True,
    enqueue=True,
    encoding="utf-8",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
    backtrace=True,
    diagnose=True,
)
