from dataclasses import dataclass, field
from datetime import datetime, timedelta
from random import Random

from lta.domain.assignment_repository import AssignmentRepository
from lta.domain.scheduler.notification_scheduler import NotificationScheduler
from lta.domain.survey_repository import SurveyRepository
from lta.utils import make_uuid4


@dataclass
class AssignmentService:
    notification_scheduler: NotificationScheduler
    assignment_repository: AssignmentRepository
    survey_repository: SurveyRepository
    reminder_notification_delays: list[timedelta]
    rand: Random = field(default_factory=Random)

    def create_assignment(
        self, user_id: str, survey_id: str, ref_time: datetime
    ) -> None:
        survey = self.survey_repository.get_survey(survey_id)
        assignment_id = str(make_uuid4(self.rand))
        self.assignment_repository.create_assignment(
            user_id=user_id,
            id=assignment_id,
            survey_id=survey_id,
            survey_title=survey.title,
            created_at=ref_time,
        )

        first_notification_time = ref_time
        self.notification_scheduler.schedule_initial_notification(
            user_id=user_id,
            assignment_id=assignment_id,
            when=first_notification_time,
        )

        for delay in self.reminder_notification_delays:
            second_notification_time = ref_time + delay
            self.notification_scheduler.schedule_reminder_notification(
                user_id=user_id,
                assignment_id=assignment_id,
                when=second_notification_time,
            )
