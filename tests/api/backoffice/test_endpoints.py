import pytest
from fastapi.testclient import TestClient

import lta.api.app
from lta.api.configuration import AppConfiguration, get_configuration
from lta.authentication import AuthenticatedUser, get_admin_user
from lta.domain.user_repository import UserRepository


@pytest.fixture
def test_client(prefilled_memory_user_repository: UserRepository) -> TestClient:

    class TestAppConfiguration(AppConfiguration):

        @property
        def user_repository(self) -> UserRepository:
            return prefilled_memory_user_repository

    def override_get_configuration() -> TestAppConfiguration:
        return TestAppConfiguration()

    def override_get_admin_user() -> AuthenticatedUser:
        return AuthenticatedUser(id="admin_user", email_address="admin@idontexist.net")

    app = lta.api.app.app
    app.dependency_overrides[get_configuration] = override_get_configuration
    app.dependency_overrides[get_admin_user] = override_get_admin_user
    return TestClient(app)


def test_list_users(test_client: TestClient) -> None:
    response = test_client.get("/api/v1/users/")
    assert response.status_code == 200
    assert response.json() == {
        "users": [
            {
                "email_address": "user1@idontexist.net",
                "id": "user1",
                "created_at": "2022-01-01T00:00:00Z",
            },
            {
                "email_address": "user2@idontexist.net",
                "id": "user2",
                "created_at": "2022-02-02T00:00:00Z",
            },
            {
                "email_address": "user3@idontexist.net",
                "id": "user3",
                "created_at": "2022-03-03T00:00:00Z",
            },
        ]
    }


def test_get_user(test_client: TestClient) -> None:
    response = test_client.get("/api/v1/users/user1/")
    assert response.status_code == 200
    assert response.json() == {
        "email_address": "user1@idontexist.net",
        "id": "user1",
        "created_at": "2022-01-01T00:00:00Z",
        "devices": [
            {
                "last_connection": "2024-01-02T00:00:00Z",
                "token": "user1_device1",
            },
            {
                "last_connection": "2024-01-03T00:00:00Z",
                "token": "user1_device2",
            },
        ],
    }
