from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.roles import Role
from schemas.roles import RoleCreateSchema, RolesSchema


class AbstractRoleService(ABC):
    @abstractmethod
    async def get_roles_list(self) -> Role | None:
        pass

    @abstractmethod
    async def create_role(self, role: RoleCreateSchema) -> Role:
        pass


class RolesService(AbstractRoleService):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_roles_list(self) -> Role | None:
        """Получение всех ролей"""
        result = await self.db.execute(select(Role))
        return result.scalars().all()

    async def create_role(self, role: RoleCreateSchema) -> Role:
        """Создание роли"""
        new_role = Role(title=role.title)
        self.db.add(new_role)
        await self.db.commit()
        await self.db.refresh(new_role)
        return new_role
