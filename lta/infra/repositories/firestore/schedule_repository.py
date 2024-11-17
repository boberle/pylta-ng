from __future__ import annotations

from dataclasses import dataclass
from datetime import time
from typing import Literal

import pydantic
from google.cloud import firestore
from pydantic import BaseModel, ConfigDict, Field

from lta.domain.schedule import Day, Schedule, TimeRange
from lta.domain.schedule_repository import (
    ScheduleCreation,
    ScheduleNotFound,
    ScheduleRepository,
)
from lta.infra.repositories.firestore.utils import make_filter


class StoredSchedule(BaseModel):
    revision: Literal[1] = 1
    id: str
    survey_id: str
    active: bool
    days: list[Day]
    time_range: str
    user_ids: list[str] = Field(default_factory=list)
    group_ids: list[str] = Field(default_factory=list)
    same_time_for_all_users: bool

    model_config = ConfigDict(extra="forbid")

    @staticmethod
    def from_domain(schedule: Schedule) -> StoredSchedule:
        time_range = f"{schedule.time_range.start_time.isoformat()}-{schedule.time_range.end_time.isoformat()}"
        return StoredSchedule(
            id=schedule.id,
            survey_id=schedule.survey_id,
            active=schedule.active,
            days=schedule.days,
            time_range=time_range,
            user_ids=schedule.user_ids,
            group_ids=schedule.group_ids,
            same_time_for_all_users=schedule.same_time_for_all_users,
        )

    def to_domain(self) -> Schedule:
        time_range = TimeRange(
            start_time=time.fromisoformat(self.time_range.split("-")[0]),
            end_time=time.fromisoformat(self.time_range.split("-")[1]),
        )
        return Schedule(
            id=self.id,
            survey_id=self.survey_id,
            active=self.active,
            days=self.days,
            time_range=time_range,
            user_ids=self.user_ids,
            group_ids=self.group_ids,
            same_time_for_all_users=self.same_time_for_all_users,
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
                Schedule(
                    id=id,
                    active=schedule.active,
                    survey_id=schedule.survey_id,
                    days=schedule.days,
                    time_range=schedule.time_range,
                    user_ids=schedule.user_ids,
                    group_ids=schedule.group_ids,
                    same_time_for_all_users=schedule.same_time_for_all_users,
                )
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

    def list_active_schedules(self) -> list[Schedule]:
        collection_ref = self.client.collection(self.collection_name)
        docs = collection_ref.where(filter=make_filter("active", "==", True)).stream()
        stored_schedules = (
            pydantic.TypeAdapter(StoredSchedule).validate_python(doc.to_dict())
            for doc in docs
        )
        return [stored_schedule.to_domain() for stored_schedule in stored_schedules]
