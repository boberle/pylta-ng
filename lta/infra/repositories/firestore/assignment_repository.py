from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List, Literal

import pydantic
from google.cloud import firestore
from pydantic import BaseModel

from lta.domain.assignment import AnswerType, Assignment
from lta.domain.assignment_repository import AssignmentNotFound, AssignmentRepository


class StoredAssignment(BaseModel):
    revision: Literal[1] = 1
    id: str
    user_id: str
    survey_id: str
    created_at: datetime
    scheduled_for: datetime | None
    published_at: datetime | None
    expired_at: datetime | None
    notified_at: list[datetime]
    opened_at: list[datetime]
    submitted_at: datetime | None
    answers: str | None

    @classmethod
    def from_domain(cls, assigment: Assignment) -> StoredAssignment:
        return StoredAssignment(
            id=assigment.id,
            user_id=assigment.user_id,
            survey_id=assigment.survey_id,
            created_at=assigment.created_at,
            scheduled_for=assigment.scheduled_for,
            published_at=assigment.published_at,
            expired_at=assigment.expired_at,
            notified_at=assigment.notified_at,
            opened_at=assigment.opened_at,
            submitted_at=assigment.submitted_at,
            answers=cls.serialize_answers(assigment.answers),
        )

    @staticmethod
    def serialize_answers(answers: List[AnswerType] | None) -> str | None:
        return json.dumps(answers) if answers else None

    def to_domain(self) -> Assignment:
        return Assignment(
            id=self.id,
            user_id=self.user_id,
            survey_id=self.survey_id,
            created_at=self.created_at,
            scheduled_for=self.scheduled_for,
            published_at=self.published_at,
            expired_at=self.expired_at,
            notified_at=self.notified_at,
            opened_at=self.opened_at,
            submitted_at=self.submitted_at,
            answers=json.loads(self.answers) if self.answers else None,
        )


@dataclass
class FirestoreAssignmentRepository(AssignmentRepository):
    client: firestore.Client
    collection_name: str = "assignments"
    expiration_delay: timedelta = timedelta(hours=1)

    def get_assignment(self, id: str) -> Assignment:
        doc_ref = self.client.collection(self.collection_name).document(id)
        doc = doc_ref.get()
        if not doc.exists:
            raise AssignmentNotFound(assignment_id=id)
        stored_assignment: StoredAssignment = pydantic.TypeAdapter(
            StoredAssignment
        ).validate_python(doc.to_dict())
        return stored_assignment.to_domain()

    def create_assignment(
        self,
        id: str,
        survey_id: str,
        user_id: str,
        created_at: datetime,
    ) -> None:
        assigment = Assignment(
            id=id,
            survey_id=survey_id,
            user_id=user_id,
            created_at=created_at,
        )
        stored_assignment = StoredAssignment.from_domain(assigment)
        self.client.collection(self.collection_name).document(id).set(
            stored_assignment.model_dump()
        )

    def list_assignments(self, user_id: str) -> List[Assignment]:
        assignments_ref = self.client.collection(self.collection_name)
        docs = assignments_ref.where("user_id", "==", user_id).stream()
        stored_assignments = (
            pydantic.TypeAdapter(StoredAssignment).validate_python(doc.to_dict())
            for doc in docs
        )
        return [
            stored_assignment.to_domain() for stored_assignment in stored_assignments
        ]

    def schedule_assignment(self, id: str, when: datetime) -> None:
        doc_ref = self.client.collection(self.collection_name).document(id)
        doc_ref.update({"scheduled_for": when})

    def publish_assignment(self, id: str, when: datetime) -> None:
        doc_ref = self.client.collection(self.collection_name).document(id)
        expired_at = when + self.expiration_delay
        doc_ref.update({"published_at": when, "expired_at": expired_at})

    def notify_user(self, id: str, when: datetime) -> None:
        doc_ref = self.client.collection(self.collection_name).document(id)
        doc_ref.update({"notified_at": firestore.ArrayUnion([when])})

    def open_assignment(self, id: str, when: datetime) -> None:
        doc_ref = self.client.collection(self.collection_name).document(id)
        doc_ref.update({"opened_at": firestore.ArrayUnion([when])})

    def submit_assignment(
        self, id: str, when: datetime, answers: List[AnswerType]
    ) -> None:
        doc_ref = self.client.collection(self.collection_name).document(id)
        doc_ref.update(
            {
                "submitted_at": when,
                "answers": StoredAssignment.serialize_answers(answers),
            }
        )

    def get_pending_assignments(
        self, user_id: str, ref_time: datetime
    ) -> List[Assignment]:
        assignments_ref = self.client.collection(self.collection_name)
        docs = (
            assignments_ref.where("user_id", "==", user_id)
            .where("expired_at", ">", ref_time)
            .where("submitted_at", "==", None)
        ).stream()
        stored_assignments = (
            pydantic.TypeAdapter(StoredAssignment).validate_python(doc.to_dict())
            for doc in docs
        )
        return [
            stored_assignment.to_domain() for stored_assignment in stored_assignments
        ]
