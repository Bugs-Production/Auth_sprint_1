from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_pagination import Page, paginate
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from db.postgres import get_db
from schemas.roles import RoleCreateSchema, RolesSchema
from services.role import RolesService

router = APIRouter()


@router.get(
    "/",
    response_model=Page[RolesSchema],
    summary="Список ролей",
    description="Cписок ролей с пагинацией. Размер страницы задается пользователем.",
    response_description="Список ролей",
)
async def roles(
    db: AsyncSession = Depends(get_db),
) -> Page[RolesSchema]:
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
                    "example": {"detail": "Role with title already exists."}
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
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role with title already exists",
        )
