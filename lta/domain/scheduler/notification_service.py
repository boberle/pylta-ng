from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime, timezone

from lta.domain.assignment_repository import AssignmentRepository
from lta.domain.scheduler.notification_pulisher import (
    Notification,
    NotificationPublisher,
)
from lta.domain.user import DeviceOS
from lta.domain.user_repository import UserRepository


@dataclass
class UnsupportedOSError(Exception):
    os: DeviceOS


class NotificationSendingPolicy:
    @abstractmethod
    def should_send_notification(
        self,
        assignment_repository: AssignmentRepository,
        user_id: str,
        assignment_id: str,
    ) -> bool: ...


class AlwaysSendNotificationPolicy(NotificationSendingPolicy):
    def should_send_notification(
        self,
        assignment_repository: AssignmentRepository,
        user_id: str,
        assignment_id: str,
    ) -> bool:
        return True


class NotificationSendingAssignmentNotSubmitterPolicy(NotificationSendingPolicy):
    def should_send_notification(
        self,
        assignment_repository: AssignmentRepository,
        user_id: str,
        assignment_id: str,
    ) -> bool:
        assigment = assignment_repository.get_assignment(user_id, assignment_id)
        return assigment.submitted_at is None


@dataclass
class NotificationService:
    ios_notification_publisher: NotificationPublisher
    android_notification_publisher: NotificationPublisher
    user_repository: UserRepository
    assignment_repository: AssignmentRepository

    def notify_user(
        self,
        user_id: str,
        assignment_id: str,
        notification_title: str,
        notification_message: str,
        policy: NotificationSendingPolicy = AlwaysSendNotificationPolicy(),
        notified_at: datetime | None = None,
    ) -> None:
        if not policy.should_send_notification(
            self.assignment_repository, user_id, assignment_id
        ):
            return
        self.send_notification(user_id, notification_title, notification_message)
        self._set_notified_at(
            user_id, assignment_id, notified_at or datetime.now(tz=timezone.utc)
        )

    def _set_notified_at(
        self, user_id: str, assignment_id: str, when: datetime
    ) -> None:
        self.assignment_repository.notify_user(user_id, assignment_id, when=when)

    def send_notification(
        self,
        user_id: str,
        notification_title: str,
        notification_message: str,
    ) -> None:
        devices = self.user_repository.get_device_registrations_from_user_id(user_id)
        for device in devices:
            notification = Notification(
                title=notification_title, message=notification_message
            )
            if device.os == DeviceOS.IOS:
                self.ios_notification_publisher.publish(device.token, notification)
            elif device.os == DeviceOS.ANDROID:
                self.android_notification_publisher.publish(device.token, notification)
            else:
                raise UnsupportedOSError(os=device.os)
