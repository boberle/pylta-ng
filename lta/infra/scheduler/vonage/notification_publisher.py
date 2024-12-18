import logging
from dataclasses import dataclass

import vonage

from lta.domain.scheduler.notification_pulisher import (
    NotificationPublisher,
    NotificationType,
)
from lta.domain.survey import SurveyNotificationInfo
from lta.domain.user import UserNotificationInfo


@dataclass
class VonageNotificationPublisher(NotificationPublisher):
    client: vonage.Client
    sender: str

    def send_notification(
        self,
        user_id: str,
        assignment_id: str,
        user_notification_info: UserNotificationInfo,
        survey_notification_info: SurveyNotificationInfo,
        notification_type: NotificationType,
    ) -> bool:
        phone_number = user_notification_info.phone_number
        notification_set = survey_notification_info.sms_notification
        if phone_number is None or notification_set is None:
            return False

        if notification_type == NotificationType.INITIAL:
            notification_message = notification_set.initial_notification.message
        else:
            notification_message = notification_set.reminder_notification.message
        notification_message = notification_message.format(
            user_id=user_id, assignment_id=assignment_id
        )

        sms = vonage.Sms(self.client)
        response_data = sms.send_message(
            {
                "from": self.sender,
                "to": phone_number,
                "text": notification_message,
            }
        )

        if response_data["messages"][0]["status"] == "0":
            logging.info(
                "Vonage SMS sent successfully",
                extra=dict(
                    json_fields=dict(
                        user_id=user_id,
                        assignment_id=assignment_id,
                        phone_number=phone_number,
                        notification_message=notification_message,
                    )
                ),
            )
            return True
        else:
            logging.error(
                "Error when sending Vonage SMS",
                extra=dict(
                    json_fields=dict(
                        user_id=user_id,
                        assignment_id=assignment_id,
                        recipient_phone_number=phone_number,
                        notification_message=notification_message,
                        error_message=response_data["messages"][0]["error-text"],
                    )
                ),
            )
            return False

    def send_sms(
        self,
        phone_number: str,
        message: str,
    ) -> None:
        sms = vonage.Sms(self.client)
        response_data = sms.send_message(
            {
                "from": self.sender,
                "to": phone_number,
                "text": message,
            }
        )

        if response_data["messages"][0]["status"] == "0":
            print("Success")
        else:
            error_message = (response_data["messages"][0]["error-text"],)
            print(f"Error: {error_message}")
