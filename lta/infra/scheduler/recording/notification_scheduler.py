from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from lta.infra.scheduler.direct.notification_scheduler import (
    DirectNotificationScheduler,
)


@dataclass
class RecordingDirectNotificationScheduler(DirectNotificationScheduler):
    recorder: list[dict[str, Any]] = field(default_factory=list)

    def schedule_initial_notification(
        self,
        user_id: str,
        assignment_id: str,
        notification_title: str,
        notification_message: str,
        when: datetime | None = None,
    ) -> None:
        self.recorder.append(
            dict(
                assignment_id=assignment_id,
                user_id=user_id,
                notification_title=notification_title,
                notification_message=notification_message,
                when=when,
            )
        )
        super().schedule_initial_notification(
            user_id=user_id,
            assignment_id=assignment_id,
            notification_title=notification_title,
            notification_message=notification_message,
            when=when,
        )

    def schedule_reminder_notification(
        self,
        user_id: str,
        assignment_id: str,
        notification_title: str,
        notification_message: str,
        when: datetime,
    ) -> None:
        self.recorder.append(
            dict(
                assignment_id=assignment_id,
                user_id=user_id,
                notification_title=notification_title,
                notification_message=notification_message,
                when=when,
            )
        )
        super().schedule_reminder_notification(
            user_id=user_id,
            assignment_id=assignment_id,
            notification_title=notification_title,
            notification_message=notification_message,
            when=when,
        )
