from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr

from lta.api.configuration import AppConfiguration, get_configuration
from lta.authentication import get_admin_user
from lta.domain.assignment import Assignment
from lta.domain.user import DeviceOS, User
from lta.domain.user_repository import UserNotFound

router = APIRouter()


class UserItemResponse(BaseModel):
    id: str
    email_address: EmailStr
    device_oses: list[str]

    @staticmethod
    def from_domain(user: User) -> UserItemResponse:
        return UserItemResponse(
            id=user.id,
            email_address=user.email_address,
            device_oses=[device.os for device in user.notification_info.devices],
        )


class UserListResponse(BaseModel):
    users: list[UserItemResponse]


@router.get("/")
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
    os: DeviceOS
    version: str | None
    connections: list[datetime]


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
                Device(
                    token=device.token,
                    os=device.os,
                    version=device.version,
                    connections=device.connections,
                )
                for device in user.notification_info.devices
            ],
        )


@router.get("/{id:str}/")
async def get_user(
    id: str,
    configuration: AppConfiguration = Depends(get_configuration),
    admin_id: str = Depends(get_admin_user),
) -> UserResponse:
    try:
        user = configuration.user_repository.get_user(id)
    except UserNotFound:
        raise HTTPException(status_code=404)
    return UserResponse.from_domain(user)


class UserAssignmentItemResponse(BaseModel):
    id: str
    title: str
    created_at: datetime
    opened_at: datetime | None
    submitted_at: datetime | None

    @staticmethod
    def from_domain(assignment: Assignment) -> UserAssignmentItemResponse:
        print("BAR:", assignment.submitted_at)
        return UserAssignmentItemResponse(
            id=assignment.id,
            title=assignment.title,
            created_at=assignment.created_at,
            opened_at=max(assignment.opened_at) if assignment.opened_at else None,
            submitted_at=assignment.submitted_at,
        )


class UserAssignmentListResponse(BaseModel):
    assignments: list[UserAssignmentItemResponse]


@router.get("/{id:str}/assignments/")
async def get_user_assignments(
    id: str,
    configuration: AppConfiguration = Depends(get_configuration),
    admin_id: str = Depends(get_admin_user),
) -> UserAssignmentListResponse:
    try:
        assignments = configuration.assignment_repository.list_assignments(id)
    except UserNotFound:
        raise HTTPException(status_code=404)
    return UserAssignmentListResponse(
        assignments=[
            UserAssignmentItemResponse.from_domain(assignment)
            for assignment in assignments
        ]
    )
