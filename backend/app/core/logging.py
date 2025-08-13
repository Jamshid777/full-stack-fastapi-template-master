import logging
from loguru import logger
import sys
from app.core.config import settings

class InterceptHandler(logging.Handler):
    def emit(self, record: logging.LogRecord) -> None:
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno
        logger.opt(depth=6, exception=record.exc_info).log(level, record.getMessage())

def configure_logging() -> None:
    logging.getLogger().handlers = [InterceptHandler()]
    for name in ("uvicorn", "uvicorn.access", "uvicorn.error"):
        logging.getLogger(name).handlers = [InterceptHandler()]
    logger.remove()
    logger.add(sys.stdout, level=settings.log_level, serialize=False, backtrace=True, diagnose=False)