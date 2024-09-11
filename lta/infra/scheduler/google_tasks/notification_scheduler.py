from dataclasses import dataclass
from datetime import datetime, timezone

from lta.domain.scheduler.notification_scheduler import NotificationScheduler
from lta.infra.tasks_api import CloudTasksAPI


@dataclass
class CloudTasksNotificationScheduler(NotificationScheduler):
    tasks_api: CloudTasksAPI

    def schedule_notification_for_now(
        self,
        user_id: str,
        notification_title: str,
        notification_message: str,
        when: datetime | None = None,
    ) -> None:
        self.tasks_api.create_task(
            payload=dict(
                user_id=user_id,
                notification_title=notification_title,
                notification_message=notification_message,
            ),
            task_id=CloudTasksAPI.generate_task_id(
                user_id,
                when if when is not None else datetime.now(tz=timezone.utc),
                "now",
            ),
        )

    def schedule_notification_for_later(
        self,
        user_id: str,
        notification_title: str,
        notification_message: str,
        when: datetime,
        assignment_id: str | None = None,
    ) -> None:
        self.tasks_api.create_task(
            payload=dict(
                user_id=user_id,
                notification_title=notification_title,
                notification_message=notification_message,
                assignment_id=assignment_id,
            ),
            when=when,
            task_id=CloudTasksAPI.generate_task_id(user_id, when),
        )
