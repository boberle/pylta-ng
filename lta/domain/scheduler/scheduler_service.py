import logging
import random
from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta, timezone
from typing import Generator, Optional, Protocol

from lta.domain.group_repository import GroupRepository
from lta.domain.schedule import Day, Schedule, TimeRange
from lta.domain.schedule_repository import ScheduleRepository
from lta.domain.scheduler.assignment_scheduler import AssignmentScheduler


class SchedulerService(Protocol):
    @abstractmethod
    def schedule_assignments(self, ref_time: datetime) -> None: ...


@dataclass
class BasicSchedulerService(SchedulerService):
    assignment_scheduler: AssignmentScheduler
    schedule_repository: ScheduleRepository
    group_repository: GroupRepository
    rand: random.Random = field(default_factory=random.Random)

    def schedule_assignments(self, ref_time: datetime) -> None:
        schedules = self.schedule_repository.list_active_schedules()
        for schedule in schedules:
            self.schedule_assignment(schedule, ref_time)

    def schedule_assignment(self, schedule: Schedule, ref_time: datetime) -> None:
        if schedule.same_time_for_all_users:
            when = self._get_random_datetime(schedule, ref_time)
            if when is None:
                return
            for user_id in self._generate_user_ids(
                schedule.user_ids, schedule.group_ids
            ):
                self._schedule_assignment(user_id, schedule.survey_id, when)

        else:
            for user_id in self._generate_user_ids(
                schedule.user_ids, schedule.group_ids
            ):
                when = self._get_random_datetime(schedule, ref_time)
                if when is None:
                    continue
                self._schedule_assignment(user_id, schedule.survey_id, when)

    def _get_random_datetime(
        self, schedule: Schedule, ref_time: datetime
    ) -> datetime | None:
        rv = get_random_datetime(
            ref_time=ref_time,
            days=schedule.days,
            time_range=schedule.time_range,
            rand=self.rand,
        )
        if rv is None:
            logging.warning(f"No valid time range found for schedule {schedule.id}")
        return rv

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
class DatetimeRange:
    start: datetime
    end: datetime


def get_random_datetime(
    ref_time: datetime, days: list[Day], time_range: TimeRange, rand: random.Random
) -> Optional[datetime]:
    dates: list[date] = get_dates_from_days(ref_time, days)
    ranges: list[DatetimeRange] = get_datetime_ranges_from_dates_and_time_range(
        dates, time_range
    )
    ranges = keep_ranges_after_ref_time(ref_time, ranges)

    if not ranges:
        return None

    range_: DatetimeRange = rand.choice(ranges)
    start = int(range_.start.timestamp())
    end = int(range_.end.timestamp())
    t = rand.randint(start, end)
    return datetime.fromtimestamp(t, tz=range_.start.tzinfo)


def get_dates_from_days(ref_time: datetime, days: list[Day]) -> list[date]:
    monday = get_previous_monday(ref_time)
    offsets = {
        Day.MONDAY: 0,
        Day.TUESDAY: 1,
        Day.WEDNESDAY: 2,
        Day.THURSDAY: 3,
        Day.FRIDAY: 4,
        Day.SATURDAY: 5,
        Day.SUNDAY: 6,
    }
    return [monday + timedelta(days=offsets[day]) for day in days]


def get_previous_monday(ref_time: datetime) -> date:
    days_since_monday = ref_time.weekday()
    monday = (ref_time - timedelta(days=days_since_monday)).date()
    return monday


def get_datetime_ranges_from_dates_and_time_range(
    dates: list[date], time_range: TimeRange
) -> list[DatetimeRange]:
    rv: list[DatetimeRange] = []
    for date_ in dates:
        start = datetime.combine(date_, time_range.start_time, tzinfo=timezone.utc)
        end = datetime.combine(date_, time_range.end_time, tzinfo=timezone.utc)
        rv.append(DatetimeRange(start, end))
    return rv


def keep_ranges_after_ref_time(
    ref_time: datetime, ranges: list[DatetimeRange]
) -> list[DatetimeRange]:
    rv: list[DatetimeRange] = []
    for range_ in ranges:
        if range_.start >= ref_time:
            rv.append(range_)
        elif range_.end >= ref_time:
            rv.append(DatetimeRange(ref_time, range_.end))
    return rv
