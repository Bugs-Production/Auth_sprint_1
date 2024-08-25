from uuid import UUID, uuid4

from pydantic import BaseModel, Field, EmailStr


class User(BaseModel):
    id: UUID = Field(default_factory=uuid4, serialization_alias="uuid")
    login: str
    first_name: str | None
    last_name: str | None
    email: EmailStr | None

    class Config:
        from_attributes = True
