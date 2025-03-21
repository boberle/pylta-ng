from dataclasses import dataclass
from datetime import datetime

from lta.domain.scheduler.assignment_scheduler import AssignmentScheduler
from lta.infra.tasks_api import CloudTasksAPI


@dataclass
class CloudTasksAssignmentScheduler(AssignmentScheduler):
    tasks_api: CloudTasksAPI

    def schedule_assignment(self, user_id: str, survey_id: str, when: datetime) -> None:
        self.tasks_api.create_task(
            payload=dict(user_id=user_id, survey_id=survey_id),
            when=when,
            task_id=CloudTasksAPI.generate_task_id(user_id, survey_id, when),
        )
