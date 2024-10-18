from datetime import datetime, timezone

import pytest

from lta.domain.assignment import Assignment
from lta.domain.scheduler.notification_service import (
    NotificationSendingAssignmentNotSubmitterPolicy,
    NotificationService,
)
from lta.domain.user_repository import UserRepository
from lta.infra.repositories.memory.assignment_repository import (
    InMemoryAssignmentRepository,
)
from lta.infra.scheduler.recording.notification_publisher import (
    RecordingNotificationPublisher,
)


def test_notify_user(prefilled_memory_user_repository: UserRepository) -> None:
    ios_notification_publisher = RecordingNotificationPublisher()
    android_notification_publisher = RecordingNotificationPublisher()
    assignment_repository = InMemoryAssignmentRepository()
    assignment_repository.create_assignment(
        user_id="user1",
        id="assignment1",
        survey_id="survey1",
        survey_title="Latest Survey",
        created_at=datetime(2022, 1, 1, 0, 0, tzinfo=timezone.utc),
    )

    service = NotificationService(
        ios_notification_publisher=ios_notification_publisher,
        android_notification_publisher=android_notification_publisher,
        user_repository=prefilled_memory_user_repository,
        assignment_repository=assignment_repository,
    )

    service.notify_user(
        user_id="user1",
        assignment_id="assignment1",
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

    assert (
        len(assignment_repository.get_assignment("user1", "assignment1").notified_at)
        == 1
    )


@pytest.mark.parametrize(
    "assignment_id,expect_notification",
    [
        ("assignment1", True),
        ("assignment2", False),
    ],
)
def test_notify_user__check_assignment_is_not_submitted(
    prefilled_memory_user_repository: UserRepository,
    assignment_id: str,
    expect_notification: bool,
) -> None:
    ios_notification_publisher = RecordingNotificationPublisher()
    android_notification_publisher = RecordingNotificationPublisher()
    assignment_repository = InMemoryAssignmentRepository(
        {
            "user1": {
                "assignment1": Assignment(
                    id="assignment1",
                    title="Sample first survey!",
                    user_id="user1",
                    survey_id="survey1",
                    created_at=datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc),
                    expired_at=datetime(2023, 10, 10, 12, 0, 0, tzinfo=timezone.utc),
                    notified_at=[datetime(2023, 10, 1, 14, 0, 0, tzinfo=timezone.utc)],
                    opened_at=[datetime(2023, 10, 1, 15, 0, 0, tzinfo=timezone.utc)],
                    submitted_at=None,
                    answers=None,
                ),
                "assignment2": Assignment(
                    id="assignment2",
                    title="Sample first survey!",
                    user_id="user1",
                    survey_id="survey1",
                    created_at=datetime(2023, 10, 1, 12, 0, 0, tzinfo=timezone.utc),
                    expired_at=datetime(2023, 10, 10, 12, 0, 0, tzinfo=timezone.utc),
                    notified_at=[datetime(2023, 10, 1, 14, 0, 0, tzinfo=timezone.utc)],
                    opened_at=[datetime(2023, 10, 1, 15, 0, 0, tzinfo=timezone.utc)],
                    submitted_at=datetime(2023, 10, 1, 16, 0, 0, tzinfo=timezone.utc),
                    answers=[1, 2, "answer"],
                ),
            }
        }
    )
    service = NotificationService(
        ios_notification_publisher=ios_notification_publisher,
        android_notification_publisher=android_notification_publisher,
        user_repository=prefilled_memory_user_repository,
        assignment_repository=assignment_repository,
    )

    service.notify_user(
        user_id="user1",
        assignment_id=assignment_id,
        notification_title="New Survey Available",
        notification_message="Please take a look at the latest survey",
        policy=NotificationSendingAssignmentNotSubmitterPolicy(),
    )

    if expect_notification:
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
        assert (
            len(
                assignment_repository.get_assignment("user1", "assignment1").notified_at
            )
            == 2
        )
        assert (
            len(
                assignment_repository.get_assignment("user1", "assignment2").notified_at
            )
            == 1
        )
    else:
        assert len(android_notification_publisher.recorder) == 0
        assert len(ios_notification_publisher.recorder) == 0
        assert (
            len(
                assignment_repository.get_assignment("user1", "assignment1").notified_at
            )
            == 1
        )
        assert (
            len(
                assignment_repository.get_assignment("user1", "assignment2").notified_at
            )
            == 1
        )
