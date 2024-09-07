from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time
from typing import Literal

import pydantic
from google.cloud import firestore
from pydantic import BaseModel, Field

from lta.domain.schedule import Schedule, TimeRange
from lta.domain.schedule_repository import (
    ScheduleCreation,
    ScheduleNotFound,
    ScheduleRepository,
)


class StoredSchedule(BaseModel):
    revision: Literal[1] = 1
    id: str
    survey_id: str
    start_date: datetime
    end_date: datetime
    time_ranges: list[str]
    user_ids: list[str] = Field(default_factory=list)
    group_ids: list[str] = Field(default_factory=list)

    @staticmethod
    def from_domain(schedule: Schedule) -> StoredSchedule:
        time_ranges = [
            f"{tr.start_time.isoformat()}-{tr.end_time.isoformat()}"
            for tr in schedule.time_ranges
        ]
        return StoredSchedule(
            id=schedule.id,
            survey_id=schedule.survey_id,
            start_date=schedule.start_date,
            end_date=schedule.end_date,
            time_ranges=time_ranges,
            user_ids=schedule.user_ids,
            group_ids=schedule.group_ids,
        )

    def to_domain(self) -> Schedule:
        time_ranges = [
            TimeRange(
                start_time=time.fromisoformat(tr.split("-")[0]),
                end_time=time.fromisoformat(tr.split("-")[1]),
            )
            for tr in self.time_ranges
        ]
        return Schedule(
            id=self.id,
            survey_id=self.survey_id,
            start_date=self.start_date,
            end_date=self.end_date,
            time_ranges=time_ranges,
            user_ids=self.user_ids,
            group_ids=self.group_ids,
        )


@dataclass
class FirestoreScheduleRepository(ScheduleRepository):
    client: firestore.Client = firestore.Client()
    collection_name: str = "schedules"

    def get_schedule(self, id: str) -> Schedule:
        doc_ref = self.client.collection(self.collection_name).document(id)
        doc = doc_ref.get()
        if not doc.exists:
            raise ScheduleNotFound(schedule_id=id)
        stored_schedule = pydantic.TypeAdapter(StoredSchedule).validate_python(
            doc.to_dict()
        )
        return stored_schedule.to_domain()

    def create_schedule(self, id: str, schedule: ScheduleCreation) -> None:
        doc_ref = self.client.collection(self.collection_name).document(id)
        doc_ref.set(
            StoredSchedule.from_domain(
                Schedule(id=id, **schedule.model_dump())
            ).model_dump()
        )

    def delete_schedule(self, id: str) -> None:
        doc_ref = self.client.collection(self.collection_name).document(id)
        doc = doc_ref.get()
        if doc.exists:
            doc_ref.delete()

    def list_schedules(self) -> list[Schedule]:
        collection_ref = self.client.collection(self.collection_name)
        docs = collection_ref.stream()
        stored_schedules = (
            pydantic.TypeAdapter(StoredSchedule).validate_python(doc.to_dict())
            for doc in docs
        )
        return [stored_schedule.to_domain() for stored_schedule in stored_schedules]
