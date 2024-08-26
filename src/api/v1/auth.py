from http import HTTPStatus
from typing import Annotated, Any

import jwt
from fastapi import HTTPException, Header


def authenticate_user(
    authorization: Annotated[str | None, Header()] = None,
) -> dict[str, Any]:
    token = authorization.replace("Bearer ", "")
    secret_key = "auth_secret_key"
    try:
        payload = jwt.decode(token, secret_key, algorithms=["HS256"])
    except jwt.exceptions.InvalidTokenError:
        raise HTTPException(status_code=HTTPStatus.UNAUTHORIZED, detail="invalid token")

    return payload
