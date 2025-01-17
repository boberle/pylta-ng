from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel

from lta.api.configuration import (
    AppConfiguration,
    get_assignment_service,
    get_configuration,
    get_expo_notification_publisher,
    get_user_repository,
)
from lta.authentication import AuthenticatedUser, get_authenticated_user
from lta.domain.assignment import AnswerType
from lta.domain.assignment_repository import SubmissionTooLate
from lta.domain.scheduler.assignment_service import AssignmentService
from lta.domain.survey import (
    MultipleChoiceQuestion,
    OpenEndedQuestion,
    SingleChoiceQuestion,
)
from lta.domain.survey_repository import TEST_SURVEY_ID
from lta.domain.user import DeviceOS
from lta.domain.user_repository import UserRepository
from lta.infra.scheduler.expo.notification_publisher import ExpoNotificationPublisher

router = APIRouter()


class Assignment(BaseModel):
    id: str
    title: str
    answered: bool
    date: datetime


class PendingAssignment(BaseModel):
    id: str
    expired_at: datetime


class AssignmentListResponse(BaseModel):
    assignments: list[Assignment]
    total_assignments: int
    answered_assignments: int
    pending_assignment: PendingAssignment | None


@router.get("/assignments/")
async def get_assignments(
    when: datetime = Query(default_factory=lambda: datetime.now(timezone.utc)),
    configuration: AppConfiguration = Depends(get_configuration),
    user: AuthenticatedUser = Depends(get_authenticated_user),
) -> AssignmentListResponse:
    assignments = configuration.assignment_repository.list_assignments(
        user.id, limit=configuration.assignment_limit_on_app_home_page
    )
    total_assignments = configuration.assignment_repository.count_assignments(user.id)
    non_answered_assignments = (
        configuration.assignment_repository.count_non_answered_assignments(user.id)
    )
    pending_assignment = (
        configuration.assignment_repository.get_next_pending_assignment(user.id, when)
    )
    return AssignmentListResponse(
        assignments=[
            Assignment(
                id=a.id,
                title=a.title,
                answered=a.answers is not None,
                date=a.created_at,
            )
            for a in assignments
        ],
        total_assignments=total_assignments,
        answered_assignments=total_assignments - non_answered_assignments,
        pending_assignment=(
            PendingAssignment(
                id=pending_assignment.id,
                expired_at=pending_assignment.expired_at,
            )
            if pending_assignment
            else None
        ),
    )


class AssignmentResponse(BaseModel):
    id: str
    welcome_message: str
    submit_message: str
    questions: list[SingleChoiceQuestion | MultipleChoiceQuestion | OpenEndedQuestion]
    expired_at: datetime


@router.get("/assignments/{user_id}/{assignment_id}/")
async def get_assignment_with_user_id(
    assignment_id: str,
    user_id: str,
    configuration: AppConfiguration = Depends(get_configuration),
) -> AssignmentResponse:
    assignment = configuration.assignment_repository.get_assignment(
        user_id, assignment_id
    )
    survey = configuration.survey_repository.get_survey(assignment.survey_id)

    configuration.assignment_repository.open_assignment(
        user_id=user_id,
        id=assignment_id,
        when=datetime.now(tz=timezone.utc),
    )

    return AssignmentResponse(
        id=assignment.id,
        welcome_message=survey.welcome_message,
        submit_message=survey.submit_message,
        questions=survey.questions,
        expired_at=assignment.expired_at,
    )


@router.get("/assignments/{assignment_id}/")
async def get_assignment(
    assignment_id: str,
    configuration: AppConfiguration = Depends(get_configuration),
    user: AuthenticatedUser = Depends(get_authenticated_user),
) -> AssignmentResponse:
    assignment = configuration.assignment_repository.get_assignment(
        user.id, assignment_id
    )
    survey = configuration.survey_repository.get_survey(assignment.survey_id)

    configuration.assignment_repository.open_assignment(
        user_id=user.id,
        id=assignment_id,
        when=datetime.now(tz=timezone.utc),
    )

    return AssignmentResponse(
        id=assignment.id,
        welcome_message=survey.welcome_message,
        submit_message=survey.submit_message,
        questions=survey.questions,
        expired_at=assignment.expired_at,
    )


class SubmitAssignmentAnswersRequest(BaseModel):
    answers: list[AnswerType]


@router.put("/assignments/{user_id}/{assignment_id}/")
async def put_assignment_answers_with_userid(
    request: SubmitAssignmentAnswersRequest,
    assignment_id: str,
    user_id: str,
    when: datetime = Query(default_factory=lambda: datetime.now(timezone.utc)),
    configuration: AppConfiguration = Depends(get_configuration),
) -> None:
    try:
        configuration.assignment_repository.submit_assignment(
            user_id=user_id,
            id=assignment_id,
            when=when,
            answers=request.answers,
        )
    except SubmissionTooLate:
        raise HTTPException(status_code=410)


@router.put("/assignments/{assignment_id}/")
async def put_assignment_answers(
    request: SubmitAssignmentAnswersRequest,
    assignment_id: str,
    when: datetime = Query(default_factory=lambda: datetime.now(timezone.utc)),
    configuration: AppConfiguration = Depends(get_configuration),
    user: AuthenticatedUser = Depends(get_authenticated_user),
) -> None:
    try:
        configuration.assignment_repository.submit_assignment(
            user_id=user.id,
            id=assignment_id,
            when=when,
            answers=request.answers,
        )
    except SubmissionTooLate:
        raise HTTPException(status_code=410)


class DeviceRegistrationRequest(BaseModel):
    token: str
    os: DeviceOS
    connection_time: datetime | None = None
    version: str | None = None


@router.post("/devices/register/")
def register_device(
    request: DeviceRegistrationRequest,
    user_repository: UserRepository = Depends(get_user_repository),
    user: AuthenticatedUser = Depends(get_authenticated_user),
) -> None:
    connection_time = request.connection_time or datetime.now(tz=timezone.utc)

    if not user_repository.exists(user.id):
        user_repository.create_user(
            id=user.id,
            email_address=user.email_address,
            created_at=connection_time,
        )

    user_repository.add_device_registration(
        id=user.id,
        token=request.token,
        os=request.os,
        version=request.version,
        date=connection_time,
    )


@router.get("/schedule-test-assignment/")
def schedule_assignment(
    ref_time: datetime = Query(default_factory=lambda: datetime.now(tz=timezone.utc)),
    user: AuthenticatedUser = Depends(get_authenticated_user),
    assignment_service: AssignmentService = Depends(get_assignment_service),
) -> None:
    assignment_service.create_assignment(
        user_id=user.id,
        survey_id=TEST_SURVEY_ID,
        ref_time=ref_time,
        send_reminder_notifications=False,
    )


@router.get("/test-notification/")
def test_push_notification(
    user: AuthenticatedUser = Depends(get_authenticated_user),
    user_repository: UserRepository = Depends(get_user_repository),
    notification_publisher: ExpoNotificationPublisher = Depends(
        get_expo_notification_publisher
    ),
) -> None:
    devices = user_repository.get_user(user.id).notification_info.devices
    tokens = [device.token for device in devices if device.token != "__null__"]
    for token in tokens:
        notification_publisher.send_push_notification(
            device_token=token,
            title="LTA test notification",
            body="This is a test push notification.",
        )
