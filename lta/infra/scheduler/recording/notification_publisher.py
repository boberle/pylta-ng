from dataclasses import dataclass, field

from lta.domain.scheduler.notification_pulisher import (
    NotificationPublisher,
    NotificationType,
)
from lta.domain.survey import SurveyNotificationInfo
from lta.domain.user import UserNotificationInfo


@dataclass
class RecordedData:
    user_id: str
    assignment_id: str
    user_notification_info: UserNotificationInfo
    survey_notification_info: SurveyNotificationInfo
    notification_type: NotificationType


@dataclass
class RecordingNotificationPublisher(NotificationPublisher):
    recorder: list[RecordedData] = field(default_factory=list)

    def send_notification(
        self,
        user_id: str,
        assignment_id: str,
        user_notification_info: UserNotificationInfo,
        survey_notification_info: SurveyNotificationInfo,
        notification_type: NotificationType,
    ) -> bool:
        self.recorder.append(
            RecordedData(
                user_id,
                assignment_id,
                user_notification_info,
                survey_notification_info,
                notification_type,
            )
        )
        return True
