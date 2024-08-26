from functools import lru_cache
from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

import api.v1.models as pydantic_models
import models as db_models
from db.postgres import get_postgres


class UserService:
    def __init__(self, postgres_session: AsyncSession):
        self.postgres_session = postgres_session

    async def get_user_info(self, user_id: UUID) -> pydantic_models.User | None:
        async with self.postgres_session() as session:
            results = await session.scalars(select(db_models.User).where(db_models.User.id == user_id))
            if not results:
                return None
            return results.first()


@lru_cache()
def get_user_service(
    postgres_session: AsyncSession = Depends(get_postgres),
) -> UserService:
    return UserService(postgres_session)
