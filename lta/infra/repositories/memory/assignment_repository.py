from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List

from lta.domain.assignment import AnswerType, Assignment
from lta.domain.assignment_repository import (
    AssignmentNotFound,
    AssignmentRepository,
    SubmissionTooLate,
)


@dataclass
class InMemoryAssignmentRepository(AssignmentRepository):
    assignments: dict[str, dict[str, Assignment]] = field(
        default_factory=lambda: defaultdict(dict)
    )
    expiration_delay: timedelta = timedelta(hours=1)

    def _get_assignment(self, user_id: str, id: str) -> Assignment:
        """Return a reference to the object."""
        if user_id not in self.assignments or id not in self.assignments[user_id]:
            raise AssignmentNotFound(user_id=user_id, assignment_id=id)
        return self.assignments[user_id][id]

    def get_assignment(self, user_id: str, id: str) -> Assignment:
        """Return a copy of the object."""
        return self._get_assignment(user_id, id).model_copy()

    def create_assignment(
        self,
        user_id: str,
        id: str,
        survey_id: str,
        survey_title: str,
        created_at: datetime,
    ) -> None:
        assignment = Assignment(
            id=id,
            title=survey_title,
            user_id=user_id,
            survey_id=survey_id,
            created_at=created_at,
            expired_at=created_at + self.expiration_delay,
        )
        self.assignments[user_id][id] = assignment

    def list_assignments(
        self, user_id: str, limit: int | None = None
    ) -> List[Assignment]:
        assignments = [
            assignment.model_copy()
            for assignment in self.assignments[user_id].values()
            if assignment.user_id == user_id
        ]
        assignments = sorted(assignments, key=lambda x: x.created_at, reverse=True)
        if limit is not None:
            assignments = assignments[:limit]
        return assignments

    def count_assignments(self, user_id: str) -> int:
        return len(self.assignments[user_id])

    def notify_user(self, user_id: str, assignment_id: str, when: datetime) -> None:
        assignment = self._get_assignment(user_id, assignment_id)
        assignment.notified_at.append(when)

    def open_assignment(self, user_id: str, assignment_id: str, when: datetime) -> None:
        assignment = self._get_assignment(user_id, assignment_id)
        assignment.opened_at.append(when)

    def submit_assignment(
        self,
        user_id: str,
        assignment_id: str,
        when: datetime,
        answers: List[AnswerType],
    ) -> None:
        assignment = self._get_assignment(user_id, id)
        if when > assignment.expired_at:
            raise SubmissionTooLate(user_id=user_id, assignment_id=id)
        assignment.submitted_at = when
        assignment.answers = answers

    def list_pending_assignments(
        self, user_id: str, ref_time: datetime
    ) -> List[Assignment]:
        assignments = [
            assignment.model_copy()
            for assignment in self.assignments[user_id].values()
            if assignment.user_id == user_id
            and assignment.expired_at is not None
            and assignment.expired_at > ref_time
            and assignment.submitted_at is None
        ]
        return sorted(assignments, key=lambda x: x.created_at, reverse=True)

    def get_next_pending_assignment(
        self, user_id: str, ref_time: datetime
    ) -> Assignment | None:
        pending_assignments = self.list_pending_assignments(user_id, ref_time=ref_time)
        if pending_assignments:
            return pending_assignments[-1]
        return None

    def count_non_answered_assignments(self, user_id: str) -> int:
        return sum(
            not bool(assignment.submitted_at)
            for assignment in self.assignments[user_id].values()
        )
