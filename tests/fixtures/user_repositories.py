import urllib.request
from datetime import datetime, timezone
from typing import Any, Generator

import pytest

from lta.api.configuration import (
    get_firebase_app,
    get_firestore_client,
    get_project_name,
)
from lta.domain.user import Device, DeviceOS, User, UserNotificationInfo
from lta.domain.user_repository import UserRepository
from lta.infra.repositories.firestore.user_repository import FirestoreUserRepository
from lta.infra.repositories.memory.user_repository import InMemoryUserRepository


@pytest.fixture()
def sample_user_1() -> User:
    return User(
        id="user1",
        email_address="user1@idontexist.net",
        created_at=datetime(2022, 1, 1, tzinfo=timezone.utc),
        notification_info=UserNotificationInfo(
            phone_number="123",
            email_address="user1@idontexist.net",
            devices=[
                Device(
                    token="user1_device1",
                    os=DeviceOS.ANDROID,
                    version="1",
                    connections=[datetime(2024, 1, 1, tzinfo=timezone.utc)],
                ),
                Device(
                    token="user1_device2",
                    os=DeviceOS.IOS,
                    version="1",
                    connections=[datetime(2024, 1, 1, tzinfo=timezone.utc)],
                ),
            ],
        ),
    )


@pytest.fixture()
def sample_user_2() -> User:
    return User(
        id="user2",
        email_address="user2@idontexist.net",
        created_at=datetime(2022, 2, 2, tzinfo=timezone.utc),
        notification_info=UserNotificationInfo(
            email_address="user2@idontexist.net",
            devices=[
                Device(
                    token="user2_device1",
                    os=DeviceOS.ANDROID,
                    version="1",
                    connections=[datetime(2024, 1, 1, tzinfo=timezone.utc)],
                ),
            ],
        ),
    )


@pytest.fixture()
def sample_user_3() -> User:
    return User(
        id="user3",
        email_address="user3@idontexist.net",
        created_at=datetime(2022, 3, 3, tzinfo=timezone.utc),
        notification_info=UserNotificationInfo(),
    )


@pytest.fixture()
def prefilled_memory_user_repository(
    sample_user_1: User,
    sample_user_2: User,
    sample_user_3: User,
) -> UserRepository:
    return InMemoryUserRepository(
        {
            "user1": sample_user_1,
            "user2": sample_user_2,
            "user3": sample_user_3,
        }
    )


@pytest.fixture
def empty_firestore_user_repository() -> Generator[UserRepository, None, None]:
    get_firebase_app()
    yield FirestoreUserRepository(get_firestore_client(use_emulator=True))
    request = urllib.request.Request(
        f"http://localhost:8080/emulator/v1/projects/{get_project_name()}/databases/(default)/documents",
        method="DELETE",
    )
    resp = urllib.request.urlopen(request)
    if resp.status != 200:
        raise RuntimeError("Failed to delete Firestore emulator data")


@pytest.fixture
def empty_memory_user_repository() -> UserRepository:
    return InMemoryUserRepository()


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
