from contextlib import asynccontextmanager

import secure
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from secure.middleware import SecureASGIMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.api.routes import auth, health, items
from app.core.config import settings
from app.core.logging import setup_logging
from app.db.migrate import init_db

# Initialize logging
setup_logging()

# Setup rate limiter
limiter = Limiter(
    key_func=get_remote_address, default_limits=[settings.RATE_LIMIT_DEFAULT]
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Initialize database tables
    await init_db()
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc",
    lifespan=lifespan,
)

# Register rate limiter
app.state.limiter = limiter


@app.exception_handler(RateLimitExceeded)
async def rate_limit_exceeded_handler(
    request: Request, exc: RateLimitExceeded
) -> Response:
    return _rate_limit_exceeded_handler(request, exc)


# Set CORS middleware
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Set secure headers middleware
# Sets CSP, HSTS, X-Content-Type-Options, X-Frame-Options, X-XSS-Protection, etc.
secure_headers = secure.Secure.with_default_headers()
app.add_middleware(SecureASGIMiddleware, secure=secure_headers)

# Register API Routers
app.include_router(
    health.router, prefix=f"{settings.API_V1_STR}/health", tags=["health"]
)
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(items.router, prefix=f"{settings.API_V1_STR}/items", tags=["items"])


@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}! Access API docs at {settings.API_V1_STR}/docs"
    }
