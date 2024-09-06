from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import List

from lta.domain.assignment import AnswerType, Assignment
from lta.domain.assignment_repository import AssignmentNotFound, AssignmentRepository


@dataclass
class InMemoryAssignmentRepository(AssignmentRepository):
    assignments: dict[str, Assignment]
    expiration_delay: timedelta = timedelta(hours=1)

    def get_assignment(self, id: str) -> Assignment:
        if id not in self.assignments:
            raise AssignmentNotFound(assignment_id=id)
        return self.assignments[id]

    def create_assignment(
        self,
        id: str,
        survey_id: str,
        user_id: str,
        created_at: datetime,
    ) -> None:
        assignment = Assignment(
            id=id,
            user_id=user_id,
            survey_id=survey_id,
            created_at=created_at,
        )
        self.assignments[id] = assignment

    def list_assignments(self, user_id: str) -> List[Assignment]:
        return [
            assignment
            for assignment in self.assignments.values()
            if assignment.user_id == user_id
        ]

    def schedule_assignment(self, assignment_id: str, when: datetime) -> None:
        assignment = self.get_assignment(assignment_id)
        assignment.scheduled_for = when

    def publish_assignment(self, assignment_id: str, when: datetime) -> None:
        assignment = self.get_assignment(assignment_id)
        assignment.published_at = when
        assignment.expired_at = when + self.expiration_delay

    def notify_user(self, assignment_id: str, when: datetime) -> None:
        assignment = self.get_assignment(assignment_id)
        assignment.notified_at.append(when)

    def open_assignment(self, assignment_id: str, when: datetime) -> None:
        assignment = self.get_assignment(assignment_id)
        assignment.opened_at.append(when)

    def submit_assignment(
        self, assignment_id: str, when: datetime, answers: List[AnswerType]
    ) -> None:
        assignment = self.get_assignment(assignment_id)
        assignment.submitted_at = when
        assignment.answers = answers

    def get_pending_assignments(
        self, user_id: str, ref_date: datetime
    ) -> List[Assignment]:
        return [
            assignment
            for assignment in self.assignments.values()
            if assignment.user_id == user_id
            and assignment.expired_at is not None
            and assignment.expired_at > ref_date
            and assignment.submitted_at is None
        ]
