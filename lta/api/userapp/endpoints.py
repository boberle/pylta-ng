from datetime import datetime, timezone
from typing import cast

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel

from lta.api.configuration import AppConfiguration, get_configuration
from lta.authentication import get_authenticated_user
from lta.domain.assignment import AnswerType
from lta.domain.survey import (
    MultipleChoiceQuestion,
    OpenEndedQuestion,
    SingleChoiceQuestion,
)

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
    when: datetime = Query(default=lambda: datetime.now(timezone.utc)),
    configuration: AppConfiguration = Depends(get_configuration),
    user_id: str = Depends(get_authenticated_user),
) -> AssignmentListResponse:
    assignments = configuration.assignment_repository.list_assignments(
        user_id, limit=configuration.assignment_limit_on_app_home_page
    )
    total_assignments = configuration.assignment_repository.count_assignments(user_id)
    non_answered_assignments = (
        configuration.assignment_repository.count_non_answered_assignments(user_id)
    )
    pending_assignment = (
        configuration.assignment_repository.get_next_pending_assignment(user_id, when)
    )
    return AssignmentListResponse(
        assignments=[
            Assignment(
                id=a.id,
                title="TODO",
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
                expired_at=cast(datetime, pending_assignment.expired_at),
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


@router.get("/assignments/{assignment_id}/")
async def get_assignment(
    assignment_id: str,
    configuration: AppConfiguration = Depends(get_configuration),
    user_id: str = Depends(get_authenticated_user),
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
    )


class SubmitAssignmentAnswersRequest(BaseModel):
    answers: list[AnswerType]


@router.put("/assignments/{assignment_id}/")
async def put_assignment_answers(
    request: SubmitAssignmentAnswersRequest,
    assignment_id: str,
    when: datetime = Query(default=lambda: datetime.now(timezone.utc)),
    configuration: AppConfiguration = Depends(get_configuration),
    user_id: str = Depends(get_authenticated_user),
) -> None:
    configuration.assignment_repository.submit_assignment(
        user_id=user_id,
        id=assignment_id,
        when=when,
        answers=request.answers,
    )
