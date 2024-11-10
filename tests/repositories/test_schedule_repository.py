from datetime import time

import pytest

from lta.domain.schedule import Day, Schedule, TimeRange
from lta.domain.schedule_repository import (
    ScheduleCreation,
    ScheduleNotFound,
    ScheduleRepository,
)


def test_create_and_get_schedule(empty_schedule_repository: ScheduleRepository) -> None:
    schedule = ScheduleCreation(
        survey_id="survey1",
        active=True,
        days=[Day.MONDAY],
        time_range=TimeRange(
            start_time=time(hour=12, minute=0, second=0),
            end_time=time(hour=12, minute=30, second=0),
        ),
        user_ids=["user1"],
        group_ids=["group1"],
        same_time_for_all_users=True,
    )
    empty_schedule_repository.create_schedule("1", schedule)
    got_schedule = empty_schedule_repository.get_schedule("1")
    assert got_schedule == Schedule(id="1", **schedule.model_dump())

    with pytest.raises(ScheduleNotFound):
        empty_schedule_repository.get_schedule("2")


def test_delete_schedule(empty_schedule_repository: ScheduleRepository) -> None:
    schedule = ScheduleCreation(
        survey_id="survey1",
        active=True,
        days=[Day.MONDAY],
        time_range=TimeRange(
            start_time=time(hour=12, minute=0, second=0),
            end_time=time(hour=12, minute=30, second=0),
        ),
        user_ids=["user1"],
        group_ids=["group1"],
        same_time_for_all_users=True,
    )
    empty_schedule_repository.create_schedule("1", schedule)
    empty_schedule_repository.delete_schedule("1")
    assert empty_schedule_repository.list_schedules() == []


def test_list_schedules_and_active_schedules(
    empty_schedule_repository: ScheduleRepository,
) -> None:
    schedule_creation_1 = ScheduleCreation(
        survey_id="survey1",
        active=True,
        days=[Day.MONDAY],
        time_range=TimeRange(
            start_time=time(hour=12, minute=0, second=0),
            end_time=time(hour=12, minute=30, second=0),
        ),
        user_ids=["user1"],
        group_ids=["group1"],
        same_time_for_all_users=True,
    )
    schedule_creation_2 = ScheduleCreation(
        survey_id="survey1",
        active=False,
        days=[Day.MONDAY],
        time_range=TimeRange(
            start_time=time(hour=12, minute=0, second=0),
            end_time=time(hour=12, minute=30, second=0),
        ),
        user_ids=["user1"],
        group_ids=["group1"],
        same_time_for_all_users=True,
    )

    schedule_1 = Schedule(id="1", **schedule_creation_1.model_dump())
    schedule_2 = Schedule(id="2", **schedule_creation_2.model_dump())

    empty_schedule_repository.create_schedule("1", schedule_creation_1)
    empty_schedule_repository.create_schedule("2", schedule_creation_2)

    assert empty_schedule_repository.list_schedules() == [
        schedule_1,
        schedule_2,
    ]

    assert empty_schedule_repository.list_active_schedules() == [
        schedule_1,
    ]
