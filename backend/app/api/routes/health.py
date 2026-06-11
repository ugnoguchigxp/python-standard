import time
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.session import get_db

router = APIRouter()


@router.get("/liveness", status_code=status.HTTP_200_OK)
async def check_liveness():
    """Liveness check to verify the service is running."""
    return {"status": "ok", "timestamp": time.time()}


@router.get("/readiness", status_code=status.HTTP_200_OK)
async def check_readiness(db: AsyncSession = Depends(get_db)):
    """Readiness check to verify the database connectivity is active."""
    try:
        # Run a simple query to verify connection
        await db.execute(select(1))
        return {
            "status": "ready",
            "database": "connected",
            "timestamp": time.time(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database connection failure: {str(e)}",
        )
