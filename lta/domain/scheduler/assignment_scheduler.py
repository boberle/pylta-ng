from abc import abstractmethod
from datetime import datetime
from typing import Protocol


class AssignmentScheduler(Protocol):
    @abstractmethod
    def schedule_assignment(
        self, user_id: str, survey_id: str, when: datetime
    ) -> None: ...
