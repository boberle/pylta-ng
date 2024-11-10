from datetime import time
from enum import Enum

from pydantic import BaseModel, Field


class TimeRange(BaseModel):
    start_time: time
    end_time: time


class Day(str, Enum):
    MONDAY = "monday"
    TUESDAY = "tuesday"
    WEDNESDAY = "wednesday"
    THURSDAY = "thursday"
    FRIDAY = "friday"
    SATURDAY = "saturday"
    SUNDAY = "sunday"


class Schedule(BaseModel):
    id: str
    survey_id: str
    active: bool
    days: list[Day] = Field(default_factory=list)
    time_range: TimeRange
    user_ids: list[str] = Field(default_factory=list)
    group_ids: list[str] = Field(default_factory=list)
    same_time_for_all_users: bool = False
