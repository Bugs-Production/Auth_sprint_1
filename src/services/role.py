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

    @abstractmethod
    async def change_role(self, role: RoleCreateSchema, role_id: str) -> Role:
        pass

    @abstractmethod
    async def get_role_by_id(self, role_id: str) -> Role:
        pass


class RolesService(AbstractRoleService):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_role_by_id(self, role_id: str) -> Role:
        """Поиск роли по id"""
        role_uuid = UUID(role_id)

        result = await self.db.execute(select(Role).filter_by(id=role_uuid))
        role = result.scalars().first()

        return role

    async def get_roles_list(self) -> Role | None:
        """Получение всех ролей"""
        result = await self.db.execute(select(Role))
        return result.scalars().all()

    async def create_role(self, role: RoleCreateSchema) -> Role | HTTPException:
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
        role = await self.get_role_by_id(role_id)

        if role is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found.",
            )

        await self.db.delete(role)
        await self.db.commit()

    async def change_role(
        self, role: RoleCreateSchema, role_id: str
    ) -> Role | HTTPException:
        """Изменение роли"""
        old_role = await self.get_role_by_id(role_id)

        if old_role is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Role not found.",
            )

        if old_role.title == role.title:
            return old_role

        old_role.title = role.title

        self.db.add(old_role)
        await self.db.commit()
        await self.db.refresh(old_role)

        return old_role
