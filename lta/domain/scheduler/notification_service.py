from dataclasses import dataclass

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


@dataclass
class NotificationService:
    ios_notification_publisher: NotificationPublisher
    android_notification_publisher: NotificationPublisher
    user_repository: UserRepository
    assignment_repository: AssignmentRepository

    def notify_user(
        self, user_id: str, notification_title: str, notification_message: str
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

    def notify_user_if_assignment_not_submitted(
        self,
        user_id: str,
        assignment_id: str,
        notification_title: str,
        notification_message: str,
    ) -> None:
        assigment = self.assignment_repository.get_assignment(user_id, assignment_id)
        if assigment.submitted_at is None:
            self.notify_user(user_id, notification_title, notification_message)
