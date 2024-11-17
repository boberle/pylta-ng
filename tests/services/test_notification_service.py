import logging
from datetime import datetime, timezone

import pytest
from _pytest.logging import LogCaptureFixture

from lta.domain.assignment import Assignment
from lta.domain.scheduler.notification_pulisher import (
    NotificationPublisher,
    NotificationType,
)
from lta.domain.scheduler.notification_service import NotificationService
from lta.domain.survey import Survey, SurveyNotificationInfo
from lta.domain.survey_repository import SurveyRepository
from lta.domain.user import User, UserNotificationInfo
from lta.domain.user_repository import UserRepository
from lta.infra.repositories.memory.assignment_repository import (
    InMemoryAssignmentRepository,
)
from lta.infra.scheduler.recording.notification_publisher import (
    RecordedData,
    RecordingNotificationPublisher,
)


@pytest.fixture
def recording_notification_publisher() -> RecordingNotificationPublisher:
    return RecordingNotificationPublisher()


@pytest.fixture
def notification_service(
    prefilled_memory_user_repository: UserRepository,
    prefilled_memory_survey_repository: SurveyRepository,
    prefilled_memory_assignment_repository: InMemoryAssignmentRepository,
    recording_notification_publisher: RecordingNotificationPublisher,
) -> NotificationService:
    return NotificationService(
        publishers=[recording_notification_publisher],
        user_repository=prefilled_memory_user_repository,
        assignment_repository=prefilled_memory_assignment_repository,
        survey_repository=prefilled_memory_survey_repository,
    )


def test_send_notification(
    notification_service: NotificationService,
    recording_notification_publisher: RecordingNotificationPublisher,
    sample_user_1: User,
    sample_survey_1: Survey,
    sample_assignment_1: Assignment,
) -> None:
    result = notification_service.send_notification(
        user=sample_user_1,
        assignment=sample_assignment_1,
        notification_type=NotificationType.INITIAL,
    )

    assert result is True
    assert recording_notification_publisher.recorder == [
        RecordedData(
            user_id=sample_user_1.id,
            assignment_id=sample_assignment_1.id,
            user_notification_info=sample_user_1.notification_info,
            survey_notification_info=sample_survey_1.notification_info,
            notification_type=NotificationType.INITIAL,
        )
    ]


def test_send_notification__multiple_publishers(
    notification_service: NotificationService,
    recording_notification_publisher: RecordingNotificationPublisher,
    sample_user_1: User,
    sample_survey_1: Survey,
    sample_assignment_1: Assignment,
) -> None:
    notification_service.publishers.append(recording_notification_publisher)
    result = notification_service.send_notification(
        user=sample_user_1,
        assignment=sample_assignment_1,
        notification_type=NotificationType.INITIAL,
    )

    assert result is True
    assert (
        recording_notification_publisher.recorder
        == [
            RecordedData(
                user_id=sample_user_1.id,
                assignment_id=sample_assignment_1.id,
                user_notification_info=sample_user_1.notification_info,
                survey_notification_info=sample_survey_1.notification_info,
                notification_type=NotificationType.INITIAL,
            )
        ]
        * 2
    )


def test_send_notification__no_publisher(
    notification_service: NotificationService,
    prefilled_memory_survey_repository: SurveyRepository,
    recording_notification_publisher: RecordingNotificationPublisher,
    sample_user_1: User,
    sample_assignment_1: Assignment,
) -> None:
    notification_service.publishers = []
    result = notification_service.send_notification(
        user=sample_user_1,
        assignment=sample_assignment_1,
        notification_type=NotificationType.INITIAL,
    )

    assert result is False
    assert recording_notification_publisher.recorder == []


def test_notify_user(
    notification_service: NotificationService,
    recording_notification_publisher: RecordingNotificationPublisher,
    sample_user_1: User,
    sample_assignment_1: Assignment,
    sample_survey_1: Survey,
) -> None:
    ref_time = datetime.now(timezone.utc)
    notification_service.notify_user(
        user_id=sample_user_1.id,
        assignment_id=sample_assignment_1.id,
        notification_type=NotificationType.INITIAL,
        when=ref_time,
    )
    assert recording_notification_publisher.recorder == [
        RecordedData(
            user_id=sample_user_1.id,
            assignment_id=sample_assignment_1.id,
            user_notification_info=sample_user_1.notification_info,
            survey_notification_info=sample_survey_1.notification_info,
            notification_type=NotificationType.INITIAL,
        )
    ]

    assert sample_assignment_1.notified_at == [ref_time]


def test_notify_user__assignment_already_submitted(
    notification_service: NotificationService,
    prefilled_memory_survey_repository: SurveyRepository,
    recording_notification_publisher: RecordingNotificationPublisher,
    sample_user_1: User,
    sample_assignment_2: Assignment,
) -> None:
    assert sample_assignment_2.submitted_at is not None
    notification_service.notify_user(
        user_id=sample_user_1.id,
        assignment_id=sample_assignment_2.id,
        notification_type=NotificationType.INITIAL,
    )
    assert recording_notification_publisher.recorder == []


class FailingPublisher(NotificationPublisher):
    def send_notification(
        self,
        user_id: str,
        assignment_id: str,
        user_notification_info: UserNotificationInfo,
        survey_notification_info: SurveyNotificationInfo,
        notification_type: NotificationType,
    ) -> bool:
        return False


def test_notify_user__failing_publisher(
    notification_service: NotificationService,
    prefilled_memory_survey_repository: SurveyRepository,
    sample_user_1: User,
    sample_assignment_1: Assignment,
    caplog: LogCaptureFixture,
) -> None:
    notification_service.publishers = [FailingPublisher()]
    with caplog.at_level(logging.WARNING):
        notification_service.notify_user(
            user_id=sample_user_1.id,
            assignment_id=sample_assignment_1.id,
            notification_type=NotificationType.INITIAL,
        )
        assert caplog.messages == [
            "Notification not sent: no notification channel available"
        ]
