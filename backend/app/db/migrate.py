import logging

from sqlmodel import SQLModel

from app.db.session import engine

# Import all models to ensure they are registered on SQLModel.metadata

logger = logging.getLogger(__name__)


async def init_db() -> None:
    logger.info("Initializing database tables...")
    async with engine.begin() as conn:
        # Create tables if they do not exist
        await conn.run_sync(SQLModel.metadata.create_all)
    logger.info("Database tables initialized successfully.")
