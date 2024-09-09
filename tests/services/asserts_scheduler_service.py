from datetime import datetime, timezone

from lta.domain.assignment import Assignment
from lta.infra.repositories.memory.assignment_repository import (
    InMemoryAssignmentRepository,
)
from lta.infra.scheduler.recording.notification_publisher import (
    RecordingNotificationPublisher,
)
from lta.infra.scheduler.recording.notification_scheduler import (
    RecordingDirectNotificationScheduler,
)


def assert_scheduler_service_for_date_20230102(
    assignment_repository: InMemoryAssignmentRepository,
    notification_scheduler: RecordingDirectNotificationScheduler,
    android_notification_publisher: RecordingNotificationPublisher,
    ios_notification_publisher: RecordingNotificationPublisher,
) -> None:
    assert assignment_repository.assignments == {
        "user1": {
            "81c1e7ff-6efa-4d5b-9988-5afcbb61a9cd": Assignment(
                id="81c1e7ff-6efa-4d5b-9988-5afcbb61a9cd",
                user_id="user1",
                survey_id="survey1",
                created_at=datetime(2023, 1, 2, 14, 31, 3, tzinfo=timezone.utc),
                scheduled_for=None,
                published_at=None,
                expired_at=None,
                notified_at=[],
                opened_at=[],
                submitted_at=None,
                answers=None,
            ),
            "f3a3c571-7476-4899-b5a3-adb3254a9493": Assignment(
                id="f3a3c571-7476-4899-b5a3-adb3254a9493",
                user_id="user1",
                survey_id="survey1",
                created_at=datetime(2023, 1, 2, 9, 9, 56, tzinfo=timezone.utc),
                scheduled_for=None,
                published_at=None,
                expired_at=None,
                notified_at=[],
                opened_at=[],
                submitted_at=None,
                answers=None,
            ),
        },
        "user2": {
            "1f0e4b4a-886c-4a30-9c26-ffa8ccce240c": Assignment(
                id="1f0e4b4a-886c-4a30-9c26-ffa8ccce240c",
                user_id="user2",
                survey_id="survey1",
                created_at=datetime(2023, 1, 2, 14, 52, 37, tzinfo=timezone.utc),
                scheduled_for=None,
                published_at=None,
                expired_at=None,
                notified_at=[],
                opened_at=[],
                submitted_at=None,
                answers=None,
            ),
            "649dda6e-b49c-43dc-acbc-408cc5521660": Assignment(
                id="649dda6e-b49c-43dc-acbc-408cc5521660",
                user_id="user2",
                survey_id="survey1",
                created_at=datetime(2023, 1, 2, 9, 31, 22, tzinfo=timezone.utc),
                scheduled_for=None,
                published_at=None,
                expired_at=None,
                notified_at=[],
                opened_at=[],
                submitted_at=None,
                answers=None,
            ),
        },
    }
    assert notification_scheduler.recorder == [
        {
            "dt": datetime(2023, 1, 2, 9, 9, 56, tzinfo=timezone.utc),
            "user_id": "user1",
            "notification_title": "Hey",
            "notification_message": "Survey published!",
        },
        {
            "dt": datetime(2023, 1, 2, 9, 39, 56, tzinfo=timezone.utc),
            "user_id": "user1",
            "notification_title": "Hey",
            "notification_message": "Survey soon to expire!",
        },
        {
            "dt": datetime(2023, 1, 2, 9, 31, 22, tzinfo=timezone.utc),
            "user_id": "user2",
            "notification_title": "Hey",
            "notification_message": "Survey published!",
        },
        {
            "dt": datetime(2023, 1, 2, 10, 1, 22, tzinfo=timezone.utc),
            "user_id": "user2",
            "notification_title": "Hey",
            "notification_message": "Survey soon to expire!",
        },
        {
            "dt": datetime(2023, 1, 2, 14, 31, 3, tzinfo=timezone.utc),
            "user_id": "user1",
            "notification_title": "Hey",
            "notification_message": "Survey published!",
        },
        {
            "dt": datetime(2023, 1, 2, 15, 1, 3, tzinfo=timezone.utc),
            "user_id": "user1",
            "notification_title": "Hey",
            "notification_message": "Survey soon to expire!",
        },
        {
            "dt": datetime(2023, 1, 2, 14, 52, 37, tzinfo=timezone.utc),
            "user_id": "user2",
            "notification_title": "Hey",
            "notification_message": "Survey published!",
        },
        {
            "dt": datetime(2023, 1, 2, 15, 22, 37, tzinfo=timezone.utc),
            "user_id": "user2",
            "notification_title": "Hey",
            "notification_message": "Survey soon to expire!",
        },
    ]

    assert len(android_notification_publisher.recorder) == 8
    assert android_notification_publisher.recorder == [
        {
            "device_token": "user1_device1",
            "title": "Hey",
            "message": "Survey published!",
        },
        {
            "device_token": "user1_device1",
            "title": "Hey",
            "message": "Survey soon to expire!",
        },
        {
            "device_token": "user2_device1",
            "title": "Hey",
            "message": "Survey published!",
        },
        {
            "device_token": "user2_device1",
            "title": "Hey",
            "message": "Survey soon to expire!",
        },
        {
            "device_token": "user1_device1",
            "title": "Hey",
            "message": "Survey published!",
        },
        {
            "device_token": "user1_device1",
            "title": "Hey",
            "message": "Survey soon to expire!",
        },
        {
            "device_token": "user2_device1",
            "title": "Hey",
            "message": "Survey published!",
        },
        {
            "device_token": "user2_device1",
            "title": "Hey",
            "message": "Survey soon to expire!",
        },
    ]

    assert len(ios_notification_publisher.recorder) == 4
    assert ios_notification_publisher.recorder == [
        {
            "device_token": "user1_device2",
            "title": "Hey",
            "message": "Survey published!",
        },
        {
            "device_token": "user1_device2",
            "title": "Hey",
            "message": "Survey soon to expire!",
        },
        {
            "device_token": "user1_device2",
            "title": "Hey",
            "message": "Survey published!",
        },
        {
            "device_token": "user1_device2",
            "title": "Hey",
            "message": "Survey soon to expire!",
        },
    ]
