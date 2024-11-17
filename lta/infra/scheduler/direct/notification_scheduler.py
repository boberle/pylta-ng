from dataclasses import dataclass
from datetime import datetime

from lta.domain.scheduler.notification_pulisher import NotificationType
from lta.domain.scheduler.notification_scheduler import NotificationScheduler
from lta.domain.scheduler.notification_service import NotificationService
from lta.domain.user_repository import UserRepository


@dataclass
class DirectNotificationScheduler(NotificationScheduler):
    user_repository: UserRepository
    notification_service: NotificationService

    def schedule_initial_notification(
        self,
        user_id: str,
        assignment_id: str,
        when: datetime | None = None,
    ) -> None:
        self.notification_service.notify_user(
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
        self.notification_service.notify_user(
            user_id=user_id,
            assignment_id=assignment_id,
            notification_type=NotificationType.REMINDER,
            when=when,
        )
