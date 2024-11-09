import logging
from dataclasses import dataclass

import vonage

from lta.domain.scheduler.notification_pulisher import (
    Notification,
    SMSNotificationPublisher,
)


@dataclass
class VonageSettings:
    api_key: str
    api_secret: str
    sender: str


@dataclass
class VonageNotificationPublisher(SMSNotificationPublisher):
    settings: VonageSettings

    def publish(self, recipient_phone_number: str, notification: Notification) -> None:
        client = vonage.Client(
            key=self.settings.api_key, secret=self.settings.api_secret
        )
        sms = vonage.Sms(client)

        response_data = sms.send_message(
            {
                "from": self.settings.sender,
                "to": recipient_phone_number,
                "text": notification.message,
            }
        )

        if response_data["messages"][0]["status"] == "0":
            logging.info(
                "Message sent successfully",
                extra=dict(
                    json_fields=dict(
                        recipient_phone_number=recipient_phone_number,
                        notification_message=notification.message,
                    )
                ),
            )
        else:
            logging.info(
                "Message sent successfully",
                extra=dict(
                    json_fields=dict(
                        recipient_phone_number=recipient_phone_number,
                        notification_message=notification.message,
                        error_message=response_data["messages"][0]["error-text"],
                    )
                ),
            )
