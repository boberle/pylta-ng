from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol

from pydantic import BaseModel, Field

from lta.domain.schedule import Day, Schedule, TimeRange


@dataclass
class ScheduleNotFound(Exception):
    schedule_id: str


class ScheduleCreation(BaseModel):
    survey_id: str
    active: bool
    days: list[Day] = Field(default_factory=list)
    time_range: TimeRange
    user_ids: list[str] = Field(default_factory=list)
    group_ids: list[str] = Field(default_factory=list)
    same_time_for_all_users: bool = False


class ScheduleRepository(Protocol):
    @abstractmethod
    def get_schedule(self, id: str) -> Schedule: ...

    @abstractmethod
    def create_schedule(self, id: str, schedule: ScheduleCreation) -> None: ...

    @abstractmethod
    def delete_schedule(self, id: str) -> None: ...

    @abstractmethod
    def list_schedules(self) -> list[Schedule]: ...

    @abstractmethod
    def list_active_schedules(self) -> list[Schedule]: ...
