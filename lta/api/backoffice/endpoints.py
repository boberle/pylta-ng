from __future__ import annotations

from fastapi import APIRouter, Depends
from pydantic import BaseModel, EmailStr

from lta.api.configuration import AppConfiguration, get_configuration
from lta.domain.user import User

router = APIRouter()


class UserItemResponse(BaseModel):
    id: str
    email_address: EmailStr

    @staticmethod
    def from_domain(user: User) -> UserItemResponse:
        return UserItemResponse(id=user.id, email_address=user.email_address)


class UserListResponse(BaseModel):
    users: list[UserItemResponse]


@router.get("/users/")
async def get_users(
    configuration: AppConfiguration = Depends(get_configuration),
) -> UserListResponse:
    users = configuration.user_repository.list_users()
    return UserListResponse(
        users=[UserItemResponse.from_domain(user) for user in users]
    )


class UserResponse(BaseModel):
    id: str
    email_address: EmailStr

    @staticmethod
    def from_domain(user: User) -> UserResponse:
        return UserResponse(id=user.id, email_address=user.email_address)


@router.get("/users/{id:str}/")
async def get_user(
    id: str,
    configuration: AppConfiguration = Depends(get_configuration),
) -> UserResponse:
    user = configuration.user_repository.get_user(id)
    return UserResponse.from_domain(user)
