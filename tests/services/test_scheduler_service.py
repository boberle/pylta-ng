import random
from datetime import date, time, timedelta

import pytest

from lta.domain.group_repository import GroupRepository
from lta.domain.schedule_repository import ScheduleRepository
from lta.domain.scheduler.assignment_service import BasicAssignmentService
from lta.domain.scheduler.notification_service import PushNotificationService
from lta.domain.scheduler.scheduler_service import (
    BasicSchedulerService,
    convert_int_to_time,
    convert_time_to_int,
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
from tests.fixtures.assignment_repositories import AlwaysSubmittedAssignmentRepository
from tests.services.asserts_scheduler_service import (
    assert_scheduler_service_for_date_20230102,
)


@pytest.mark.parametrize(
    "t,i",
    [
        (time(0, 0, 0), 0),
        (time(1, 0, 0), 3600),
        (time(0, 1, 0), 60),
        (time(0, 0, 1), 1),
        (time(1, 1, 1), 3661),
        (time(23, 59, 59), 86399),
    ],
)
def test_convert_time_to_int_in_vice_versa(t: time, i: int) -> None:
    assert convert_time_to_int(t) == i
    assert convert_int_to_time(i) == t


@pytest.mark.parametrize("assignment_is_submitted", [True, False])
def test_schedule_assignments_for_date__using_direct_scheduler(
    prefilled_memory_user_repository: UserRepository,
    prefilled_memory_schedule_repository: ScheduleRepository,
    prefilled_memory_group_repository: GroupRepository,
    prefilled_memory_survey_repository: SurveyRepository,
    empty_memory_assignment_repository: InMemoryAssignmentRepository,
    always_submitted_assignment_repository: AlwaysSubmittedAssignmentRepository,
    assignment_is_submitted: bool,
) -> None:
    ios_notification_publisher = RecordingNotificationPublisher()
    android_notification_publisher = RecordingNotificationPublisher()

    assignment_repository = (
        always_submitted_assignment_repository
        if assignment_is_submitted
        else empty_memory_assignment_repository
    )

    notification_service = PushNotificationService(
        ios_notification_publisher=ios_notification_publisher,
        android_notification_publisher=android_notification_publisher,
        user_repository=prefilled_memory_user_repository,
        assignment_repository=assignment_repository,
    )

    notification_scheduler = RecordingDirectNotificationScheduler(
        user_repository=prefilled_memory_user_repository,
        notification_service=notification_service,
    )
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

    service = BasicSchedulerService(
        assignment_scheduler=assignment_scheduler,
        schedule_repository=prefilled_memory_schedule_repository,
        group_repository=prefilled_memory_group_repository,
        rand=random.Random(100),
    )

    now = date(2023, 1, 2)
    service.schedule_assignments_for_date(ref_date=now)

    assert_scheduler_service_for_date_20230102(
        assignment_repository=assignment_repository,
        notification_scheduler=notification_scheduler,
        android_notification_publisher=android_notification_publisher,
        ios_notification_publisher=ios_notification_publisher,
        assignments_are_submitted=assignment_is_submitted,
    )
