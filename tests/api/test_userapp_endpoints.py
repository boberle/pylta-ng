from datetime import datetime, timezone

import pytest
from starlette.testclient import TestClient

from lta.domain.user import Device, DeviceOS
from lta.infra.repositories.memory.user_repository import InMemoryUserRepository
from lta.infra.scheduler.recording.notification_publisher import (
    RecordingNotificationPublisher,
)


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

    assert prefilled_memory_user_repository.users[
        "user1"
    ].notification_info.devices == [
        Device(
            token="user1_device1",
            os=DeviceOS.ANDROID,
            version="1",
            connections=[
                datetime(2024, 1, 1, tzinfo=timezone.utc),
                datetime(2024, 3, 4, 5, 6, 7, tzinfo=timezone.utc),
            ],
        ),
        Device(
            token="user1_device2",
            os=DeviceOS.IOS,
            version="1",
            connections=[
                datetime(2024, 1, 1, tzinfo=timezone.utc),
            ],
        ),
    ]


@pytest.mark.skip("Test not implemented yet")
def test_send_test_notification(
    test_client: TestClient,
    android_recording_notification_publisher: RecordingNotificationPublisher,
    ios_recording_notification_publisher: RecordingNotificationPublisher,
) -> None:
    response = test_client.get(
        "/api/mobile/v1/test-notification/",
    )
    assert response.status_code == 200
    assert android_recording_notification_publisher.recorder == []
    assert ios_recording_notification_publisher.recorder == []
