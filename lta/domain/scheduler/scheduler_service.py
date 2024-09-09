import random
from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta, timezone
from typing import Generator, Protocol

from lta.domain.group_repository import GroupRepository
from lta.domain.schedule_repository import ScheduleRepository
from lta.domain.scheduler.assignment_scheduler import AssignmentScheduler


class SchedulerService(Protocol):
    @abstractmethod
    def schedule_assignments_for_date(self, ref_date: date) -> None: ...


@dataclass
class BasicSchedulerService:
    assignment_scheduler: AssignmentScheduler
    schedule_repository: ScheduleRepository
    group_repository: GroupRepository
    rand: random.Random = field(default_factory=random.Random)

    def schedule_assignments_for_date(self, ref_date: date) -> None:
        schedules = self.schedule_repository.list_active_schedules(ref_date=ref_date)
        for schedule in schedules:
            for time_range in schedule.time_ranges:
                start = convert_time_to_int(time_range.start_time)
                end = convert_time_to_int(time_range.end_time)
                for user_id in self._generate_user_ids(
                    schedule.user_ids, schedule.group_ids
                ):
                    t = convert_int_to_time(self.rand.randint(start, end))
                    dt = datetime.combine(ref_date, t, tzinfo=timezone.utc)
                    self._schedule_assignment(user_id, schedule.survey_id, dt)

    def _schedule_assignment(
        self, user_id: str, survey_id: str, when: datetime
    ) -> None:
        self.assignment_scheduler.schedule_assignment(
            user_id=user_id, survey_id=survey_id, when=when
        )

    def _generate_user_ids(
        self, user_ids: list[str], group_ids: list[str]
    ) -> Generator[str, None, None]:
        for user_id in user_ids:
            yield user_id

        for group_id in group_ids:
            group = self.group_repository.get_group(group_id)
            for user_id in group.user_ids:
                yield user_id


@dataclass
class TestSchedulerService:
    assignment_scheduler: AssignmentScheduler
    test_user_id: str
    test_survey_id: str

    def schedule_assignments_for_date(self, ref_date: date) -> None:
        self.assignment_scheduler.schedule_assignment(
            user_id=self.test_user_id,
            survey_id=self.test_survey_id,
            when=datetime.now(tz=timezone.utc) + timedelta(minutes=1),
        )


def convert_time_to_int(t: time) -> int:
    return t.hour * 3600 + t.minute * 60 + t.second


def convert_int_to_time(i: int) -> time:
    return time(i // 3600, (i % 3600) // 60, i % 60)
