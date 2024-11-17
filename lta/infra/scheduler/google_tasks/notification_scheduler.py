from dataclasses import dataclass
from datetime import datetime, timezone

from lta.domain.scheduler.notification_pulisher import NotificationType
from lta.domain.scheduler.notification_scheduler import NotificationScheduler
from lta.infra.tasks_api import CloudTasksAPI


@dataclass
class CloudTasksNotificationScheduler(NotificationScheduler):
    tasks_api: CloudTasksAPI

    def schedule_initial_notification(
        self,
        user_id: str,
        assignment_id: str,
        when: datetime | None = None,
    ) -> None:
        self._schedule_notification(
            user_id=user_id,
            assignment_id=assignment_id,
            notification_type=NotificationType.INITIAL,
            when=when,
        )

    def schedule_reminder_notification(
        self,
        user_id: str,
        assignment_id: str,
        when: datetime,
    ) -> None:
        self._schedule_notification(
            user_id=user_id,
            assignment_id=assignment_id,
            notification_type=NotificationType.REMINDER,
            when=when,
        )

    def _schedule_notification(
        self,
        user_id: str,
        assignment_id: str,
        notification_type: NotificationType,
        when: datetime | None,
    ) -> None:
        self.tasks_api.create_task(
            payload=dict(
                user_id=user_id,
                assignment_id=assignment_id,
                notification_type=notification_type.value,
            ),
            when=when,
            task_id=CloudTasksAPI.generate_task_id(
                user_id,
                when if when is not None else datetime.now(tz=timezone.utc),
                "now",
            ),
        )
