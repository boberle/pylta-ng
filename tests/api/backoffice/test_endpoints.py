import pytest
from fastapi.testclient import TestClient

import lta.api.app
from lta.api.configuration import AppConfiguration, get_configuration
from lta.domain.user_repository import UserRepository


@pytest.fixture
def test_client(user_repository: UserRepository) -> TestClient:

    class TestAppConfiguration(AppConfiguration):

        @property
        def user_repository(self) -> UserRepository:
            return user_repository

    def override_get_configuration() -> TestAppConfiguration:
        return TestAppConfiguration()

    app = lta.api.app.app
    app.dependency_overrides[get_configuration] = override_get_configuration
    return TestClient(app)


def test_list_users(test_client: TestClient) -> None:
    response = test_client.get("/api/v1/users/")
    assert response.status_code == 200
    assert response.json() == {
        "users": [
            {"email_address": "user1@idontexist.net", "id": "user1"},
            {"email_address": "user2@idontexist.net", "id": "user2"},
        ]
    }


def test_get_user(test_client: TestClient) -> None:
    response = test_client.get("/api/v1/users/user1/")
    assert response.status_code == 200
    assert response.json() == {"email_address": "user1@idontexist.net", "id": "user1"}
