from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = None


class UserRead(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    is_active: bool
    is_superuser: bool


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str | None = None
