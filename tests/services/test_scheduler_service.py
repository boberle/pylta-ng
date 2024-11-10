import random
from datetime import date, datetime, time, timedelta, timezone

import pytest

from lta.domain.group_repository import GroupRepository
from lta.domain.schedule import Day, TimeRange
from lta.domain.schedule_repository import ScheduleRepository
from lta.domain.scheduler.assignment_service import BasicAssignmentService
from lta.domain.scheduler.notification_service import PushNotificationService
from lta.domain.scheduler.scheduler_service import (
    BasicSchedulerService,
    DatetimeRange,
    get_dates_from_days,
    get_datetime_ranges_from_dates_and_time_range,
    get_previous_monday,
    get_random_datetime,
    keep_ranges_after_ref_time,
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
    "ref_time, expected_monday",
    [
        (
            datetime(2023, 10, 16, tzinfo=timezone.utc),
            date(2023, 10, 16),
        ),  # Monday
        (
            datetime(2023, 10, 17, tzinfo=timezone.utc),
            date(2023, 10, 16),
        ),  # Tuesday
        (
            datetime(2023, 10, 20, tzinfo=timezone.utc),
            date(2023, 10, 16),
        ),  # Friday
        (
            datetime(2023, 10, 22, tzinfo=timezone.utc),
            date(2023, 10, 16),
        ),  # Sunday
    ],
)
def test_get_previous_monday(ref_time: datetime, expected_monday: date) -> None:
    assert get_previous_monday(ref_time) == expected_monday


@pytest.mark.parametrize(
    "ref_time, days, expected_dates",
    [
        (
            datetime(2023, 10, 18, tzinfo=timezone.utc),  # Wednesday
            [Day.MONDAY, Day.WEDNESDAY, Day.FRIDAY],
            [date(2023, 10, 16), date(2023, 10, 18), date(2023, 10, 20)],
        ),
        (
            datetime(2023, 10, 20, tzinfo=timezone.utc),  # Friday
            [Day.TUESDAY, Day.THURSDAY],
            [date(2023, 10, 17), date(2023, 10, 19)],
        ),
        (
            datetime(2023, 10, 22, tzinfo=timezone.utc),  # Sunday
            [Day.SATURDAY, Day.SUNDAY],
            [date(2023, 10, 21), date(2023, 10, 22)],
        ),
    ],
)
def test_get_dates_from_days(
    ref_time: datetime, days: list[Day], expected_dates: list[date]
) -> None:
    assert get_dates_from_days(ref_time, days) == expected_dates


@pytest.mark.parametrize(
    "dates, time_range, expected_ranges",
    [
        (
            [date(2023, 10, 16), date(2023, 10, 17)],
            TimeRange(start_time=time(9, 0, 0), end_time=time(17, 0, 0)),
            [
                DatetimeRange(
                    start=datetime(2023, 10, 16, 9, 0, 0, tzinfo=timezone.utc),
                    end=datetime(2023, 10, 16, 17, 0, 0, tzinfo=timezone.utc),
                ),
                DatetimeRange(
                    start=datetime(2023, 10, 17, 9, 0, 0, tzinfo=timezone.utc),
                    end=datetime(2023, 10, 17, 17, 0, 0, tzinfo=timezone.utc),
                ),
            ],
        ),
        (
            [date(2023, 10, 18)],
            TimeRange(start_time=time(8, 30, 0), end_time=time(12, 30, 0)),
            [
                DatetimeRange(
                    start=datetime(2023, 10, 18, 8, 30, 0, tzinfo=timezone.utc),
                    end=datetime(2023, 10, 18, 12, 30, 0, tzinfo=timezone.utc),
                ),
            ],
        ),
        (
            [],
            TimeRange(start_time=time(10, 0, 0), end_time=time(11, 0, 0)),
            [],
        ),
    ],
)
def test_get_datetime_ranges_from_dates_and_time_range(
    dates: list[date], time_range: TimeRange, expected_ranges: list[DatetimeRange]
) -> None:
    assert (
        get_datetime_ranges_from_dates_and_time_range(dates, time_range)
        == expected_ranges
    )


@pytest.mark.parametrize(
    "ref_time, ranges, expected",
    [
        (
            datetime(2023, 10, 16, 12, 0, 0, tzinfo=timezone.utc),
            [
                DatetimeRange(
                    start=datetime(2023, 10, 16, 9, 0, 0, tzinfo=timezone.utc),
                    end=datetime(2023, 10, 16, 17, 0, 0, tzinfo=timezone.utc),
                ),
                DatetimeRange(
                    start=datetime(2023, 10, 17, 9, 0, 0, tzinfo=timezone.utc),
                    end=datetime(2023, 10, 17, 17, 0, 0, tzinfo=timezone.utc),
                ),
            ],
            [
                DatetimeRange(
                    start=datetime(2023, 10, 16, 12, 0, 0, tzinfo=timezone.utc),
                    end=datetime(2023, 10, 16, 17, 0, 0, tzinfo=timezone.utc),
                ),
                DatetimeRange(
                    start=datetime(2023, 10, 17, 9, 0, 0, tzinfo=timezone.utc),
                    end=datetime(2023, 10, 17, 17, 0, 0, tzinfo=timezone.utc),
                ),
            ],
        ),
        (
            datetime(2023, 10, 16, 18, 0, 0, tzinfo=timezone.utc),
            [
                DatetimeRange(
                    start=datetime(2023, 10, 16, 9, 0, 0, tzinfo=timezone.utc),
                    end=datetime(2023, 10, 16, 17, 0, 0, tzinfo=timezone.utc),
                ),
                DatetimeRange(
                    start=datetime(2023, 10, 17, 9, 0, 0, tzinfo=timezone.utc),
                    end=datetime(2023, 10, 17, 17, 0, 0, tzinfo=timezone.utc),
                ),
            ],
            [
                DatetimeRange(
                    start=datetime(2023, 10, 17, 9, 0, 0, tzinfo=timezone.utc),
                    end=datetime(2023, 10, 17, 17, 0, 0, tzinfo=timezone.utc),
                ),
            ],
        ),
        (
            datetime(2023, 10, 16, 8, 0, 0, tzinfo=timezone.utc),
            [
                DatetimeRange(
                    start=datetime(2023, 10, 16, 7, 0, 0, tzinfo=timezone.utc),
                    end=datetime(2023, 10, 16, 17, 0, 0, tzinfo=timezone.utc),
                ),
            ],
            [
                DatetimeRange(
                    start=datetime(2023, 10, 16, 8, 0, 0, tzinfo=timezone.utc),
                    end=datetime(2023, 10, 16, 17, 0, 0, tzinfo=timezone.utc),
                ),
            ],
        ),
        (
            datetime(2023, 10, 16, 18, 0, 0, tzinfo=timezone.utc),
            [
                DatetimeRange(
                    start=datetime(2023, 10, 16, 9, 0, 0, tzinfo=timezone.utc),
                    end=datetime(2023, 10, 16, 17, 0, 0, tzinfo=timezone.utc),
                ),
            ],
            [],
        ),
    ],
)
def test_keep_ranges_after_ref_time(
    ref_time: datetime, ranges: list[DatetimeRange], expected: list[DatetimeRange]
) -> None:
    assert keep_ranges_after_ref_time(ref_time, ranges) == expected


@pytest.mark.parametrize(
    "ref_time, days, time_range, expected",
    [
        (
            datetime(2023, 10, 16, 12, 0, 0, tzinfo=timezone.utc),
            [Day.MONDAY, Day.WEDNESDAY],
            TimeRange(start_time=time(9, 0, 0), end_time=time(17, 0, 0)),
            datetime(2023, 10, 16, 16, 10, 57, tzinfo=timezone.utc),
        ),
        (
            datetime(2023, 10, 16, 8, 0, 0, tzinfo=timezone.utc),
            [Day.MONDAY],
            TimeRange(start_time=time(7, 0, 0), end_time=time(17, 0, 0)),
            datetime(2023, 10, 16, 12, 10, 57, tzinfo=timezone.utc),
        ),
        (
            datetime(2023, 10, 16, 18, 0, 0, tzinfo=timezone.utc),
            [Day.MONDAY],
            TimeRange(start_time=time(9, 0, 0), end_time=time(17, 0, 0)),
            None,
        ),
        (
            datetime(2023, 10, 17, 7, 0, 0, tzinfo=timezone.utc),
            [Day.MONDAY],
            TimeRange(start_time=time(9, 0, 0), end_time=time(17, 0, 0)),
            None,
        ),
    ],
)
def test_get_random_datetime(
    ref_time: datetime,
    days: list[Day],
    time_range: TimeRange,
    expected: datetime | None,
) -> None:
    rand = random.Random(100)
    result = get_random_datetime(ref_time, days, time_range, rand)
    assert expected == result


@pytest.mark.xfail(reason="Need to rework this test")
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

    now = datetime(2023, 1, 2)
    service.schedule_assignments(ref_time=now)

    assert_scheduler_service_for_date_20230102(
        assignment_repository=assignment_repository,
        notification_scheduler=notification_scheduler,
        android_notification_publisher=android_notification_publisher,
        ios_notification_publisher=ios_notification_publisher,
        assignments_are_submitted=assignment_is_submitted,
    )
