from abc import abstractmethod
from datetime import datetime
from typing import Protocol


class NotificationScheduler(Protocol):
    @abstractmethod
    def schedule_notification_for_now(
        self,
        user_id: str,
        notification_title: str,
        notification_message: str,
        when: datetime | None = None,
    ) -> None: ...

    @abstractmethod
    def schedule_notification_for_later(
        self,
        user_id: str,
        notification_title: str,
        notification_message: str,
        when: datetime,
        assignment_id: str | None = None,
    ) -> None: ...
