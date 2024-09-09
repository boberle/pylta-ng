import random
from datetime import date, datetime, timedelta

import pytest
from fastapi.testclient import TestClient

import lta.api.app
from lta.api.configuration import (
    get_assignment_service,
    get_notification_service,
    get_scheduler_service,
)
from lta.domain.assignment import Assignment
from lta.domain.group_repository import GroupRepository
from lta.domain.schedule_repository import ScheduleRepository
from lta.domain.scheduler.assignment_service import (
    AssignmentService,
    BasicAssignmentService,
)
from lta.domain.scheduler.notification_service import NotificationService
from lta.domain.scheduler.scheduler_service import (
    BasicSchedulerService,
    SchedulerService,
)
from lta.domain.survey_repository import SurveyRepository
from lta.domain.user_repository import UserRepository
from lta.infra.repositories.memory.assignment_repository import (
    InMemoryAssignmentRepository,
)
from lta.infra.scheduler.direct.assignment_scheduler import DirectAssignmentScheduler
from lta.infra.scheduler.recording.notification_publisher import (
    RecordingNotificationPublisher,
)
from lta.infra.scheduler.recording.notification_scheduler import (
    RecordingDirectNotificationScheduler,
)
from tests.services.asserts_scheduler_service import (
    assert_scheduler_service_for_date_20230102,
)


@pytest.fixture
def ios_recording_notification_publisher() -> RecordingNotificationPublisher:
    return RecordingNotificationPublisher()


@pytest.fixture
def android_recording_notification_publisher() -> RecordingNotificationPublisher:
    return RecordingNotificationPublisher()


@pytest.fixture
def assignment_repository() -> InMemoryAssignmentRepository:
    return InMemoryAssignmentRepository()


@pytest.fixture
def notification_service(
    prefilled_memory_user_repository: UserRepository,
    ios_recording_notification_publisher: RecordingNotificationPublisher,
    android_recording_notification_publisher: RecordingNotificationPublisher,
) -> NotificationService:
    return NotificationService(
        ios_notification_publisher=ios_recording_notification_publisher,
        android_notification_publisher=android_recording_notification_publisher,
        user_repository=prefilled_memory_user_repository,
    )


@pytest.fixture
def notification_scheduler(
    prefilled_memory_user_repository: UserRepository,
    notification_service: NotificationService,
) -> RecordingDirectNotificationScheduler:
    return RecordingDirectNotificationScheduler(
        user_repository=prefilled_memory_user_repository,
        notification_service=notification_service,
    )


@pytest.fixture
def test_client(
    prefilled_memory_user_repository: UserRepository,
    prefilled_memory_schedule_repository: ScheduleRepository,
    prefilled_memory_group_repository: GroupRepository,
    prefilled_memory_survey_repository: SurveyRepository,
    ios_recording_notification_publisher: RecordingNotificationPublisher,
    android_recording_notification_publisher: RecordingNotificationPublisher,
    assignment_repository: InMemoryAssignmentRepository,
    notification_service: NotificationService,
    notification_scheduler: RecordingDirectNotificationScheduler,
) -> TestClient:

    assignment_service = BasicAssignmentService(
        notification_scheduler=notification_scheduler,
        assignment_repository=assignment_repository,
        survey_repository=prefilled_memory_survey_repository,
        soon_to_expire_notification_delay=timedelta(minutes=30),
        rand=random.Random(100),
    )

    assignment_scheduler = DirectAssignmentScheduler(
        assignment_service=assignment_service,
    )

    scheduler_service = BasicSchedulerService(
        assignment_scheduler=assignment_scheduler,
        schedule_repository=prefilled_memory_schedule_repository,
        group_repository=prefilled_memory_group_repository,
        rand=random.Random(100),
    )

    def override_get_scheduler_service() -> SchedulerService:
        return scheduler_service

    def override_get_assignment_service() -> AssignmentService:
        return assignment_service

    def override_get_notification_service() -> NotificationService:
        return notification_service

    app = lta.api.app.app
    app.dependency_overrides[get_scheduler_service] = override_get_scheduler_service
    app.dependency_overrides[get_assignment_service] = override_get_assignment_service
    app.dependency_overrides[get_notification_service] = (
        override_get_notification_service
    )
    return TestClient(app)


def test_schedule_assignments(
    test_client: TestClient,
    ios_recording_notification_publisher: RecordingNotificationPublisher,
    android_recording_notification_publisher: RecordingNotificationPublisher,
    assignment_repository: InMemoryAssignmentRepository,
    notification_scheduler: RecordingDirectNotificationScheduler,
) -> None:
    now = date(2023, 1, 2)
    response = test_client.get(f"/schedule-assignments/?ref_date={now.isoformat()}")
    assert response.status_code == 200

    assert_scheduler_service_for_date_20230102(
        assignment_repository=assignment_repository,
        notification_scheduler=notification_scheduler,
        android_notification_publisher=android_recording_notification_publisher,
        ios_notification_publisher=ios_recording_notification_publisher,
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
    assignment_repository: InMemoryAssignmentRepository,
    notification_scheduler: RecordingDirectNotificationScheduler,
) -> None:
    now = datetime(2023, 1, 2, 3, 4, 5)
    response = test_client.post(
        f"/schedule-assignment/?ref_time={now.isoformat()}",
        json=dict(user_id="user1", survey_id="survey1"),
    )
    assert response.status_code == 200

    assert assignment_repository.assignments == {
        "user1": {
            "f3a3c571-7476-4899-b5a3-adb3254a9493": Assignment(
                id="f3a3c571-7476-4899-b5a3-adb3254a9493",
                user_id="user1",
                survey_id="survey1",
                created_at=datetime(2023, 1, 2, 3, 4, 5),
                scheduled_for=None,
                published_at=None,
                expired_at=None,
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
