from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr

from lta.api.configuration import AppConfiguration, get_configuration
from lta.authentication import get_admin_user
from lta.domain.user import User
from lta.domain.user_repository import UserNotFound

router = APIRouter()


class UserItemResponse(BaseModel):
    id: str
    email_address: EmailStr
    created_at: datetime

    @staticmethod
    def from_domain(user: User) -> UserItemResponse:
        return UserItemResponse(
            id=user.id, email_address=user.email_address, created_at=user.created_at
        )


class UserListResponse(BaseModel):
    users: list[UserItemResponse]


@router.get("/users/")
async def get_users(
    configuration: AppConfiguration = Depends(get_configuration),
    admin_id: str = Depends(get_admin_user),
) -> UserListResponse:
    users = configuration.user_repository.list_users()
    return UserListResponse(
        users=[UserItemResponse.from_domain(user) for user in users]
    )


class Device(BaseModel):
    token: str
    last_connection: datetime | None


class UserResponse(BaseModel):
    id: str
    email_address: EmailStr
    created_at: datetime
    devices: list[Device]

    @staticmethod
    def from_domain(user: User) -> UserResponse:
        return UserResponse(
            id=user.id,
            email_address=user.email_address,
            created_at=user.created_at,
            devices=[
                Device(token=device.token, last_connection=device.last_connection)
                for device in user.devices
            ],
        )


@router.get("/users/{id:str}/")
async def get_user(
    id: str,
    configuration: AppConfiguration = Depends(get_configuration),
) -> UserResponse:
    try:
        user = configuration.user_repository.get_user(id)
    except UserNotFound:
        raise HTTPException(status_code=404)
    return UserResponse.from_domain(user)
