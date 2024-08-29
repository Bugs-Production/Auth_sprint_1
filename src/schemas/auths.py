from pydantic import BaseModel


class AuthOutputSchema(BaseModel):
    access_token: str
    refresh_token: str


class RefreshInputSchema(BaseModel):
    refresh_token: str
    access_token: str


class LoginInputSchema(BaseModel):
    login: str
    password: str
