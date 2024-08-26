from pydantic import BaseModel

from schemas.mixins import IdMixin


class RolesSchema(IdMixin):
    title: str


class RoleCreateSchema(BaseModel):
    title: str
