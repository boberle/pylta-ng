import random
from datetime import date, datetime, time, timedelta, timezone

import pytest

from lta.domain.assignment import Assignment
from lta.domain.group_repository import GroupRepository
from lta.domain.schedule_repository import ScheduleRepository
from lta.domain.scheduler.assignment_service import AssignmentService
from lta.domain.scheduler.notification_service import NotificationService
from lta.domain.scheduler.scheduler_service import (
    SchedulerService,
    convert_int_to_time,
    convert_time_to_int,
)
from lta.domain.survey_repository import SurveyRepository
from lta.domain.user_repository import UserRepository
from lta.infra.repositories.memory.assignment_repository import (
    InMemoryAssignmentRepository,
)
from lta.infra.scheduler.assignment_scheduler import DirectAssignmentScheduler
from lta.infra.scheduler.notification_publisher import RecordingNotificationPublisher
from lta.infra.scheduler.notification_scheduler import (
    RecordingDirectNotificationScheduler,
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


def test_schedule_assignments_for_date__using_direct_scheduler(
    prefilled_memory_user_repository: UserRepository,
    prefilled_memory_schedule_repository: ScheduleRepository,
    prefilled_memory_group_repository: GroupRepository,
    prefilled_memory_survey_repository: SurveyRepository,
) -> None:
    ios_notification_publisher = RecordingNotificationPublisher()
    android_notification_publisher = RecordingNotificationPublisher()
    notification_service = NotificationService(
        ios_notification_publisher=ios_notification_publisher,
        android_notification_publisher=android_notification_publisher,
        user_repository=prefilled_memory_user_repository,
    )

    notification_scheduler = RecordingDirectNotificationScheduler(
        user_repository=prefilled_memory_user_repository,
        notification_service=notification_service,
    )
    assignment_repository = InMemoryAssignmentRepository()
    assignment_service = AssignmentService(
        notification_scheduler=notification_scheduler,
        assignment_repository=assignment_repository,
        survey_repository=prefilled_memory_survey_repository,
        soon_to_expire_notification_delay=timedelta(minutes=30),
        rand=random.Random(100),
    )

    assignment_scheduler = DirectAssignmentScheduler(
        assignment_service=assignment_service,
    )

    service = SchedulerService(
        assignment_scheduler=assignment_scheduler,
        schedule_repository=prefilled_memory_schedule_repository,
        group_repository=prefilled_memory_group_repository,
        rand=random.Random(100),
    )

    now = date(2023, 1, 2)
    service.schedule_assignments_for_date(ref_date=now)

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
