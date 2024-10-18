from dataclasses import dataclass
from datetime import datetime, timezone

from lta.domain.scheduler.notification_scheduler import NotificationScheduler
from lta.infra.tasks_api import CloudTasksAPI


@dataclass
class CloudTasksNotificationScheduler(NotificationScheduler):
    tasks_api: CloudTasksAPI

    def schedule_initial_notification(
        self,
        user_id: str,
        assignment_id: str,
        notification_title: str,
        notification_message: str,
        when: datetime | None = None,
    ) -> None:
        self._schedule_notification(
            user_id=user_id,
            assignment_id=assignment_id,
            notification_title=notification_title,
            notification_message=notification_message,
            when=when,
            always_send_notification=True,
        )

    def schedule_reminder_notification(
        self,
        user_id: str,
        assignment_id: str,
        notification_title: str,
        notification_message: str,
        when: datetime,
    ) -> None:
        self._schedule_notification(
            user_id=user_id,
            assignment_id=assignment_id,
            notification_title=notification_title,
            notification_message=notification_message,
            when=when,
            always_send_notification=False,
        )

    def _schedule_notification(
        self,
        user_id: str,
        assignment_id: str,
        notification_title: str,
        notification_message: str,
        when: datetime | None,
        always_send_notification: bool,
    ) -> None:
        self.tasks_api.create_task(
            payload=dict(
                user_id=user_id,
                assignment_id=assignment_id,
                notification_title=notification_title,
                notification_message=notification_message,
                always_send_notification=always_send_notification,
            ),
            when=when,
            task_id=CloudTasksAPI.generate_task_id(
                user_id,
                when if when is not None else datetime.now(tz=timezone.utc),
                "now",
            ),
        )
