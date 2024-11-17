from abc import abstractmethod
from datetime import datetime
from typing import Protocol


class NotificationScheduler(Protocol):
    @abstractmethod
    def schedule_initial_notification(
        self,
        user_id: str,
        assignment_id: str,
        when: datetime | None = None,
    ) -> None: ...

    @abstractmethod
    def schedule_reminder_notification(
        self,
        user_id: str,
        assignment_id: str,
        when: datetime,
    ) -> None: ...
