from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from random import Random
from typing import Protocol

from lta.domain.assignment_repository import AssignmentRepository
from lta.domain.scheduler.notification_scheduler import NotificationScheduler
from lta.domain.survey_repository import SurveyRepository
from lta.utils import make_uuid4


class AssignmentService(Protocol):
    @abstractmethod
    def create_assignment(
        self, user_id: str, survey_id: str, ref_time: datetime
    ) -> None: ...


@dataclass
class BasicAssignmentService:
    notification_scheduler: NotificationScheduler
    assignment_repository: AssignmentRepository
    survey_repository: SurveyRepository
    soon_to_expire_notification_delay: timedelta
    rand: Random = field(default_factory=Random)

    def create_assignment(
        self, user_id: str, survey_id: str, ref_time: datetime
    ) -> None:
        self.assignment_repository.create_assignment(
            user_id=user_id,
            id=str(make_uuid4(self.rand)),
            survey_id=survey_id,
            created_at=ref_time,
        )
        survey = self.survey_repository.get_survey(survey_id)

        first_notification_time = ref_time
        self.notification_scheduler.schedule_notification_for_now(
            user_id=user_id,
            notification_title=survey.publish_notification.title,
            notification_message=survey.publish_notification.message,
            when=first_notification_time,
        )

        second_notification_time = ref_time + self.soon_to_expire_notification_delay
        self.notification_scheduler.schedule_notification_for_later(
            user_id=user_id,
            notification_title=survey.soon_to_expire_notification.title,
            notification_message=survey.soon_to_expire_notification.message,
            when=second_notification_time,
        )


@dataclass
class TestAssignmentService:
    notification_scheduler: NotificationScheduler
    test_notification_title: str = "Test Notification Title"
    test_notification_message: str = "Test Notification Message"

    def create_assignment(
        self, user_id: str, survey_id: str, ref_time: datetime
    ) -> None:
        self.notification_scheduler.schedule_notification_for_now(
            user_id=user_id,
            notification_title=self.test_notification_title,
            notification_message=self.test_notification_message,
        )
