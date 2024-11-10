from dataclasses import dataclass, field

from lta.domain.schedule import Schedule
from lta.domain.schedule_repository import (
    ScheduleCreation,
    ScheduleNotFound,
    ScheduleRepository,
)


@dataclass
class InMemoryScheduleRepository(ScheduleRepository):
    schedules: dict[str, Schedule] = field(default_factory=dict)

    def get_schedule(self, id: str) -> Schedule:
        try:
            return self.schedules[id]
        except KeyError:
            raise ScheduleNotFound(schedule_id=id)

    def create_schedule(self, id: str, schedule: ScheduleCreation) -> None:
        self.schedules[id] = Schedule(
            id=id,
            active=schedule.active,
            survey_id=schedule.survey_id,
            days=schedule.days,
            time_range=schedule.time_range,
            user_ids=schedule.user_ids,
            group_ids=schedule.group_ids,
            same_time_for_all_users=schedule.same_time_for_all_users,
        )

    def delete_schedule(self, id: str) -> None:
        if id in self.schedules:
            del self.schedules[id]

    def list_schedules(self) -> list[Schedule]:
        return list(self.schedules.values())

    def list_active_schedules(self) -> list[Schedule]:
        return [schedule for schedule in self.schedules.values() if schedule.active]
