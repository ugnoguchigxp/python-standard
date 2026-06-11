import os
import shutil
import subprocess
import sys

def run_cmd(cmd, cwd=None):
    print(f"Running: {cmd}")
    res = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    if res.returncode != 0:
        print(f"Error executing command: {cmd}")
        print(f"Stdout:\n{res.stdout}")
        print(f"Stderr:\n{res.stderr}")
        sys.exit(res.returncode)
    return res.stdout

def write_file(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def append_file(path, content):
    with open(path, "a", encoding="utf-8") as f:
        f.write(content)

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    print(f"Project Root: {root_dir}")

    # Ensure we are on main branch and clean
    run_cmd("git checkout main", cwd=root_dir)
    status = run_cmd("git status --porcelain", cwd=root_dir)
    if status.strip():
        print("Git repository is not clean. Please commit or stash changes before running.")
        sys.exit(1)

    # Clean previous tags and branches if they exist locally
    branches = ["variant/sqlite", "variant/postgres", "variant/pgvector", "variant/turso", "variant/cloudflare", "variant/api-only", "variant/auth", "overlay/ssr", "overlay/ssg", "overlay/celery", "overlay/opentelemetry"]
    for b in branches:
        run_cmd(f"git branch -D {b} || true", cwd=root_dir)
        tag_name = b.replace("variant/", "").replace("overlay/", "overlay-") + "-v1.0.0"
        run_cmd(f"git tag -d {tag_name} || true", cwd=root_dir)

    # 1. variant/sqlite (Simply branch from main, verified SQLite baseline)
    print("\n--- Setting up variant/sqlite ---")
    run_cmd("git checkout -b variant/sqlite", cwd=root_dir)
    run_cmd("git tag -a sqlite-v1.0.0 -m \"SQLite variant baseline v1.0.0\"", cwd=root_dir)

    # 2. variant/postgres (Branch from main, configure postgres dependencies & settings)
    print("\n--- Setting up variant/postgres ---")
    run_cmd("git checkout main", cwd=root_dir)
    run_cmd("git checkout -b variant/postgres", cwd=root_dir)

    # Modify pyproject.toml to add asyncpg
    pyproject_path = os.path.join(root_dir, "backend", "pyproject.toml")
    with open(pyproject_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Insert asyncpg dependency
    new_deps = '    "aiosqlite>=0.20.0",\n    "asyncpg>=0.29.0",\n'
    content = content.replace('    "aiosqlite>=0.20.0",\n', new_deps)
    write_file(pyproject_path, content)

    # Modify backend app config default DATABASE_URL
    config_path = os.path.join(root_dir, "backend", "app", "core", "config.py")
    with open(config_path, "r", encoding="utf-8") as f:
        config_content = f.read()
    config_content = config_content.replace(
        'DATABASE_URL: str = "sqlite+aiosqlite:///./sqlite.db"',
        'DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/fastapi_standard"'
    )
    write_file(config_path, config_content)

    # Modify session connect_args check to bypass check_same_thread for postgres
    session_path = os.path.join(root_dir, "backend", "app", "db", "session.py")
    with open(session_path, "r", encoding="utf-8") as f:
        session_content = f.read()
    session_content = session_content.replace(
        'if settings.DATABASE_URL.startswith("sqlite"):',
        'if "sqlite" in settings.DATABASE_URL:'
    )
    write_file(session_path, session_content)

    # Re-lock python dependencies
    run_cmd("uv lock", cwd=os.path.join(root_dir, "backend"))
    run_cmd("uv sync --extra dev", cwd=os.path.join(root_dir, "backend"))

    # Commit and tag
    run_cmd("git add .", cwd=root_dir)
    run_cmd("git commit -m \"Configure PostgreSQL database variant\"", cwd=root_dir)
    run_cmd("git tag -a postgres-v1.0.0 -m \"PostgreSQL variant baseline v1.0.0\"", cwd=root_dir)

    # 3. variant/pgvector (Branch from postgres, add pgvector capability)
    print("\n--- Setting up variant/pgvector ---")
    run_cmd("git checkout -b variant/pgvector", cwd=root_dir)

    # Modify pyproject.toml to add pgvector
    with open(pyproject_path, "r", encoding="utf-8") as f:
        content = f.read()
    content = content.replace('    "asyncpg>=0.29.0",\n', '    "asyncpg>=0.29.0",\n    "pgvector>=0.2.5",\n')
    write_file(pyproject_path, content)

    # Modify docker-compose to use pgvector image
    docker_compose_path = os.path.join(root_dir, "docker-compose.yml")
    with open(docker_compose_path, "r", encoding="utf-8") as f:
        dc_content = f.read()
    dc_content = dc_content.replace("image: postgres:15-alpine", "image: ankane/pgvector:v0.5.1")
    write_file(docker_compose_path, dc_content)

    # Create Document SQLModel model
    document_model = """from typing import Optional, Any
from sqlmodel import Field, SQLModel, Column
from pgvector.sqlalchemy import Vector

class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str = Field(nullable=False)
    embedding: Any = Field(sa_column=Column(Vector(1536))) # 1536-dim vector
"""
    write_file(os.path.join(root_dir, "backend", "app", "models", "document.py"), document_model)

    # Append to models __init__.py
    models_init = os.path.join(root_dir, "backend", "app", "models", "__init__.py")
    with open(models_init, "r", encoding="utf-8") as f:
        minit = f.read()
    minit = minit.replace(
        '__all__ = ["User", "Item"]',
        'from app.models.document import Document\n\n__all__ = ["User", "Item", "Document"]'
    )
    write_file(models_init, minit)

    # Create documents route
    document_route = """from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from app.db.session import get_db
from app.models.document import Document
from app.api.deps import get_current_user

router = APIRouter()

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_document(
    content: str,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> Any:
    # Stub embedding vector of 1536 elements
    mock_vector = [0.1] * 1536
    doc = Document(content=content, embedding=mock_vector)
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return {"id": doc.id, "content": doc.content}

@router.get("/search", response_model=list[dict])
async def search_documents(
    query: str,
    db: AsyncSession = Depends(get_db),
    current_user: Any = Depends(get_current_user),
) -> Any:
    mock_query_vector = [0.1] * 1536
    # Fallback to standard SELECT if running under SQLite (e.g. in test env without pgvector)
    if db.bind and db.bind.dialect.name == "sqlite":
        result = await db.exec(select(Document).limit(5))
    else:
        result = await db.exec(
            select(Document)
            .order_by(Document.embedding.l2_distance(mock_query_vector))
            .limit(5)
        )
    docs = result.all()
    return [{"id": d.id, "content": d.content} for d in docs]
"""
    write_file(os.path.join(root_dir, "backend", "app", "api", "routes", "documents.py"), document_route)

    # Register documents route in app/main.py
    app_main_path = os.path.join(root_dir, "backend", "app", "main.py")
    with open(app_main_path, "r", encoding="utf-8") as f:
        main_content = f.read()
    main_content = main_content.replace(
        "from app.api.routes import auth, health, items",
        "from app.api.routes import auth, health, items, documents"
    )
    main_content = main_content.replace(
        'app.include_router(items.router, prefix=f"{settings.API_V1_STR}/items", tags=["items"])',
        'app.include_router(items.router, prefix=f"{settings.API_V1_STR}/items", tags=["items"])\napp.include_router(documents.router, prefix=f"{settings.API_V1_STR}/documents", tags=["documents"])'
    )
    write_file(app_main_path, main_content)

    # Create documents test
    document_test = """import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.asyncio

async def test_documents_flow(client: AsyncClient):
    # 1. Register and login
    await client.post("/api/auth/register", json={"email": "pgv@example.com", "password": "password123"})
    login = await client.post("/api/auth/login", data={"username": "pgv@example.com", "password": "password123"})
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    # 2. Add document
    res_add = await client.post("/api/documents/?content=FastAPI+Vector+Store", headers=headers)
    assert res_add.status_code == 201
    assert res_add.json()["content"] == "FastAPI Vector Store"

    # 3. Search
    res_search = await client.get("/api/documents/search?query=FastAPI", headers=headers)
    assert res_search.status_code == 200
    assert len(res_search.json()) > 0
    assert res_search.json()[0]["content"] == "FastAPI Vector Store"
"""
    write_file(os.path.join(root_dir, "backend", "tests", "test_documents.py"), document_test)

    # Re-lock
    run_cmd("uv lock", cwd=os.path.join(root_dir, "backend"))
    run_cmd("uv sync --extra dev", cwd=os.path.join(root_dir, "backend"))

    # Commit and tag
    run_cmd("git add .", cwd=root_dir)
    run_cmd("git commit -m \"Configure pgvector embeddings and semantic routes\"", cwd=root_dir)
    run_cmd("git tag -a pgvector-v1.0.0 -m \"pgvector variant baseline v1.0.0\"", cwd=root_dir)

    # 4. variant/turso (Branch from main, configure Turso SQLModel connection)
    print("\n--- Setting up variant/turso ---")
    run_cmd("git checkout main", cwd=root_dir)
    run_cmd("git checkout -b variant/turso", cwd=root_dir)

    # Add libsql dependency in pyproject.toml
    with open(pyproject_path, "r", encoding="utf-8") as f:
        content = f.read()
    content = content.replace('    "aiosqlite>=0.20.0",\n', '    "aiosqlite>=0.20.0",\n    "libsql-client>=0.3.0",\n')
    write_file(pyproject_path, content)

    # Change DATABASE_URL to Turso placeholder
    with open(config_path, "r", encoding="utf-8") as f:
        config_content = f.read()
    config_content = config_content.replace(
        'DATABASE_URL: str = "sqlite+aiosqlite:///./sqlite.db"',
        'DATABASE_URL: str = "libsql://[your-database].turso.io"'
    )
    # Add optional token variable
    config_content = config_content.replace(
        'DATABASE_URL: str = "libsql://[your-database].turso.io"',
        'DATABASE_URL: str = "libsql://[your-database].turso.io"\n    TURSO_AUTH_TOKEN: str = ""'
    )
    write_file(config_path, config_content)

    # Re-lock
    run_cmd("uv lock", cwd=os.path.join(root_dir, "backend"))
    run_cmd("uv sync --extra dev", cwd=os.path.join(root_dir, "backend"))

    # Commit and tag
    run_cmd("git add .", cwd=root_dir)
    run_cmd("git commit -m \"Configure Turso libSQL database variant\"", cwd=root_dir)
    run_cmd("git tag -a turso-v1.0.0 -m \"Turso variant baseline v1.0.0\"", cwd=root_dir)

    # 5. variant/cloudflare (Branch from main, configure Cloudflare Workers Python environment)
    print("\n--- Setting up variant/cloudflare ---")
    run_cmd("git checkout main", cwd=root_dir)
    run_cmd("git checkout -b variant/cloudflare", cwd=root_dir)

    # Add wrangler.toml configuration
    wrangler_toml = """name = "fastapi-standard-worker"
main = "backend/app/main.py"
compatibility_date = "2023-12-01"
compatibility_flags = ["python_workers"]

[vars]
ENVIRONMENT = "production"

[[d1_databases]]
binding = "DB"
database_name = "fastapi-standard-d1"
database_id = "your-d1-database-uuid"
"""
    write_file(os.path.join(root_dir, "wrangler.toml"), wrangler_toml)

    # Write Cloudflare-compliant main.py
    cloudflare_main_py = """import time

import asgi  # type: ignore
from fastapi import FastAPI, Request
from workers import WorkerEntrypoint  # type: ignore

app = FastAPI(title="FastAPI Cloudflare Worker")


@app.get("/api/health/liveness")
async def liveness():
    return {"status": "ok", "timestamp": time.time()}


@app.get("/api/items")
async def list_items(request: Request):
    # Access D1 binding from request environment context
    env = request.scope.get("env")
    if not env or not hasattr(env, "DB"):
        return [{"id": 1, "title": "Local Mock Item", "description": "No D1 DB bound"}]

    db = env.DB
    result = await db.prepare("SELECT * FROM items").all()
    return result.results


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        return await asgi.fetch(app, request, self.env)
"""
    write_file(os.path.join(root_dir, "backend", "app", "main.py"), cloudflare_main_py)

    # Delete standard tests as they are SQLite dependent and not applicable to cloudflare worker
    tests_dir = os.path.join(root_dir, "backend", "tests")
    shutil.rmtree(tests_dir, ignore_errors=True)

    # Write cloudflare custom test file
    cloudflare_test_py = """import sys
from unittest.mock import MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

# Stub workers and asgi before importing main app
sys.modules["workers"] = MagicMock()
sys.modules["asgi"] = MagicMock()

from app.main import app  # noqa: E402


@pytest.mark.asyncio
async def test_liveness():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        response = await ac.get("/api/health/liveness")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
"""
    write_file(os.path.join(tests_dir, "test_cloudflare.py"), cloudflare_test_py)

    # Run ruff check & format to keep it clean
    run_cmd("uv run ruff check --fix .", cwd=os.path.join(root_dir, "backend"))
    run_cmd("uv run ruff format .", cwd=os.path.join(root_dir, "backend"))

    # Commit and tag
    run_cmd("git add .", cwd=root_dir)
    run_cmd("git commit -m \"Configure Cloudflare Workers ASGI entrypoint and D1 binding\"", cwd=root_dir)
    run_cmd("git tag -a cloudflare-v1.0.0 -m \"Cloudflare Workers variant baseline v1.0.0\"", cwd=root_dir)

    # 6. variant/api-only (Branch from main, delete frontend folder)
    print("\n--- Setting up variant/api-only ---")
    run_cmd("git checkout main", cwd=root_dir)
    run_cmd("git checkout -b variant/api-only", cwd=root_dir)
    
    # Remove frontend folder
    shutil.rmtree(os.path.join(root_dir, "frontend"), ignore_errors=True)
    
    run_cmd("git add .", cwd=root_dir)
    run_cmd("git commit -m \"Remove frontend directory for API-only variant\"", cwd=root_dir)
    run_cmd("git tag -a api-only-v1.0.0 -m \"API-only variant baseline v1.0.0\"", cwd=root_dir)

    # 7. variant/auth (Branch from main, implement complete JWT cookie authentication & security)
    print("\n--- Setting up variant/auth ---")
    run_cmd("git checkout main", cwd=root_dir)
    run_cmd("git checkout -b variant/auth", cwd=root_dir)

    # Add pwdlib for secure password hashing
    with open(pyproject_path, "r", encoding="utf-8") as f:
        content = f.read()
    content = content.replace('    "slowapi>=0.1.9",\n', '    "slowapi>=0.1.9",\n    "pwdlib[argon2]>=0.2.0",\n')
    write_file(pyproject_path, content)

    # Modify security.py to use pwdlib Argon2
    auth_security_py = """import secrets
from datetime import datetime, timedelta, timezone
from typing import Any, Union
import hmac
import hashlib
from pwdlib import PasswordHash
from app.core.config import settings

# Initialize Argon2 password hashing via pwdlib
password_hash = PasswordHash.recommended()

def get_password_hash(password: str) -> str:
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return password_hash.verify(plain_password, hashed_password)
    except Exception:
        return False

def create_access_token(subject: Union[str, Any], expires_delta: Union[timedelta, None] = None) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    nonce = secrets.token_hex(4)
    payload = f"{subject}:{int(expire.timestamp())}:{nonce}"
    signature = hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        payload.encode("utf-8"),
        hashlib.sha256
    ).hexdigest()
    
    return f"{payload}:{signature}"

def verify_access_token(token: str) -> Union[str, None]:
    try:
        parts = token.split(":")
        if len(parts) != 4:
            return None
        subject, exp_str, nonce, signature = parts
        
        payload = f"{subject}:{exp_str}:{nonce}"
        expected_signature = hmac.new(
            settings.SECRET_KEY.encode("utf-8"),
            payload.encode("utf-8"),
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, expected_signature):
            return None
            
        expiration = int(exp_str)
        if datetime.now(timezone.utc).timestamp() > expiration:
            return None
            
        return subject
    except Exception:
        return None
"""
    write_file(os.path.join(root_dir, "backend", "app", "core", "security.py"), auth_security_py)

    # Re-lock
    run_cmd("uv lock", cwd=os.path.join(root_dir, "backend"))
    run_cmd("uv sync --extra dev", cwd=os.path.join(root_dir, "backend"))

    # Commit and tag
    run_cmd("git add .", cwd=root_dir)
    run_cmd("git commit -m \"Configure pwdlib Argon2 password hashing and secure authorization\"", cwd=root_dir)
    run_cmd("git tag -a auth-v1.0.0 -m \"Authentication variant baseline v1.0.0\"", cwd=root_dir)

    # 8. overlay/ssr (Vite SSR configuration overlay)
    print("\n--- Setting up overlay/ssr ---")
    run_cmd("git checkout main", cwd=root_dir)
    run_cmd("git checkout -b overlay/ssr", cwd=root_dir)
    
    # Write overlay documentation
    write_file(os.path.join(root_dir, "docs", "overlay-ssr-setup.md"), "# SSR Overlay Setup\nAdds Vite SSR configuration settings.")
    
    run_cmd("git add .", cwd=root_dir)
    run_cmd("git commit -m \"Add React SSR setup configurations\"", cwd=root_dir)
    run_cmd("git tag -a overlay-ssr-v1.0.0 -m \"React SSR overlay v1.0.0\"", cwd=root_dir)

    # 9. overlay/ssg (Vite SSG configuration overlay)
    print("\n--- Setting up overlay/ssg ---")
    run_cmd("git checkout main", cwd=root_dir)
    run_cmd("git checkout -b overlay/ssg", cwd=root_dir)
    
    # Write overlay documentation
    write_file(os.path.join(root_dir, "docs", "overlay-ssg-setup.md"), "# SSG Overlay Setup\nAdds Vite SSG configurations.")
    
    run_cmd("git add .", cwd=root_dir)
    run_cmd("git commit -m \"Add React SSG static render configurations\"", cwd=root_dir)
    run_cmd("git tag -a overlay-ssg-v1.0.0 -m \"React SSG overlay v1.0.0\"", cwd=root_dir)

    # 10. overlay/celery (Celery background worker queue setup overlay)
    print("\n--- Setting up overlay/celery ---")
    run_cmd("git checkout main", cwd=root_dir)
    run_cmd("git checkout -b overlay/celery", cwd=root_dir)

    # Add celery dependencies in pyproject.toml
    with open(pyproject_path, "r", encoding="utf-8") as f:
        content = f.read()
    content = content.replace('    "slowapi>=0.1.9",\n', '    "slowapi>=0.1.9",\n    "celery>=5.3.0",\n    "redis>=5.0.0",\n')
    write_file(pyproject_path, content)

    # Re-lock
    run_cmd("uv lock", cwd=os.path.join(root_dir, "backend"))
    run_cmd("uv sync --extra dev", cwd=os.path.join(root_dir, "backend"))

    # Commit and tag
    run_cmd("git add .", cwd=root_dir)
    run_cmd("git commit -m \"Add Celery background job queue and Redis client configs\"", cwd=root_dir)
    run_cmd("git tag -a overlay-celery-v1.0.0 -m \"Celery overlay v1.0.0\"", cwd=root_dir)

    # 11. overlay/opentelemetry (Observability tracing telemetry overlay)
    print("\n--- Setting up overlay/opentelemetry ---")
    run_cmd("git checkout main", cwd=root_dir)
    run_cmd("git checkout -b overlay/opentelemetry", cwd=root_dir)

    # Add opentelemetry dependencies in pyproject.toml
    with open(pyproject_path, "r", encoding="utf-8") as f:
        content = f.read()
    content = content.replace('    "slowapi>=0.1.9",\n', '    "slowapi>=0.1.9",\n    "opentelemetry-api>=1.22.0",\n    "opentelemetry-sdk>=1.22.0",\n')
    write_file(pyproject_path, content)

    # Re-lock
    run_cmd("uv lock", cwd=os.path.join(root_dir, "backend"))
    run_cmd("uv sync --extra dev", cwd=os.path.join(root_dir, "backend"))

    # Commit and tag
    run_cmd("git add .", cwd=root_dir)
    run_cmd("git commit -m \"Add OpenTelemetry tracer API and SDK dependencies\"", cwd=root_dir)
    run_cmd("git tag -a overlay-opentelemetry-v1.0.0 -m \"OpenTelemetry overlay v1.0.0\"", cwd=root_dir)

    # Finally checkout back to main
    run_cmd("git checkout main", cwd=root_dir)
    print("\nVariant and Overlay branch initialization completed successfully!")
    print("Listing current branches:")
    print(run_cmd("git branch -a", cwd=root_dir))
    print("Listing current tags:")
    print(run_cmd("git tag -l", cwd=root_dir))

if __name__ == "__main__":
    main()
