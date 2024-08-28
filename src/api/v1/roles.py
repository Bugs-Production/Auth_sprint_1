from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page, paginate

from api.auth_utils import authenticate_user, check_admin
from schemas.roles import RoleCreateSchema, RoleSchema
from services.exceptions import (ObjectAlreadyExistsException,
                                 ObjectNotFoundError)
from services.role import RoleService, get_role_service

router = APIRouter()


@router.get(
    "/",
    response_model=Page[RoleSchema],
    summary="Список ролей",
    response_description="Список ролей",
    responses={
        status.HTTP_200_OK: {
            "description": "Успешный запрос.",
            "content": {
                "application/json": {
                    "example": {
                        "items": [
                            {
                                "id": "8f58b17c-283f-4177-9e89-50cbf060504d",
                                "title": "admin",
                            }
                        ]
                    }
                }
            },
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Ошибка валидации токена",
            "content": {"application/json": {"example": {"detail": "invalid token"}}},
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Доступ запрещен",
            "content": {"application/json": {"example": {"detail": "Forbidden"}}},
        },
    },
)
async def roles(
    auth_data: dict[str, Any] = Depends(authenticate_user),
    role_service: RoleService = Depends(get_role_service),
) -> Page[RoleSchema]:
    check_admin(auth_data)

    roles_list = await role_service.get_roles_list()
    return paginate(roles_list)


@router.post(
    "/",
    response_model=RoleCreateSchema,
    summary="Создание новой роли",
    response_description="Подтверждение создания роли",
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": "Конфликт с существующей ролью.",
            "content": {
                "application/json": {
                    "example": {"detail": "Role with title admin already exists."}
                }
            },
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Ошибка валидации токена",
            "content": {"application/json": {"example": {"detail": "invalid token"}}},
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Доступ запрещен",
            "content": {"application/json": {"example": {"detail": "Forbidden"}}},
        },
        status.HTTP_422_UNPROCESSABLE_ENTITY: {
            "description": "Ошибка валидации данных.",
            "content": {
                "application/json": {
                    "example": {"detail": "Input should be a valid string."}
                }
            },
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "Ошибка сервера при обработке запроса.",
            "content": {
                "application/json": {"example": {"detail": "Internal server error"}}
            },
        },
    },
)
async def create_roles(
    role: RoleCreateSchema,
    auth_data: dict[str, Any] = Depends(authenticate_user),
    role_service: RoleService = Depends(get_role_service),
) -> RoleSchema:
    check_admin(auth_data)
    try:
        new_role = await role_service.create_role(role)
        return new_role
    except ObjectAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role with title {role.title} already exists",
        )


@router.delete(
    "/{role_id}",
    summary="Удаление роли",
    response_description="Удаление роли по ee id",
    responses={
        status.HTTP_200_OK: {
            "description": "Успешное удаление.",
            "content": {
                "application/json": {
                    "example": {"detail": "Role deleted successfully."}
                }
            },
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Ошибка валидации токена",
            "content": {"application/json": {"example": {"detail": "invalid token"}}},
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Доступ запрещен",
            "content": {"application/json": {"example": {"detail": "Forbidden"}}},
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Отсутствие id у роли.",
            "content": {"application/json": {"example": {"detail": "Role not found."}}},
        },
    },
)
async def delete_roles(
    role_id: str,
    auth_data: dict[str, Any] = Depends(authenticate_user),
    role_service: RoleService = Depends(get_role_service),
) -> dict:
    check_admin(auth_data)
    try:
        await role_service.delete_role(role_id)
        return {"detail": "Role deleted successfully"}
    except ObjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found.",
        )


@router.put(
    "/{role_id}",
    response_model=RoleCreateSchema,
    summary="Обновление роли",
    response_description="Обновление роли по ee id",
    responses={
        status.HTTP_200_OK: {
            "description": "Успешное изменение.",
            "content": {"application/json": {"example": {"detail": "string"}}},
        },
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Ошибка валидации токена",
            "content": {"application/json": {"example": {"detail": "invalid token"}}},
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Доступ запрещен",
            "content": {"application/json": {"example": {"detail": "Forbidden"}}},
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Отсутствие id у роли.",
            "content": {"application/json": {"example": {"detail": "Role not found."}}},
        },
    },
)
async def update_roles(
    role_id: str,
    role: RoleSchema,
    auth_data: dict[str, Any] = Depends(authenticate_user),
    role_service: RoleService = Depends(get_role_service),
) -> RoleSchema:
    check_admin(auth_data)
    try:
        updated_role = await role_service.change_role(role, role_id)
        return updated_role
    except ObjectNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found.",
        )
