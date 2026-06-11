from typing import Optional
from sqlmodel import Field, SQLModel


class Item(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str = Field(index=True, nullable=False)
    description: Optional[str] = Field(default=None)
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")
