from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from lta.domain.scheduler.notification_scheduler import NotificationScheduler
from lta.domain.scheduler.notification_service import NotificationService
from lta.domain.user_repository import UserRepository


@dataclass
class DirectNotificationScheduler(NotificationScheduler):
    user_repository: UserRepository
    notification_service: NotificationService

    def schedule_notification_for_now(
        self,
        user_id: str,
        notification_title: str,
        notification_message: str,
        when: datetime | None = None,
    ) -> None:
        self.notification_service.notify_user(
            user_id=user_id,
            notification_title=notification_title,
            notification_message=notification_message,
        )

    def schedule_notification_for_later(
        self,
        user_id: str,
        notification_title: str,
        notification_message: str,
        when: datetime,
    ) -> None:
        self.notification_service.notify_user(
            user_id=user_id,
            notification_title=notification_title,
            notification_message=notification_message,
        )


@dataclass
class RecordingDirectNotificationScheduler(DirectNotificationScheduler):
    recorder: list[dict[str, Any]] = field(default_factory=list)

    def schedule_notification_for_now(
        self,
        user_id: str,
        notification_title: str,
        notification_message: str,
        when: datetime | None = None,
    ) -> None:
        self.recorder.append(
            dict(
                dt=when,
                user_id=user_id,
                notification_title=notification_title,
                notification_message=notification_message,
            )
        )
        super().schedule_notification_for_now(
            user_id, notification_title, notification_message, when
        )

    def schedule_notification_for_later(
        self,
        user_id: str,
        notification_title: str,
        notification_message: str,
        when: datetime,
    ) -> None:
        self.recorder.append(
            dict(
                dt=when,
                user_id=user_id,
                notification_title=notification_title,
                notification_message=notification_message,
            )
        )
        super().schedule_notification_for_later(
            user_id, notification_title, notification_message, when
        )
