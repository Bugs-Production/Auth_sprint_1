from functools import lru_cache
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

import api.v1.models as pydantic_models
import models as db_models
from db.postgres import get_postgres_session
from services.exceptions import ObjectNotFoundError, ConflictError


class UserService:
    def __init__(self, postgres_session: AsyncSession):
        self.postgres_session = postgres_session

    async def get_user(self, user_id: UUID) -> db_models.User | None:
        async with self.postgres_session() as session:
            results = await session.scalars(
                select(db_models.User).where(db_models.User.id == user_id)
            )
            if not results:
                raise ObjectNotFoundError

            return results.first()

    async def update_user(
        self, user_id: UUID, user_data: pydantic_models.UpdateUserSchema
    ) -> db_models.User | None:
        async with self.postgres_session() as session:
            results = await session.scalars(
                select(db_models.User).where(db_models.User.id == user_id)
            )
            if not results:
                raise ObjectNotFoundError

            user = results.first()

            for field in user_data.model_fields_set:
                val = getattr(user_data, field)
                setattr(user, field, val)

            session.add(user)
            try:
                await session.commit()
            except IntegrityError:
                raise ConflictError

            return user


@lru_cache()
def get_user_service(
    postgres_session: AsyncSession = Depends(get_postgres_session),
) -> UserService:
    return UserService(postgres_session)
