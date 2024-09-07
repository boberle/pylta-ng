from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, List, Literal

import pydantic
from google.api_core.exceptions import NotFound
from google.cloud import firestore
from pydantic import BaseModel

from lta.domain.assignment import AnswerType, Assignment
from lta.domain.assignment_repository import AssignmentNotFound, AssignmentRepository
from lta.infra.repositories.firestore.utils import get_collection_count, make_filter


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
    user_collection_name: str = "users"
    expiration_delay: timedelta = timedelta(hours=1)

    def get_assignment(self, user_id: str, id: str) -> Assignment:
        doc_ref = self._get_collection_ref(user_id).document(id)
        doc = doc_ref.get()
        if not doc.exists:
            raise AssignmentNotFound(user_id=user_id, assignment_id=id)
        stored_assignment: StoredAssignment = pydantic.TypeAdapter(
            StoredAssignment
        ).validate_python(doc.to_dict())
        return stored_assignment.to_domain()

    def create_assignment(
        self,
        user_id: str,
        id: str,
        survey_id: str,
        created_at: datetime,
    ) -> None:
        assigment = Assignment(
            id=id,
            survey_id=survey_id,
            user_id=user_id,
            created_at=created_at,
        )
        stored_assignment = StoredAssignment.from_domain(assigment)
        self._get_collection_ref(user_id).document(id).set(
            stored_assignment.model_dump()
        )

    def list_assignments(
        self, user_id: str, limit: int | None = None
    ) -> List[Assignment]:
        assignments_ref = self._get_collection_ref(user_id).order_by(
            "created_at", direction=firestore.Query.DESCENDING
        )
        if limit is not None:
            assignments_ref = assignments_ref.limit(limit)

        docs = assignments_ref.where(
            filter=make_filter("user_id", "==", user_id)
        ).stream()
        stored_assignments = (
            pydantic.TypeAdapter(StoredAssignment).validate_python(doc.to_dict())
            for doc in docs
        )
        return [
            stored_assignment.to_domain() for stored_assignment in stored_assignments
        ]

    def count_assignments(self, user_id: str) -> int:
        return get_collection_count(self._get_collection_ref(user_id))

    def schedule_assignment(self, user_id: str, id: str, when: datetime) -> None:
        doc_ref = self._get_collection_ref(user_id).document(id)
        self._update(doc_ref, user_id, id, {"scheduled_for": when})

    def publish_assignment(self, user_id: str, id: str, when: datetime) -> None:
        doc_ref = self._get_collection_ref(user_id).document(id)
        expired_at = when + self.expiration_delay
        self._update(
            doc_ref, user_id, id, {"published_at": when, "expired_at": expired_at}
        )

    def notify_user(self, user_id: str, id: str, when: datetime) -> None:
        doc_ref = self._get_collection_ref(user_id).document(id)
        self._update(
            doc_ref, user_id, id, {"notified_at": firestore.ArrayUnion([when])}
        )

    def open_assignment(self, user_id: str, id: str, when: datetime) -> None:
        doc_ref = self._get_collection_ref(user_id).document(id)
        self._update(doc_ref, user_id, id, {"opened_at": firestore.ArrayUnion([when])})

    def submit_assignment(
        self, user_id: str, id: str, when: datetime, answers: List[AnswerType]
    ) -> None:
        doc_ref = self._get_collection_ref(user_id).document(id)
        self._update(
            doc_ref,
            user_id,
            id,
            {
                "submitted_at": when,
                "answers": StoredAssignment.serialize_answers(answers),
            },
        )

    def list_pending_assignments(
        self, user_id: str, ref_time: datetime
    ) -> List[Assignment]:
        assignments_ref = self._get_collection_ref(user_id)
        docs = (
            assignments_ref.where(filter=make_filter("user_id", "==", user_id))
            .where(filter=make_filter("expired_at", ">", ref_time))
            .where(filter=make_filter("submitted_at", "==", None))
            .order_by("created_at", direction=firestore.Query.DESCENDING)
        ).stream()
        stored_assignments = (
            pydantic.TypeAdapter(StoredAssignment).validate_python(doc.to_dict())
            for doc in docs
        )
        return [
            stored_assignment.to_domain() for stored_assignment in stored_assignments
        ]

    def get_next_pending_assignment(
        self, user_id: str, ref_time: datetime
    ) -> Assignment | None:
        assignments_ref = self._get_collection_ref(user_id)
        docs = (
            assignments_ref.where(filter=make_filter("user_id", "==", user_id))
            .where(filter=make_filter("expired_at", ">", ref_time))
            .where(filter=make_filter("submitted_at", "==", None))
            .order_by("created_at", direction=firestore.Query.ASCENDING)
            .limit(1)
        ).stream()
        stored_assignments = [
            pydantic.TypeAdapter(StoredAssignment).validate_python(doc.to_dict())
            for doc in docs
        ]
        if stored_assignments:
            return stored_assignments[0].to_domain() if stored_assignments else None
        return None

    def count_non_answered_assignments(self, user_id: str) -> int:
        """
        We count the **non-answered** assignments, meaning those that have not been submitted yet, because
        Firestore doesn't support `!= None`, queries, only `== None` ones.  If you really want to count
        answers assignments, you will need to change StoredAssignment to store the number of answers in
        a separate field.  (No need to change the domain Assignment object.)
        """
        return get_collection_count(
            self._get_collection_ref(user_id)
            .where(filter=make_filter("user_id", "==", user_id))
            .where(filter=make_filter("submitted_at", "==", None))
        )

    def _get_collection_ref(self, user_id: str) -> firestore.CollectionReference:
        return (
            self.client.collection(self.user_collection_name)
            .document(user_id)
            .collection(self.collection_name)
        )

    def _update(
        self,
        doc_ref: firestore.DocumentReference,
        user_id: str,
        id: str,
        updates: dict[str, Any],
    ) -> None:
        try:
            doc_ref.update(updates)
        except NotFound:
            raise AssignmentNotFound(user_id=user_id, assignment_id=id)
