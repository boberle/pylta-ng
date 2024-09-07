from datetime import datetime, time, timedelta, timezone

import pytest

from lta.domain.schedule import Schedule, TimeRange
from lta.domain.schedule_repository import (
    ScheduleCreation,
    ScheduleNotFound,
    ScheduleRepository,
)


def test_create_and_get_schedule(empty_schedule_repository: ScheduleRepository) -> None:
    now = datetime.now(tz=timezone.utc)
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
    now = datetime.now(tz=timezone.utc)
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


def test_list_schedules(empty_schedule_repository: ScheduleRepository) -> None:
    now = datetime.now(tz=timezone.utc)
    time_now = time(hour=12, minute=0, second=0)
    schedule1 = ScheduleCreation(
        survey_id="survey1",
        start_date=now,
        end_date=now + timedelta(days=1),
        time_ranges=[
            TimeRange(start_time=time_now, end_time=time_now.replace(minute=30))
        ],
        user_ids=["user1"],
        group_ids=["group1"],
    )
    schedule2 = ScheduleCreation(
        survey_id="survey1",
        start_date=now,
        end_date=now + timedelta(days=1),
        time_ranges=[
            TimeRange(start_time=time_now, end_time=time_now.replace(minute=30))
        ],
        user_ids=["user1"],
        group_ids=["group1"],
    )
    empty_schedule_repository.create_schedule("1", schedule1)
    empty_schedule_repository.create_schedule("2", schedule2)
    assert empty_schedule_repository.list_schedules() == [
        Schedule(id="1", **schedule1.model_dump()),
        Schedule(id="2", **schedule1.model_dump()),
    ]
