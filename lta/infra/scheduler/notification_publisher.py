from dataclasses import dataclass, field
from typing import Any

import requests

from lta.domain.scheduler.notification_pulisher import (
    Notification,
    NotificationPublisher,
)


@dataclass
class RecordingNotificationPublisher(NotificationPublisher):
    recorder: list[dict[str, Any]] = field(default_factory=list)

    def publish(self, device_token: str, notification: Notification) -> None:
        self.recorder.append(
            dict(
                device_token=device_token,
                title=notification.title,
                message=notification.message,
            )
        )


class ExpoNotificationPublisher(NotificationPublisher):
    def publish(self, device_token: str, notification: Notification) -> None:
        response = requests.post(
            url="https://exp.host/--/api/v2/push/send",
            json={
                "to": device_token,
                "title": notification.title,
                "body": notification.message,
            },
        )
        print(response.json())
        response.raise_for_status()
        print("Notification sent successfully")
