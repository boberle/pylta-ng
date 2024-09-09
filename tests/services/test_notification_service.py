from lta.domain.scheduler.notification_service import NotificationService
from lta.domain.user_repository import UserRepository
from lta.infra.scheduler.recording.notification_publisher import (
    RecordingNotificationPublisher,
)


def test_notify_user(prefilled_memory_user_repository: UserRepository) -> None:
    ios_notification_publisher = RecordingNotificationPublisher()
    android_notification_publisher = RecordingNotificationPublisher()
    service = NotificationService(
        ios_notification_publisher=ios_notification_publisher,
        android_notification_publisher=android_notification_publisher,
        user_repository=prefilled_memory_user_repository,
    )

    service.notify_user(
        user_id="user1",
        notification_title="New Survey Available",
        notification_message="Please take a look at the latest survey",
    )

    assert len(android_notification_publisher.recorder) == 1
    assert android_notification_publisher.recorder[0] == {
        "device_token": "user1_device1",
        "title": "New Survey Available",
        "message": "Please take a look at the latest survey",
    }

    assert len(ios_notification_publisher.recorder) == 1
    assert ios_notification_publisher.recorder[0] == {
        "device_token": "user1_device2",
        "title": "New Survey Available",
        "message": "Please take a look at the latest survey",
    }
