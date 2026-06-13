from typing import Optional, Any
from sqlmodel import Field, SQLModel, Column
from pgvector.sqlalchemy import Vector

class Document(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str = Field(nullable=False)
    embedding: Any = Field(sa_column=Column(Vector(1536))) # 1536-dim vector
