from http import HTTPStatus
from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from api.v1.models import User
from api.v1.auth import authenticate_user
from services.user import UserService, get_user_service

router = APIRouter()


@router.get("/me", response_model=User)
async def user_info(
    user_data: dict[str, Any] = Depends(authenticate_user),
    user_service: UserService = Depends(get_user_service),
):

    user_id = user_data["user_id"]

    user = await user_service.get_user_info(user_id)

    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="user not found")

    return user
