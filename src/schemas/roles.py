from pydantic import BaseModel

from schemas.mixins import IdMixin


class RoleSchema(IdMixin):
    title: str


class RoleCreateSchema(BaseModel):
    title: str
