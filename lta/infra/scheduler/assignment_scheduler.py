from dataclasses import dataclass
from datetime import datetime

from lta.domain.scheduler.assignment_scheduler import AssignmentScheduler
from lta.domain.scheduler.assignment_service import AssignmentService


@dataclass
class DirectAssignmentScheduler(AssignmentScheduler):
    assignment_service: AssignmentService

    def schedule_assignment(self, user_id: str, survey_id: str, when: datetime) -> None:
        self.assignment_service.create_assignment(
            user_id=user_id, survey_id=survey_id, ref_time=when
        )
