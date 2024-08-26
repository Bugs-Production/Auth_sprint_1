from datetime import datetime, date
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, EmailStr, model_validator


class UserSchema(BaseModel):
    id: UUID = Field(default_factory=uuid4, serialization_alias="uuid")
    login: str
    first_name: str | None
    last_name: str | None
    email: EmailStr | None

    class Config:
        from_attributes = True


class UpdateUserSchema(BaseModel):
    login: str | None = None
    password: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None
    birthdate: date | None = None

    @model_validator(mode="after")
    def check_at_least_one_field_exists(self):
        if not self.model_fields_set:
            raise ValueError("At least one field required")
        return self


class UserLoginHistorySchema(BaseModel):
    event_date: datetime
    success: bool
