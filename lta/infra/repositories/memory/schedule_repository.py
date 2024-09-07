from dataclasses import dataclass, field
from datetime import date

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
            **schedule.model_dump(),
        )

    def delete_schedule(self, id: str) -> None:
        if id in self.schedules:
            del self.schedules[id]

    def list_schedules(self) -> list[Schedule]:
        return sorted(
            self.schedules.values(),
            key=lambda schedule: schedule.start_date,
            reverse=True,
        )

    def list_active_schedules(self, ref_date: date) -> list[Schedule]:
        return sorted(
            [
                schedule
                for schedule in self.schedules.values()
                if schedule.start_date <= ref_date <= schedule.end_date
            ],
            key=lambda schedule: schedule.start_date,
            reverse=True,
        )
