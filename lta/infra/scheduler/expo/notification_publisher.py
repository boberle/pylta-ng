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
class ExpoAPI:
    def send_notification(self, device_token: str, title: str, body: str) -> None:
        response = requests.post(
            url="https://exp.host/--/api/v2/push/send",
            json={
                "to": device_token,
                "title": title,
                "body": body,
            },
        )
        response.raise_for_status()


@dataclass
class ExpoNotificationPublisher(NotificationPublisher):
    expo_api: ExpoAPI
    null_device_token = "__null__"

    def send_notification(
        self,
        user_id: str,
        assignment_id: str,
        user_notification_info: UserNotificationInfo,
        survey_notification_info: SurveyNotificationInfo,
        notification_type: NotificationType,
    ) -> bool:
        notification_set = survey_notification_info.push_notification
        if notification_set is None:
            return False

        if notification_type == NotificationType.INITIAL:
            title = notification_set.initial_notification.title
            body = notification_set.initial_notification.message
        else:
            title = notification_set.reminder_notification.title
            body = notification_set.reminder_notification.message

        devices = user_notification_info.devices
        success = False
        for device in devices:
            if device.token == self.null_device_token:
                continue
            try:
                self.send_push_notification(
                    device_token=device.token,
                    title=title,
                    body=body,
                )
            except HTTPError as e:
                logging.error(
                    "Error when sending Expo notification",
                    extra=dict(
                        json_fields=dict(
                            user_id=user_id,
                            assignment_id=assignment_id,
                            device_token=device.token,
                            notification_title=title,
                            notification_message=body,
                            error_message=str(e),
                        )
                    ),
                )
            else:
                logging.info(
                    "Expo notification sent successfully",
                    extra=dict(
                        json_fields=dict(
                            user_id=user_id,
                            assignment_id=assignment_id,
                            device_token=device.token,
                            notification_title=title,
                            notification_message=body,
                        )
                    ),
                )
                success = True
        return success

    def send_push_notification(self, device_token: str, title: str, body: str) -> None:
        self.expo_api.send_notification(
            device_token=device_token,
            title=title,
            body=body,
        )
