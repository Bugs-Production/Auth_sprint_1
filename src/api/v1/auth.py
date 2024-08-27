from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from api.auth_utils import decode_refresh_token
from schemas.auths import AuthOutputSchema, RefreshInputSchema
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


@router.post(
    "/refresh",
    response_model=AuthOutputSchema,
)
async def refresh(
    request_data: RefreshInputSchema,
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service),
):
    token_data = decode_refresh_token(request_data.refresh_token)

    if not await auth_service.is_refresh_token_valid(request_data.refresh_token):
        raise HTTPException(status_code=HTTPStatus.FORBIDDEN)

    user_id = token_data["user_id"]

    user_roles = [x.title for x in await user_service.get_user_roles(user_id)]
    refresh_token, access_token = await auth_service.update_refresh_token(
        user_id,
        request_data.refresh_token,
        user_roles,
    )

    return AuthOutputSchema(access_token=access_token, refresh_token=refresh_token)
