from dataclasses import dataclass
from datetime import datetime

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
        assignment_id: str | None = None,
    ) -> None:
        if assignment_id is not None:
            self.notification_service.notify_user_if_assignment_not_submitted(
                user_id=user_id,
                notification_title=notification_title,
                notification_message=notification_message,
                assignment_id=assignment_id,
            )
        else:
            self.notification_service.notify_user(
                user_id=user_id,
                notification_title=notification_title,
                notification_message=notification_message,
            )
