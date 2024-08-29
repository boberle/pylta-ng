from typing import Any

from lta.api.configuration import get_firestore_client, get_project_name
from lta.infra.repositories.firestore.user_repository import FirestoreUserRepository

import urllib.request
from datetime import datetime
from typing import Generator

import pytest

from lta.domain.user import Device, DeviceOS, User
from lta.domain.user_repository import UserRepository
from lta.infra.repositories.memory.user_repository import InMemoryUserRepository


@pytest.fixture()
def prefilled_memory_user_repository() -> UserRepository:
    return InMemoryUserRepository(
        {
            "user1": User(
                id="user1",
                email_address="user1@idontexist.net",
                devices=[
                    Device(
                        token="device1",
                        os=DeviceOS.ANDROID,
                        version="1",
                        connection=datetime(2024, 1, 1),
                    ),
                    Device(
                        token="device2",
                        os=DeviceOS.IOS,
                        version="1",
                        connection=datetime(2024, 1, 2),
                    ),
                ],
                created_at=datetime(2022, 1, 1),
            ),
            "user2": User(
                id="user2",
                email_address="user2@idontexist.net",
                devices=[],
                created_at=datetime(2022, 2, 2),
            ),
        }
    )


@pytest.fixture
def empty_firestore_user_repository() -> Generator[UserRepository, None, None]:
    yield FirestoreUserRepository(get_firestore_client())
    request = urllib.request.Request(
        f"http://localhost:8080/emulator/v1/projects/{get_project_name()}/databases/(default)/documents",
        method="DELETE",
    )
    resp = urllib.request.urlopen(request)
    if resp.status != 200:
        raise RuntimeError("Failed to delete Firestore emulator data")


@pytest.fixture
def empty_memory_user_repository() -> UserRepository:
    return InMemoryUserRepository(users={})


@pytest.fixture(params=["memory", "firestore"])
def empty_user_repository(
        request: Any,
        empty_firestore_user_repository: FirestoreUserRepository,
        empty_memory_user_repository: InMemoryUserRepository,
) -> Generator[UserRepository, None, None]:
    if request.param == "firestore":
        yield empty_firestore_user_repository
    else:
        yield empty_memory_user_repository


