from dataclasses import dataclass, field
from typing import Any

from lta.domain.scheduler.notification_pulisher import (
    Notification,
    PushNotificationPublisher,
)


@dataclass
class RecordingNotificationPublisher(PushNotificationPublisher):
    recorder: list[dict[str, Any]] = field(default_factory=list)

    def publish(self, device_token: str, notification: Notification) -> None:
        self.recorder.append(
            dict(
                device_token=device_token,
                title=notification.title,
                message=notification.message,
            )
        )
