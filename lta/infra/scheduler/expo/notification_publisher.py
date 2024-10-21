import logging

import requests

from lta.domain.scheduler.notification_pulisher import (
    Notification,
    PushNotificationPublisher,
)


class ExpoNotificationPublisher(PushNotificationPublisher):
    def publish(self, device_token: str, notification: Notification) -> None:
        response = requests.post(
            url="https://exp.host/--/api/v2/push/send",
            json={
                "to": device_token,
                "title": notification.title,
                "body": notification.message,
            },
        )
        logging.info(
            "Notification: Expo response:", extra=dict(json_fields=response.json())
        )
        response.raise_for_status()
        logging.info("Notification sent successfully")
