from datetime import date, time

from pydantic import BaseModel, Field


class TimeRange(BaseModel):
    start_time: time
    end_time: time


class Schedule(BaseModel):
    id: str
    survey_id: str
    start_date: date
    end_date: date
    time_ranges: list[TimeRange]
    user_ids: list[str] = Field(default_factory=list)
    group_ids: list[str] = Field(default_factory=list)
