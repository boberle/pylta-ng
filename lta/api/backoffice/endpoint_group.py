from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from lta.api.configuration import AppConfiguration, get_configuration
from lta.authentication import get_admin_user
from lta.domain.group import Group
from lta.domain.user_repository import UserRepository

router = APIRouter()


class GroupUser(BaseModel):
    id: str
    email: str


class GroupItemResponse(BaseModel):
    id: str
    name: str
    users: list[GroupUser]

    @staticmethod
    def from_domain(user_repository: UserRepository, group: Group) -> GroupItemResponse:
        users = []
        for user_id in group.user_ids:
            user = user_repository.get_user(user_id)
            users.append(GroupUser(id=user.id, email=user.email_address))
        return GroupItemResponse(id=group.id, name=group.name, users=users)


class GroupListResponse(BaseModel):
    groups: list[GroupItemResponse]


@router.get("/")
async def get_groups(
    configuration: AppConfiguration = Depends(get_configuration),
    admin_id: str = Depends(get_admin_user),
) -> GroupListResponse:
    groups = configuration.group_repository.list_groups()
    return GroupListResponse(
        groups=[
            GroupItemResponse.from_domain(configuration.user_repository, group)
            for group in groups
        ]
    )


class GroupCreationRequest(BaseModel):
    name: str
    user_ids: list[str]


@router.post("/")
def post_group(
    request: GroupCreationRequest,
    configuration: AppConfiguration = Depends(get_configuration),
    admin_id: str = Depends(get_admin_user),
) -> None:
    id = str(uuid.uuid4())
    date = datetime.now(tz=timezone.utc)
    configuration.group_repository.create_group(id, request.name, date)
    configuration.group_repository.set_users(id, request.user_ids)


class GroupUpdateRequest(BaseModel):
    user_ids: list[str]


@router.put("/{group_id:str}/")
def put_group(
    group_id: str,
    request: GroupCreationRequest,
    configuration: AppConfiguration = Depends(get_configuration),
    admin_id: str = Depends(get_admin_user),
) -> None:
    configuration.group_repository.set_users(group_id, request.user_ids)


@router.delete("/{group_id:str}/")
def delete_group(
    group_id: str,
    configuration: AppConfiguration = Depends(get_configuration),
    admin_id: str = Depends(get_admin_user),
) -> None:
    configuration.group_repository.remove_group(group_id)
