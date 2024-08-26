from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page, paginate
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_db
from schemas.roles import RoleCreateSchema, RoleSchema
from services.role import RolesService

router = APIRouter()


@router.get(
    "/",
    response_model=Page[RoleSchema],
    summary="Список ролей",
    description="Cписок ролей с пагинацией. Размер страницы задается пользователем.",
    response_description="Список ролей",
)
async def roles(
    db: AsyncSession = Depends(get_db),
) -> Page[RoleSchema]:
    roles_service = RolesService(db)
    roles_list = await roles_service.get_roles_list()
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
    db: AsyncSession = Depends(get_db),
) -> RoleCreateSchema:
    roles_service = RolesService(db)
    try:
        new_role = await roles_service.create_role(role)
        return new_role
    except HTTPException as e:
        raise e


@router.delete(
    "/{role_id}",
    summary="Удаление роли",
    description="Удаление роли по ee id",
    responses={
        status.HTTP_200_OK: {
            "description": "Успешное удаление.",
            "content": {
                "application/json": {
                    "example": {"detail": "Role deleted successfully."}
                }
            },
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "Отсутствие id у роли.",
            "content": {"application/json": {"example": {"detail": "Role not found."}}},
        },
    },
)
async def delete_roles(
    role_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict:
    roles_service = RolesService(db)
    try:
        await roles_service.delete_role(role_id)
        return {"detail": "Role deleted successfully"}
    except HTTPException as e:
        raise e


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
        status.HTTP_404_NOT_FOUND: {
            "description": "Отсутствие id у роли.",
            "content": {"application/json": {"example": {"detail": "Role not found."}}},
        },
    },
)
async def update_roles(
    role_id: str,
    role: RoleCreateSchema,
    db: AsyncSession = Depends(get_db),
) -> RoleCreateSchema:
    roles_service = RolesService(db)

    try:
        updated_role = await roles_service.change_role(role, role_id)
        return updated_role
    except HTTPException as e:
        raise e
