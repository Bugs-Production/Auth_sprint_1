from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException

from api.auth_utils import decode_token_or_401
from schemas.auths import (AuthOutputSchema, LoginInputSchema,
                           RefreshInputSchema)
from schemas.users import CreateUserSchema
from services.auth import AuthService, get_auth_service
from services.exceptions import ConflictError, ObjectNotFoundError
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

    user_id = str(user.id)
    user_roles = [x.title for x in await user_service.get_user_roles(user_id)]

    access_token = await auth_service.generate_access_token(user_id, user_roles)
    refresh_token = await auth_service.emit_refresh_token(user_id)

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
    token_data = decode_token_or_401(request_data.refresh_token)

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


@router.post(
    "/login",
    response_model=AuthOutputSchema,
)
async def login(
    login_data: LoginInputSchema,
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service),
):
    try:
        user = await user_service.get_user_by_login(login_data.login)
    except ObjectNotFoundError:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="user not found")

    if not user.check_password(login_data.password):
        raise HTTPException(HTTPStatus.BAD_REQUEST, detail="invalid password")

    user_id = str(user.id)

    user_roles = [x.title for x in await user_service.get_user_roles(user_id)]

    access_token = await auth_service.generate_access_token(user_id, user_roles)
    refresh_token = await auth_service.emit_refresh_token(user_id)

    return AuthOutputSchema(access_token=access_token, refresh_token=refresh_token)


@router.post("/logout", status_code=200)
async def logout(
    request_data: RefreshInputSchema,
    auth_service: AuthService = Depends(get_auth_service),
):
    await auth_service.invalidate_refresh_token(request_data.refresh_token)
    return {"detail": "logout success"}


@router.post("/logout/all", status_code=200)
async def logout(
    request_data: RefreshInputSchema,
    auth_service: AuthService = Depends(get_auth_service),
):
    token_data = decode_token_or_401(request_data.refresh_token)

    await auth_service.invalidate_user_refresh_tokens(
        token_data["user_id"], request_data.refresh_token
    )
    return {"detail": "logout from all other devices success"}
