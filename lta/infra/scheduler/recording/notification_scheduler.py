from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from lta.infra.scheduler.direct.notification_scheduler import (
    DirectNotificationScheduler,
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
