import logging
from dataclasses import dataclass

import requests

from lta.domain.scheduler.notification_pulisher import (
    EmailNotificationPublisher,
    Notification,
)


@dataclass
class MailgunSettings:
    api_key: str
    api_url: str
    sender: str


@dataclass
class MailgunNotificationPublisher(EmailNotificationPublisher):
    settings: MailgunSettings

    def publish(self, recipient_email: str, notification: Notification) -> None:
        response = requests.post(
            self.settings.api_url,
            auth=("api", self.settings.api_key),
            data={
                "from": self.settings.sender,
                "to": [recipient_email],
                "subject": notification.title,
                "text": notification.message,
            },
        )
        response.raise_for_status()
        logging.info(f"Sending email to {recipient_email}")
