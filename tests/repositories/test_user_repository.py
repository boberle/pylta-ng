from datetime import datetime, timezone

import pytest

from lta.domain.user import Device, DeviceOS, User
from lta.domain.user_repository import UserNotFound, UserRepository


def test_get_all_users(empty_user_repository: UserRepository) -> None:
    user1 = User(
        id="user1",
        email_address="user1@example.com",
        created_at=datetime.now(tz=timezone.utc),
    )
    user2 = User(
        id="user2",
        email_address="user2@example.com",
        created_at=datetime.now(tz=timezone.utc),
    )
    empty_user_repository.create_user(
        id=user1.id, email_address=user1.email_address, created_at=user1.created_at
    )
    empty_user_repository.create_user(
        id=user2.id, email_address=user2.email_address, created_at=user2.created_at
    )
    users = empty_user_repository.list_users()
    assert len(users) == 2
    assert user1 in users
    assert user2 in users


def test_get_device_registrations_from_user_id(
    empty_user_repository: UserRepository,
) -> None:
    empty_user_repository.create_user(
        id="user1",
        email_address="user1@example.com",
        created_at=datetime.now(tz=timezone.utc),
    )
    device1 = Device(
        token="device1_token",
        os=DeviceOS.ANDROID,
        version="1",
        first_connection=datetime.now(tz=timezone.utc),
        last_connection=None,
    )
    device2 = Device(
        token="device2_token",
        os=DeviceOS.ANDROID,
        version="1",
        first_connection=datetime.now(tz=timezone.utc),
        last_connection=None,
    )
    empty_user_repository.add_device_registration(
        "user1", device1.token, device1.os, device1.version, device1.first_connection
    )
    empty_user_repository.add_device_registration(
        "user1", device2.token, device2.os, device2.version, device2.first_connection
    )

    empty_user_repository.create_user(
        "user2",
        email_address="user2@example.com",
        created_at=datetime.now(tz=timezone.utc),
    )
    device3 = Device(
        token="device3_token",
        os=DeviceOS.ANDROID,
        version="1",
        first_connection=datetime.now(tz=timezone.utc),
        last_connection=None,
    )
    device4 = Device(
        token="device4_token",
        os=DeviceOS.ANDROID,
        version="1",
        first_connection=datetime.now(tz=timezone.utc),
        last_connection=None,
    )
    empty_user_repository.add_device_registration(
        "user2", device3.token, device3.os, device3.version, device3.first_connection
    )
    empty_user_repository.add_device_registration(
        "user2", device4.token, device4.os, device4.version, device4.first_connection
    )

    devices = empty_user_repository.get_device_registrations_from_user_id("user1")
    assert len(devices) == 2
    assert device1 in devices
    assert device2 in devices

    devices = empty_user_repository.get_device_registrations_from_user_id("user2")
    assert len(devices) == 2
    assert device3 in devices
    assert device4 in devices


def test_get_user(empty_user_repository: UserRepository) -> None:
    empty_user_repository.create_user(
        "user1", "user1@example.com", datetime.now(tz=timezone.utc)
    )
    exp = User(
        id="user1",
        email_address="user1@example.com",
        created_at=datetime.now(tz=timezone.utc),
    )
    empty_user_repository.create_user(exp.id, exp.email_address, exp.created_at)
    got = empty_user_repository.get_user(exp.id)
    assert exp == got


def test_get_user_not_found(empty_user_repository: UserRepository) -> None:
    with pytest.raises(UserNotFound):
        empty_user_repository.get_user("nonexistent_user")


def test_set_device_registration(empty_user_repository: UserRepository) -> None:
    empty_user_repository.create_user(
        "user1", "user1@example.com", datetime.now(tz=timezone.utc)
    )
    device = Device(
        token="device1_token",
        os=DeviceOS.ANDROID,
        version="1",
        first_connection=datetime.now(tz=timezone.utc),
        last_connection=None,
    )
    empty_user_repository.add_device_registration(
        "user1",
        device.token,
        device.os,
        device.version,
        device.first_connection,
    )
    devices = empty_user_repository.get_device_registrations_from_user_id("user1")
    assert devices == [device]


def test_set_device_registration__multiple_registration(
    empty_user_repository: UserRepository,
) -> None:
    empty_user_repository.create_user(
        "user1", "user1@example.com", datetime.now(tz=timezone.utc)
    )
    device = Device(
        token="device1_token",
        os=DeviceOS.ANDROID,
        version="1",
        first_connection=datetime(2023, 1, 2, 3, 4, 5, tzinfo=timezone.utc),
        last_connection=None,
    )
    empty_user_repository.add_device_registration(
        "user1",
        device.token,
        device.os,
        device.version,
        device.first_connection,
    )
    devices = empty_user_repository.get_device_registrations_from_user_id("user1")
    assert devices == [device]

    empty_user_repository.add_device_registration(
        "user1",
        device.token,
        device.os,
        device.version,
        datetime(2024, 2, 3, 4, 5, 6, tzinfo=timezone.utc),
    )
    devices = empty_user_repository.get_device_registrations_from_user_id("user1")
    device.last_connection = datetime(2024, 2, 3, 4, 5, 6, tzinfo=timezone.utc)
    assert devices == [device]

    empty_user_repository.add_device_registration(
        "user1",
        device.token,
        device.os,
        device.version,
        datetime(2024, 3, 4, 5, 6, 7, tzinfo=timezone.utc),
    )
    devices = empty_user_repository.get_device_registrations_from_user_id("user1")
    device.last_connection = datetime(2024, 3, 4, 5, 6, 7, tzinfo=timezone.utc)
    assert devices == [device]

    device2 = Device(
        token="device2_token",
        os=DeviceOS.ANDROID,
        version="1",
        first_connection=datetime(2023, 4, 5, 6, 7, 8, tzinfo=timezone.utc),
        last_connection=None,
    )
    empty_user_repository.add_device_registration(
        "user1",
        device2.token,
        device2.os,
        device2.version,
        device2.first_connection,
    )
    devices = empty_user_repository.get_device_registrations_from_user_id("user1")
    assert devices == [device, device2]


def test_create_user(empty_user_repository: UserRepository) -> None:
    user = User(
        id="user1",
        email_address="user1@example.com",
        created_at=datetime.now(tz=timezone.utc),
    )
    empty_user_repository.create_user(user.id, user.email_address, user.created_at)
    assert empty_user_repository.exists(user.id)


def test_create_user__should_not_add_user_twice(
    empty_user_repository: UserRepository,
) -> None:
    empty_user_repository.create_user(
        "user1", "user1@example.com", datetime.now(tz=timezone.utc)
    )
    assert len(empty_user_repository.list_users()) == 1
    empty_user_repository.create_user(
        "user1", "user1@example.com", datetime.now(tz=timezone.utc)
    )
    assert len(empty_user_repository.list_users()) == 1


def test_exists(empty_user_repository: UserRepository) -> None:
    empty_user_repository.create_user(
        "user1", "user1@example.com", datetime.now(tz=timezone.utc)
    )
    assert empty_user_repository.exists("user1")
    assert not empty_user_repository.exists("nonexistent_user")
