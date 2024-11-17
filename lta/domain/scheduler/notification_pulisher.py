from abc import abstractmethod
from enum import Enum
from typing import Protocol

from lta.domain.survey import SurveyNotificationInfo
from lta.domain.user import UserNotificationInfo


class NotificationType(str, Enum):
    INITIAL = "initial"
    REMINDER = "reminder"


class NotificationPublisher(Protocol):
    @abstractmethod
    def send_notification(
        self,
        user_id: str,
        assignment_id: str,
        user_notification_info: UserNotificationInfo,
        survey_notification_info: SurveyNotificationInfo,
        notification_type: NotificationType,
    ) -> bool: ...
