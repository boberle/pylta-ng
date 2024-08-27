from datetime import datetime

import pytest

from lta.domain.user import Device, DeviceOS
from lta.domain.user_repository import UserNotFound, UserRepository
from lta.infra.repositories.memory.user_repository import InMemoryUserRepository


@pytest.fixture
def user_repo() -> UserRepository:
    return InMemoryUserRepository(users={})


def test_get_all_users(user_repo: UserRepository) -> None:
    user1 = user_repo.create_user("user1")
    user2 = user_repo.create_user("user2")
    users = user_repo.list_users()
    assert len(users) == 2
    assert user1 in users
    assert user2 in users


def test_get_device_registrations_from_user_id(user_repo: UserRepository) -> None:
    user_repo.create_user("user1")
    device1 = Device(
        token="device1_token",
        os=DeviceOS.ANDROID,
        version="1",
        connection=datetime.now(),
    )
    device2 = Device(
        token="device2_token",
        os=DeviceOS.ANDROID,
        version="1",
        connection=datetime.now(),
    )
    user_repo.set_device_registration("user1", device1)
    user_repo.set_device_registration("user1", device2)

    user_repo.create_user("user2")
    device3 = Device(
        token="device3_token",
        os=DeviceOS.ANDROID,
        version="1",
        connection=datetime.now(),
    )
    device4 = Device(
        token="device4_token",
        os=DeviceOS.ANDROID,
        version="1",
        connection=datetime.now(),
    )
    user_repo.set_device_registration("user2", device3)
    user_repo.set_device_registration("user2", device4)

    devices = user_repo.get_device_registrations_from_user_id("user1")
    assert len(devices) == 2
    assert device1 in devices
    assert device2 in devices

    devices = user_repo.get_device_registrations_from_user_id("user2")
    assert len(devices) == 2
    assert device3 in devices
    assert device4 in devices


def test_get_user(user_repo: UserRepository) -> None:
    user_repo.create_user("user1")
    exp = user_repo.create_user("user2")
    got = user_repo.get_user("user2")
    assert exp == got


def test_get_user_not_found(user_repo: UserRepository) -> None:
    with pytest.raises(UserNotFound):
        user_repo.get_user("nonexistent_user")


def test_set_device_registration(user_repo: UserRepository) -> None:
    user_repo.create_user("user1")
    device = Device(
        token="device1_token",
        os=DeviceOS.ANDROID,
        version="1",
        connection=datetime.now(),
    )
    user_repo.set_device_registration("user1", device)
    assert device in user_repo.get_device_registrations_from_user_id("user1")


def test_create_user(user_repo: UserRepository) -> None:
    user = user_repo.create_user("user1")
    assert user.id == "user1"
    assert user_repo.exists("user1")


def test_create_user__should_not_add_user_twice(user_repo: UserRepository) -> None:
    user_repo.create_user("user1")
    assert len(user_repo.list_users()) == 1
    user_repo.create_user("user1")
    assert len(user_repo.list_users()) == 1


def test_exists(user_repo: UserRepository) -> None:
    user_repo.create_user("user1")
    assert user_repo.exists("user1")
    assert not user_repo.exists("nonexistent_user")
