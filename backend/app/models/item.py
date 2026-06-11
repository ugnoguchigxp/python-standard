from sqlmodel import Field, SQLModel


class Item(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(index=True, nullable=False)
    description: str | None = Field(default=None)
    owner_id: int | None = Field(default=None, foreign_key="user.id")
