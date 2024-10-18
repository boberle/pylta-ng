from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from lta.api.configuration import (
    get_assignment_service,
    get_notification_service,
    get_scheduler_service,
    get_test_scheduler_service,
)
from lta.domain.scheduler.assignment_service import AssignmentService
from lta.domain.scheduler.notification_service import (
    AlwaysSendNotificationPolicy,
    NotificationSendingAssignmentNotSubmitterPolicy,
    NotificationSendingPolicy,
    NotificationService,
)
from lta.domain.scheduler.scheduler_service import SchedulerService

router = APIRouter()


@router.get("/schedule-assignments/")
def schedule_assignments(
    ref_date: date = Query(
        default_factory=lambda: (
            datetime.now(tz=timezone.utc) + timedelta(days=1)
        ).date(),
    ),
    test: bool = False,
    scheduler_service: SchedulerService = Depends(get_scheduler_service),
    test_scheduler_service: SchedulerService = Depends(get_test_scheduler_service),
) -> None:
    if test:
        service = test_scheduler_service
    else:
        service = scheduler_service

    service.schedule_assignments_for_date(ref_date=ref_date)


class ScheduleAssignmentRequest(BaseModel):
    user_id: str
    survey_id: str


@router.post("/schedule-assignment/")
def schedule_assignment(
    request: ScheduleAssignmentRequest,
    ref_time: datetime = Query(default_factory=lambda: datetime.now(tz=timezone.utc)),
    assignment_service: AssignmentService = Depends(get_assignment_service),
) -> None:
    assignment_service.create_assignment(
        user_id=request.user_id, survey_id=request.survey_id, ref_time=ref_time
    )


class NotifyUserRequest(BaseModel):
    user_id: str
    notification_title: str
    notification_message: str
    assignment_id: str
    always_send_notification: bool = False


@router.post("/notify-user/")
def notify_user(
    request: NotifyUserRequest,
    notification_service: NotificationService = Depends(get_notification_service),
) -> None:
    notification_policy: NotificationSendingPolicy
    if request.always_send_notification:
        notification_policy = AlwaysSendNotificationPolicy()
    else:
        notification_policy = NotificationSendingAssignmentNotSubmitterPolicy()

    notification_service.notify_user(
        user_id=request.user_id,
        assignment_id=request.assignment_id,
        notification_title=request.notification_title,
        notification_message=request.notification_message,
        policy=notification_policy,
    )
