from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from lta.domain.assignment import AnswerType, Assignment


@dataclass
class AssignmentNotFound(Exception):
    user_id: str
    assignment_id: str


class AssignmentRepository(Protocol):
    @abstractmethod
    def get_assignment(self, user_id: str, id: str) -> Assignment: ...

    @abstractmethod
    def create_assignment(
        self,
        user_id: str,
        id: str,
        survey_id: str,
        created_at: datetime,
    ) -> None: ...

    @abstractmethod
    def list_assignments(
        self, user_id: str, limit: int | None = None
    ) -> list[Assignment]: ...

    @abstractmethod
    def count_assignments(self, user_id: str) -> int: ...

    @abstractmethod
    def notify_user(self, user_id: str, id: str, when: datetime) -> None: ...

    @abstractmethod
    def open_assignment(self, user_id: str, id: str, when: datetime) -> None: ...

    @abstractmethod
    def submit_assignment(
        self, user_id: str, id: str, when: datetime, answers: list[AnswerType]
    ) -> None: ...

    @abstractmethod
    def list_pending_assignments(
        self, user_id: str, ref_time: datetime
    ) -> list[Assignment]: ...

    def get_next_pending_assignment(
        self, user_id: str, ref_time: datetime
    ) -> Assignment | None: ...

    def count_non_answered_assignments(self, user_id: str) -> int: ...
