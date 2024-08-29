from http import HTTPStatus
from typing import Annotated, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi_pagination import Page, paginate

from api.auth_utils import check_admin, decode_token, oauth2_scheme
from schemas.roles import RoleSchema, RoleUpdateSchema
from services.admin import AdminService, get_admin_service
from services.auth import AuthService, get_auth_service
from services.exceptions import ConflictError, ObjectNotFoundError

router = APIRouter()


@router.get(
    "/{user_id}/roles",
    response_model=Page[RoleSchema],
    summary="Информация по ролям пользователя",
    response_description="Информация по ролям пользователя",
    responses={
        HTTPStatus.NOT_FOUND: {
            "description": "Пользователь не найден",
            "content": {"application/json": {"example": {"detail": "user not found"}}},
        },
        HTTPStatus.UNAUTHORIZED: {
            "description": "Ошибка валидации токена",
            "content": {"application/json": {"example": {"detail": "invalid token"}}},
        },
        HTTPStatus.FORBIDDEN: {
            "description": "Доступ запрещен",
            "content": {"application/json": {"example": {"detail": "Forbidden"}}},
        },
    },
)
async def get_user_roles(
    user_id: UUID,
    access_token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: AuthService = Depends(get_auth_service),
    admin_service: AdminService = Depends(get_admin_service),
):
    payload = decode_token(access_token)
    if not payload:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token")

    check_admin(payload)

    if not auth_service.is_access_token_valid(access_token):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token")
    try:
        roles = await admin_service.get_user_roles(user_id)
        return paginate(roles)
    except ObjectNotFoundError:
        raise HTTPException(
            status_code=HTTPStatus.NOT_FOUND, detail="objects not found"
        )


@router.post(
    "/{user_id}/roles",
    response_model=RoleSchema,
    summary="Добавление новой роли пользователю",
    response_description="Информация по добавленной роли пользователю",
    responses={
        HTTPStatus.NOT_FOUND: {
            "description": "Пользователь не найден",
            "content": {"application/json": {"example": {"detail": "user not found"}}},
        },
        HTTPStatus.UNAUTHORIZED: {
            "description": "Ошибка валидации токена",
            "content": {"application/json": {"example": {"detail": "invalid token"}}},
        },
        HTTPStatus.FORBIDDEN: {
            "description": "Доступ запрещен",
            "content": {"application/json": {"example": {"detail": "Forbidden"}}},
        },
    },
)
async def add_user_role(
    user_id: UUID,
    request_data: RoleUpdateSchema,
    access_token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: AuthService = Depends(get_auth_service),
    admin_service: AdminService = Depends(get_admin_service),
):
    payload = decode_token(access_token)
    if not payload:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token")
    check_admin(payload)

    if not auth_service.is_access_token_valid(access_token):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token")

    try:
        role_id = request_data.role_id
        role = await admin_service.add_user_role(user_id, role_id)
        return role
    except ObjectNotFoundError:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="object not found")
    except ConflictError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT, detail="user already has this role"
        )


@router.delete(
    "/{user_id}/roles",
    response_model=RoleSchema,
    summary="Удаление роли у пользователя",
    response_description="Информация по удалённой роли пользователю",
    responses={
        HTTPStatus.NOT_FOUND: {
            "description": "Пользователь не найден",
            "content": {"application/json": {"example": {"detail": "user not found"}}},
        },
        HTTPStatus.UNAUTHORIZED: {
            "description": "Ошибка валидации токена",
            "content": {"application/json": {"example": {"detail": "invalid token"}}},
        },
        HTTPStatus.FORBIDDEN: {
            "description": "Доступ запрещен",
            "content": {"application/json": {"example": {"detail": "Forbidden"}}},
        },
    },
)
async def remove_user_role(
    user_id: UUID,
    request_data: RoleUpdateSchema,
    access_token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: AuthService = Depends(get_auth_service),
    admin_service: AdminService = Depends(get_admin_service),
):
    payload = decode_token(access_token)
    if not payload:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token")
    check_admin(payload)

    if not auth_service.is_access_token_valid(access_token):
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token")

    try:
        role_id = request_data.role_id
        role = await admin_service.remove_user_role(user_id, role_id)
        return role
    except ObjectNotFoundError:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="object not found")
