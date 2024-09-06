from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from lta.domain.assignment import AnswerType, Assignment


@dataclass
class AssignmentNotFound(Exception):
    assignment_id: str


class AssignmentRepository(Protocol):
    @abstractmethod
    def get_assignment(self, id: str) -> Assignment: ...

    @abstractmethod
    def create_assignment(
        self,
        id: str,
        survey_id: str,
        user_id: str,
        created_at: datetime,
    ) -> None: ...

    @abstractmethod
    def list_assignments(self, user_id: str) -> list[Assignment]: ...

    @abstractmethod
    def schedule_assignment(self, id: str, when: datetime) -> None: ...

    @abstractmethod
    def publish_assignment(self, id: str, when: datetime) -> None: ...

    @abstractmethod
    def notify_user(self, id: str, when: datetime) -> None: ...

    @abstractmethod
    def open_assignment(self, id: str, when: datetime) -> None: ...

    @abstractmethod
    def submit_assignment(
        self, id: str, when: datetime, answers: list[AnswerType]
    ) -> None: ...

    @abstractmethod
    def get_pending_assignments(
        self, user_id: str, ref_time: datetime
    ) -> list[Assignment]: ...
