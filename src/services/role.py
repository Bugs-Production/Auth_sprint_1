from abc import ABC, abstractmethod
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.roles import Role
from schemas.roles import RoleCreateSchema, RoleSchema


class AbstractRoleService(ABC):
    @abstractmethod
    async def get_roles_list(self) -> Role | None:
        pass

    @abstractmethod
    async def create_role(self, role: RoleCreateSchema) -> Role:
        pass

    @abstractmethod
    async def delete_role(self, role_id: str) -> None:
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

        try:
            self.db.add(new_role)
            await self.db.commit()
            await self.db.refresh(new_role)
            return new_role
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Role with title {role.title} already exists",
            )

    async def delete_role(self, role_id: str) -> None:
        """Удаление роли"""
        role_uuid = UUID(role_id)

        # находим запись по id
        result = await self.db.execute(select(Role).filter_by(id=role_uuid))
        role = result.scalars().first()

        if role is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found.",
            )

        await self.db.delete(role)
        await self.db.commit()
