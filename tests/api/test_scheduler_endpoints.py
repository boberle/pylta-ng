from datetime import date, datetime

from fastapi.testclient import TestClient

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
from tests.services.asserts_scheduler_service import (
    assert_scheduler_service_for_date_20230102,
)


def test_schedule_assignments(
    test_client: TestClient,
    ios_recording_notification_publisher: RecordingNotificationPublisher,
    android_recording_notification_publisher: RecordingNotificationPublisher,
    empty_memory_assignment_repository: InMemoryAssignmentRepository,
    notification_scheduler: RecordingDirectNotificationScheduler,
) -> None:
    now = date(2023, 1, 2)
    response = test_client.get(f"/schedule-assignments/?ref_date={now.isoformat()}")
    assert response.status_code == 200

    assert_scheduler_service_for_date_20230102(
        assignment_repository=empty_memory_assignment_repository,
        notification_scheduler=notification_scheduler,
        android_notification_publisher=android_recording_notification_publisher,
        ios_notification_publisher=ios_recording_notification_publisher,
        assignments_are_submitted=False,
    )


def test_schedule_assignments__no_ref_date(
    test_client: TestClient,
) -> None:
    response = test_client.get("/schedule-assignments/")
    assert response.status_code == 200


def test_schedule_assignment(
    test_client: TestClient,
    ios_recording_notification_publisher: RecordingNotificationPublisher,
    android_recording_notification_publisher: RecordingNotificationPublisher,
    empty_memory_assignment_repository: InMemoryAssignmentRepository,
    notification_scheduler: RecordingDirectNotificationScheduler,
) -> None:
    now = datetime(2023, 1, 2, 3, 4, 5)
    response = test_client.post(
        f"/schedule-assignment/?ref_time={now.isoformat()}",
        json=dict(user_id="user1", survey_id="survey1"),
    )
    assert response.status_code == 200

    assert empty_memory_assignment_repository.assignments == {
        "user1": {
            "f3a3c571-7476-4899-b5a3-adb3254a9493": Assignment(
                id="f3a3c571-7476-4899-b5a3-adb3254a9493",
                title="Sample first survey!",
                user_id="user1",
                survey_id="survey1",
                created_at=datetime(2023, 1, 2, 3, 4, 5),
                expired_at=datetime(2023, 1, 2, 4, 4, 5),
                notified_at=[],
                opened_at=[],
                submitted_at=None,
                answers=None,
            )
        }
    }

    assert notification_scheduler.recorder == [
        {
            "dt": datetime(2023, 1, 2, 3, 4, 5),
            "user_id": "user1",
            "notification_title": "Hey",
            "notification_message": "Survey published!",
        },
        {
            "dt": datetime(2023, 1, 2, 3, 34, 5),
            "user_id": "user1",
            "notification_title": "Hey",
            "notification_message": "Survey soon to expire!",
            "assignment_id": "f3a3c571-7476-4899-b5a3-adb3254a9493",
        },
    ]

    assert android_recording_notification_publisher.recorder == [
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
    ]

    assert ios_recording_notification_publisher.recorder == [
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


def test_schedule_assignment__no_ref_time(
    test_client: TestClient,
) -> None:
    response = test_client.post(
        "/schedule-assignment/",
        json=dict(user_id="user1", survey_id="survey1"),
    )
    assert response.status_code == 200


def test_notify_user(
    test_client: TestClient,
    ios_recording_notification_publisher: RecordingNotificationPublisher,
    android_recording_notification_publisher: RecordingNotificationPublisher,
) -> None:
    response = test_client.post(
        "/notify-user/",
        json=dict(
            user_id="user1",
            notification_title="notif title",
            notification_message="notif message",
        ),
    )
    assert response.status_code == 200

    assert android_recording_notification_publisher.recorder == [
        {
            "device_token": "user1_device1",
            "title": "notif title",
            "message": "notif message",
        },
    ]

    assert ios_recording_notification_publisher.recorder == [
        {
            "device_token": "user1_device2",
            "title": "notif title",
            "message": "notif message",
        },
    ]
