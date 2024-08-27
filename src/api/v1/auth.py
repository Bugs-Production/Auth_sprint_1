from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from schemas.auths import AuthOutputSchema
from schemas.users import CreateUserSchema
from services.auth import AuthService, get_auth_service
from services.exceptions import ConflictError
from services.user import UserService, get_user_service

router = APIRouter()


@router.post(
    "/signup",
    response_model=AuthOutputSchema,
)
async def signup(
    user_data: CreateUserSchema,
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service),
):
    try:
        user = await user_service.create_user(user_data)
    except ConflictError:
        raise HTTPException(
            status_code=HTTPStatus.CONFLICT,
            detail="user with this parameters already exists",
        )

    user_roles = await user_service.get_user_roles(user.id)
    user_roles_list = [role.title for role in user_roles]

    access_token = await auth_service.generate_access_token(
        str(user.id), user_roles_list
    )
    refresh_token = await auth_service.emit_refresh_token(str(user.id))

    return AuthOutputSchema(access_token=access_token, refresh_token=refresh_token)
