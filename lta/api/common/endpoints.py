from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel

from lta.authentication import (
    AuthenticatedUser,
    change_user_password,
    get_authenticated_user,
)

router = APIRouter()


class ChangePasswordRequest(BaseModel):
    new_password: str


def get_authenticated_user_with_default_password_allowed(
    request: Request,
) -> AuthenticatedUser:
    return get_authenticated_user(request, allow_default_password_user=True)


@router.post("/change-password/")
def change_password(
    r: ChangePasswordRequest,
    user: AuthenticatedUser = Depends(
        get_authenticated_user_with_default_password_allowed
    ),
) -> None:
    change_user_password(user, "", r.new_password)
