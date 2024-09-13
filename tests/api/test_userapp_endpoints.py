from datetime import datetime, timezone

import pytest
from starlette.testclient import TestClient

import lta.api.app
from lta.api.configuration import get_user_repository
from lta.authentication import AuthenticatedUser, get_authenticated_user
from lta.domain.user import Device, DeviceOS
from lta.domain.user_repository import UserRepository
from lta.infra.repositories.memory.user_repository import InMemoryUserRepository


@pytest.fixture
def test_client(
    prefilled_memory_user_repository: UserRepository,
) -> TestClient:

    def override_get_user_repository() -> UserRepository:
        return prefilled_memory_user_repository

    def override_get_authenticated_user() -> AuthenticatedUser:
        return AuthenticatedUser(id="user1", email_address="user1@idontexist.net")

    app = lta.api.app.app
    app.dependency_overrides[get_user_repository] = override_get_user_repository
    app.dependency_overrides[get_authenticated_user] = override_get_authenticated_user
    return TestClient(app)


def test_register_device(
    test_client: TestClient,
    prefilled_memory_user_repository: InMemoryUserRepository,
) -> None:
    response = test_client.post(
        "/api/mobile/v1/devices/register/",
        json=dict(
            token="user1_device1",
            os="android",
            connection_time=datetime(
                2024, 3, 4, 5, 6, 7, tzinfo=timezone.utc
            ).isoformat(),
        ),
    )
    assert response.status_code == 200

    assert prefilled_memory_user_repository.users["user1"].devices == [
        Device(
            token="user1_device1",
            os=DeviceOS.ANDROID,
            version="1",
            first_connection=datetime(2024, 1, 1, tzinfo=timezone.utc),
            last_connection=datetime(2024, 3, 4, 5, 6, 7, tzinfo=timezone.utc),
        ),
        Device(
            token="user1_device2",
            os=DeviceOS.IOS,
            version="1",
            first_connection=datetime(2024, 1, 1, tzinfo=timezone.utc),
            last_connection=datetime(2024, 1, 3, tzinfo=timezone.utc),
        ),
    ]
