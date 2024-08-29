from http import HTTPStatus
from typing import Annotated, Any
from uuid import UUID

import jwt
from fastapi import Header, HTTPException

from core.config import JWT_ALGORITHM, settings


def authenticate_user(
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, Any]:
    token = authorization.replace("Bearer ", "")
    return decode_token_or_401(token)


def decode_token_or_401(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[JWT_ALGORITHM])
    except jwt.exceptions.InvalidTokenError:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token")

    return payload


def check_allow_affect_user(auth_data: dict[str, Any], user_id: UUID):
    """
    Проверяет может ли пользователь, отправивший запрос,
    производить операции над пользователем с id=user_id
    """
    if "admin" not in auth_data["roles"] and str(user_id) != auth_data["user_id"]:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN)


def check_admin(auth_data: dict[str, Any]):
    """Проверяет что только админ может получить доступ к endpoints"""
    if "admin" not in auth_data["roles"]:
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN)
