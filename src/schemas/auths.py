from uuid import UUID

from pydantic import BaseModel


class AccessToken(BaseModel):
    user_id: UUID
    exp: int
    roles: list[str]


class RefreshToken(BaseModel):
    user_id: UUID
    exp: int


class AuthOutputSchema(BaseModel):
    access_token: str
    refresh_token: str


class RefreshInputSchema(BaseModel):
    refresh_token: str


class LoginInputSchema(BaseModel):
    login: str
    password: str
