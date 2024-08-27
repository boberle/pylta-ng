from datetime import datetime

import pytest

from lta.domain.user import Device, DeviceOS, User
from lta.domain.user_repository import UserRepository
from lta.infra.repositories.memory.user_repository import InMemoryUserRepository


@pytest.fixture()
def user_repository() -> UserRepository:
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
