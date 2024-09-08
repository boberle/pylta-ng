from datetime import datetime, time, timedelta, timezone

import pytest

from lta.domain.schedule import Schedule, TimeRange
from lta.domain.schedule_repository import (
    ScheduleCreation,
    ScheduleNotFound,
    ScheduleRepository,
)


def test_create_and_get_schedule(empty_schedule_repository: ScheduleRepository) -> None:
    now = datetime.now(tz=timezone.utc).date()
    time_now = time(hour=12, minute=0, second=0)
    schedule = ScheduleCreation(
        survey_id="survey1",
        start_date=now,
        end_date=now + timedelta(days=1),
        time_ranges=[
            TimeRange(start_time=time_now, end_time=time_now.replace(minute=30))
        ],
        user_ids=["user1"],
        group_ids=["group1"],
    )
    empty_schedule_repository.create_schedule("1", schedule)
    got_schedule = empty_schedule_repository.get_schedule("1")
    assert got_schedule == Schedule(id="1", **schedule.model_dump())

    with pytest.raises(ScheduleNotFound):
        empty_schedule_repository.get_schedule("2")


def test_delete_schedule(empty_schedule_repository: ScheduleRepository) -> None:
    now = datetime.now(tz=timezone.utc).date()
    time_now = time(hour=12, minute=0, second=0)
    schedule = ScheduleCreation(
        survey_id="survey1",
        start_date=now,
        end_date=now + timedelta(days=1),
        time_ranges=[
            TimeRange(start_time=time_now, end_time=time_now.replace(minute=30))
        ],
        user_ids=["user1"],
        group_ids=["group1"],
    )
    empty_schedule_repository.create_schedule("1", schedule)
    empty_schedule_repository.delete_schedule("1")
    assert empty_schedule_repository.list_schedules() == []


def test_list_schedules_and_active_schedules(
    empty_schedule_repository: ScheduleRepository,
) -> None:
    now = datetime(2024, 1, 2, tzinfo=timezone.utc)
    time_now = time(hour=1, minute=2, second=3)
    schedule_creation_1 = ScheduleCreation(
        survey_id="survey1",
        start_date=(now - timedelta(days=2)).date(),
        end_date=(now - timedelta(days=1)).date(),
        time_ranges=[
            TimeRange(start_time=time_now, end_time=time_now.replace(minute=30))
        ],
        user_ids=["user1"],
        group_ids=["group1"],
    )
    schedule_creation_2 = ScheduleCreation(
        survey_id="survey1",
        start_date=(now - timedelta(days=1)).date(),
        end_date=(now + timedelta(days=1)).date(),
        time_ranges=[
            TimeRange(start_time=time_now, end_time=time_now.replace(minute=30))
        ],
        user_ids=["user1"],
        group_ids=["group1"],
    )
    schedule_creation_3 = ScheduleCreation(
        survey_id="survey1",
        start_date=now.date(),
        end_date=(now + timedelta(days=1)).date(),
        time_ranges=[
            TimeRange(start_time=time_now, end_time=time_now.replace(minute=30))
        ],
        user_ids=["user1"],
        group_ids=["group1"],
    )

    schedule_1 = Schedule(id="1", **schedule_creation_1.model_dump())
    schedule_2 = Schedule(id="2", **schedule_creation_2.model_dump())
    schedule_3 = Schedule(id="3", **schedule_creation_3.model_dump())

    empty_schedule_repository.create_schedule("1", schedule_creation_1)
    empty_schedule_repository.create_schedule("2", schedule_creation_2)
    empty_schedule_repository.create_schedule("3", schedule_creation_3)

    assert empty_schedule_repository.list_schedules() == [
        schedule_3,
        schedule_2,
        schedule_1,
    ]

    assert (
        empty_schedule_repository.list_active_schedules(
            (now - timedelta(days=3)).date()
        )
        == []
    )
    assert empty_schedule_repository.list_active_schedules(
        (now - timedelta(days=2)).date()
    ) == [schedule_1]
    assert empty_schedule_repository.list_active_schedules(
        (now - timedelta(days=1)).date()
    ) == [schedule_2, schedule_1]
    assert empty_schedule_repository.list_active_schedules(now.date()) == [
        schedule_3,
        schedule_2,
    ]
    assert empty_schedule_repository.list_active_schedules(
        (now + timedelta(days=1)).date()
    ) == [schedule_3, schedule_2]
    assert (
        empty_schedule_repository.list_active_schedules(
            (now + timedelta(days=2)).date()
        )
        == []
    )
