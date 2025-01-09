import random
from datetime import timedelta

import pytest
from starlette.testclient import TestClient

import lta.api.app
from lta.api.configuration import (
    get_assignment_service,
    get_notification_service,
    get_scheduler_service,
    get_user_repository,
)
from lta.authentication import AuthenticatedUser, get_authenticated_user
from lta.domain.assignment_repository import AssignmentRepository
from lta.domain.group_repository import GroupRepository
from lta.domain.schedule_repository import ScheduleRepository
from lta.domain.scheduler.assignment_service import AssignmentService
from lta.domain.scheduler.notification_service import NotificationService
from lta.domain.scheduler.scheduler_service import SchedulerService
from lta.domain.survey_repository import SurveyRepository
from lta.domain.user_repository import UserRepository
from lta.infra.repositories.memory.assignment_repository import (
    InMemoryAssignmentRepository,
)
from lta.infra.scheduler.direct.assignment_scheduler import DirectAssignmentScheduler
from lta.infra.scheduler.direct.notification_scheduler import (
    DirectNotificationScheduler,
)
from lta.infra.scheduler.recording.notification_publisher import (
    RecordingNotificationPublisher,
)


@pytest.fixture
def notification_service(
    prefilled_memory_user_repository: UserRepository,
    prefilled_memory_survey_repository: SurveyRepository,
    empty_assignment_repository: AssignmentRepository,
) -> NotificationService:
    return NotificationService(
        publishers=[RecordingNotificationPublisher()],
        user_repository=prefilled_memory_user_repository,
        assignment_repository=empty_assignment_repository,
        survey_repository=prefilled_memory_survey_repository,
    )


@pytest.fixture
def notification_scheduler(
    prefilled_memory_user_repository: UserRepository,
    notification_service: NotificationService,
) -> DirectNotificationScheduler:
    return DirectNotificationScheduler(
        user_repository=prefilled_memory_user_repository,
        notification_service=notification_service,
    )


@pytest.fixture
def test_client(
    prefilled_memory_user_repository: UserRepository,
    prefilled_memory_schedule_repository: ScheduleRepository,
    prefilled_memory_group_repository: GroupRepository,
    prefilled_memory_survey_repository: SurveyRepository,
    empty_memory_assignment_repository: InMemoryAssignmentRepository,
    notification_service: NotificationService,
    notification_scheduler: DirectNotificationScheduler,
) -> TestClient:

    assignment_service = AssignmentService(
        notification_scheduler=notification_scheduler,
        assignment_repository=empty_memory_assignment_repository,
        survey_repository=prefilled_memory_survey_repository,
        reminder_notification_delays=[timedelta(minutes=30)],
        rand=random.Random(100),
    )

    assignment_scheduler = DirectAssignmentScheduler(
        assignment_service=assignment_service,
    )

    scheduler_service = SchedulerService(
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

    def override_get_authenticated_user() -> AuthenticatedUser:
        return AuthenticatedUser(id="user1", email_address="user1@idontexist.net")

    app = lta.api.app.app
    app.dependency_overrides[get_scheduler_service] = override_get_scheduler_service
    app.dependency_overrides[get_assignment_service] = override_get_assignment_service
    app.dependency_overrides[get_notification_service] = (
        override_get_notification_service
    )
    app.dependency_overrides[get_authenticated_user] = override_get_authenticated_user
    app.dependency_overrides[get_user_repository] = (
        lambda: prefilled_memory_user_repository
    )
    return TestClient(app)
