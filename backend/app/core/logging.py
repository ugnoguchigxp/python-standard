import logging
import sys

from app.core.config import settings


class CancelledErrorFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        if "CancelledError" in msg and "starlette/routing.py" in msg:
            return False
        return True


def setup_logging() -> None:
    # Remove all handlers from the root logger
    logging.root.handlers = []

    # Choose log level
    log_level = logging.INFO
    if settings.ENVIRONMENT == "development":
        log_level = logging.DEBUG

    # Format config
    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Set logger levels for noisy libraries
    logging.getLogger("uvicorn.error").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("aiosqlite").setLevel(logging.WARNING)

    # Add CancelledErrorFilter to suppress noisy shutdown tracebacks
    cancelled_filter = CancelledErrorFilter()
    logging.root.addFilter(cancelled_filter)
    logging.getLogger("uvicorn.error").addFilter(cancelled_filter)

    logging.info("Logging system initialized.")

