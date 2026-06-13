from typing import Any
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
