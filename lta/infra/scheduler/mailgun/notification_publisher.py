import logging
from dataclasses import dataclass

import requests
from requests import HTTPError

from lta.domain.scheduler.notification_pulisher import (
    NotificationPublisher,
    NotificationType,
)
from lta.domain.survey import SurveyNotificationInfo
from lta.domain.user import UserNotificationInfo


@dataclass
class MailgunAPI:
    api_key: str
    api_url: str

    def send_email(
        self, recipient_email: str, sender: str, subject: str, body: str
    ) -> None:
        response = requests.post(
            self.api_url,
            auth=("api", self.api_key),
            data={
                "from": sender,
                "to": [recipient_email],
                "subject": subject,
                "text": body,
            },
        )
        response.raise_for_status()


@dataclass
class MailgunNotificationPublisher(NotificationPublisher):
    api: MailgunAPI
    sender: str

    def send_notification(
        self,
        user_id: str,
        assignment_id: str,
        user_notification_info: UserNotificationInfo,
        survey_notification_info: SurveyNotificationInfo,
        notification_type: NotificationType,
    ) -> bool:
        email_address = user_notification_info.email_address
        notification_set = survey_notification_info.email_notification
        if email_address is None or notification_set is None:
            return False

        if notification_type == NotificationType.INITIAL:
            notification_title = notification_set.initial_notification.title
            notification_message = notification_set.initial_notification.message
        else:
            notification_title = notification_set.reminder_notification.title
            notification_message = notification_set.reminder_notification.message
        notification_message = notification_message.format(
            user_id=user_id, assignment_id=assignment_id
        )

        try:
            self.send_email(
                recipient_email=email_address,
                subject=notification_title,
                body=notification_message,
            )
        except HTTPError as e:
            logging.error(
                "Error when sending Mailgun email",
                extra=dict(
                    json_fields=dict(
                        user_id=user_id,
                        assignment_id=assignment_id,
                        email_address=email_address,
                        notification_title=notification_title,
                        notification_message=notification_message,
                        error_message=str(e),
                    )
                ),
            )
            return False
        else:
            logging.info(
                "Mailgun email sent successfully",
                extra=dict(
                    json_fields=dict(
                        user_id=user_id,
                        assignment_id=assignment_id,
                        email_address=email_address,
                        notification_title=notification_title,
                        notification_message=notification_message,
                    )
                ),
            )
            return True

    def send_email(
        self,
        recipient_email: str,
        subject: str,
        body: str,
    ) -> None:
        self.api.send_email(
            recipient_email=recipient_email,
            sender=self.sender,
            subject=subject,
            body=body,
        )
