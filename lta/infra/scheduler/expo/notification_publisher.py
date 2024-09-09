import requests

from lta.domain.scheduler.notification_pulisher import (
    Notification,
    NotificationPublisher,
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
