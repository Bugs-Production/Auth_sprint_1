from datetime import datetime, timedelta
from functools import lru_cache

import jwt
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

import models as db_models
from core.config import settings
from db.postgres import get_postgres_session

JWT_ALGORITHM = "HS256"


class AuthService:
    def __init__(self, postgres_session: AsyncSession):
        self.postgres_session = postgres_session

    @staticmethod
    async def generate_access_token(user_id: str, user_roles: list[str]) -> str:
        valid_till = datetime.now() + timedelta(hours=settings.access_token_exp_hours)
        payload = {
            "user_id": user_id,
            "exp": int(valid_till.timestamp()),
            "roles": user_roles,
        }

        return jwt.encode(payload, settings.jwt_secret_key, algorithm=JWT_ALGORITHM)

    @staticmethod
    def _generate_refresh_token(user_id: str, valid_till: datetime) -> str:
        payload = {
            "user_id": user_id,
            "exp": int(valid_till.timestamp()),
        }

        return jwt.encode(payload, settings.jwt_secret_key, algorithm=JWT_ALGORITHM)

    async def save_refresh_token(
        self, user_id: str, refresh_token: str, valid_till: datetime
    ) -> None:
        async with self.postgres_session() as session:
            refresh_token = db_models.RefreshToken(
                user_id=user_id,
                token=refresh_token,
                expires_at=valid_till,
            )
            session.add(refresh_token)

            await session.commit()

    async def emit_refresh_token(self, user_id: str) -> str:
        valid_till = datetime.now() + timedelta(days=settings.refresh_token_exp_days)

        refresh_token = self._generate_refresh_token(user_id, valid_till)

        await self.save_refresh_token(user_id, refresh_token, valid_till)

        return refresh_token


@lru_cache()
def get_auth_service(
    postgres_session: AsyncSession = Depends(get_postgres_session),
) -> AuthService:
    return AuthService(postgres_session)
