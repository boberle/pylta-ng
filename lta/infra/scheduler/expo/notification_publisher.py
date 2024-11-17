from lta.domain.scheduler.notification_pulisher import (
    NotificationPublisher,
    NotificationType,
)
from lta.domain.survey import SurveyNotificationInfo
from lta.domain.user import UserNotificationInfo


class ExpoNotificationPublisher(NotificationPublisher):
    def send_notification(
        self,
        user_id: str,
        assignment_id: str,
        user_notification_info: UserNotificationInfo,
        survey_notification_info: SurveyNotificationInfo,
        notification_type: NotificationType,
    ) -> bool:
        """
        Previous version was:

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
        """
        raise NotImplementedError(
            "ExpoNotificationPublisher.send_notification is not implemented"
        )
