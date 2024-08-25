from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from api.v1.models import User
from services.user import UserService, get_user_service

router = APIRouter()


@router.get("/{user_id}", response_model=User)
async def user_info(
    user_id: UUID, user_service: UserService = Depends(get_user_service)
):
    # TODO: провалидировать uuid
    user = await user_service.get_user_info(user_id)

    if not user:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="user not found")

    return user
