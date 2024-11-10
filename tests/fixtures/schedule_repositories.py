import urllib.request
from datetime import time
from typing import Any, Generator

import pytest

from lta.api.configuration import (
    get_firebase_app,
    get_firestore_client,
    get_project_name,
)
from lta.domain.schedule import Day, Schedule, TimeRange
from lta.domain.schedule_repository import ScheduleRepository
from lta.infra.repositories.firestore.schedule_repository import (
    FirestoreScheduleRepository,
)
from lta.infra.repositories.memory.schedule_repository import InMemoryScheduleRepository


@pytest.fixture()
def prefilled_memory_schedule_repository() -> InMemoryScheduleRepository:
    return InMemoryScheduleRepository(
        {
            "schedule1": Schedule(
                id="1",
                survey_id="survey1",
                active=True,
                days=[Day.MONDAY],
                time_range=TimeRange(start_time=time(9, 0, 0), end_time=time(10, 0, 0)),
                group_ids=["group1"],
                same_time_for_all_users=True,
            ),
            "schedule2": Schedule(
                id="2",
                survey_id="survey1",
                active=True,
                days=[Day.MONDAY],
                time_range=TimeRange(start_time=time(9, 0, 0), end_time=time(10, 0, 0)),
                group_ids=["group1"],
                same_time_for_all_users=False,
            ),
            "schedule3": Schedule(
                id="3",
                survey_id="survey1",
                active=False,
                days=[Day.THURSDAY],
                time_range=TimeRange(start_time=time(9, 0, 0), end_time=time(10, 0, 0)),
                group_ids=["group1"],
                same_time_for_all_users=False,
            ),
        }
    )


@pytest.fixture
def empty_firestore_schedule_repository() -> Generator[ScheduleRepository, None, None]:
    # TODO: factor
    get_firebase_app()
    yield FirestoreScheduleRepository(get_firestore_client(use_emulator=True))
    request = urllib.request.Request(
        f"http://localhost:8080/emulator/v1/projects/{get_project_name()}/databases/(default)/documents",
        method="DELETE",
    )
    resp = urllib.request.urlopen(request)
    if resp.status != 200:
        raise RuntimeError("Failed to delete Firestore emulator data")


@pytest.fixture
def empty_memory_schedule_repository() -> ScheduleRepository:
    return InMemoryScheduleRepository()


@pytest.fixture(params=["memory", "firestore"])
def empty_schedule_repository(
    request: Any,
    empty_firestore_schedule_repository: FirestoreScheduleRepository,
    empty_memory_schedule_repository: InMemoryScheduleRepository,
) -> Generator[ScheduleRepository, None, None]:
    if request.param == "firestore":
        yield empty_firestore_schedule_repository
    else:
        yield empty_memory_schedule_repository
