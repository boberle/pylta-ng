from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from pydantic import BaseModel, Field

from lta.domain.schedule import Schedule, TimeRange


@dataclass
class ScheduleNotFound(Exception):
    schedule_id: str


class ScheduleCreation(BaseModel):
    survey_id: str
    start_date: datetime
    end_date: datetime
    time_ranges: list[TimeRange]
    user_ids: list[str] = Field(default_factory=list)
    group_ids: list[str] = Field(default_factory=list)


class ScheduleRepository(Protocol):
    @abstractmethod
    def get_schedule(self, id: str) -> Schedule: ...

    @abstractmethod
    def create_schedule(self, id: str, schedule: ScheduleCreation) -> None: ...

    @abstractmethod
    def delete_schedule(self, id: str) -> None: ...

    @abstractmethod
    def list_schedules(self) -> list[Schedule]: ...
