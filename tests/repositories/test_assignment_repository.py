from datetime import datetime, timedelta, timezone

import pytest

from lta.domain.assignment import AnswerType, Assignment
from lta.domain.assignment_repository import AssignmentNotFound, AssignmentRepository


def test_get_assignment(empty_assignment_repository: AssignmentRepository) -> None:
    assignment = Assignment(
        id="1",
        survey_id="survey1",
        user_id="user1",
        created_at=datetime.now(tz=timezone.utc),
    )
    empty_assignment_repository.create_assignment(
        id=assignment.id,
        survey_id=assignment.survey_id,
        user_id=assignment.user_id,
        created_at=assignment.created_at,
    )
    assert empty_assignment_repository.get_assignment(assignment.id) == assignment


def test_get_assignment_not_found(
    empty_assignment_repository: AssignmentRepository,
) -> None:
    with pytest.raises(AssignmentNotFound):
        empty_assignment_repository.get_assignment("nonexistent")


def test_list_assignments(empty_assignment_repository: AssignmentRepository) -> None:
    assignment1 = Assignment(
        id="1",
        survey_id="survey1",
        user_id="user1",
        created_at=datetime.now(tz=timezone.utc),
    )
    assignment2 = Assignment(
        id="2",
        survey_id="survey2",
        user_id="user1",
        created_at=datetime.now(tz=timezone.utc),
    )
    assignment3 = Assignment(
        id="3",
        survey_id="survey3",
        user_id="user2",
        created_at=datetime.now(tz=timezone.utc),
    )
    for assignment in [assignment1, assignment2, assignment3]:
        empty_assignment_repository.create_assignment(
            id=assignment.id,
            survey_id=assignment.survey_id,
            user_id=assignment.user_id,
            created_at=assignment.created_at,
        )
    assert empty_assignment_repository.list_assignments("user1") == [
        assignment1,
        assignment2,
    ]
    assert empty_assignment_repository.list_assignments("user2") == [assignment3]
    assert empty_assignment_repository.list_assignments("user3") == []


def test_schedule_assignment(empty_assignment_repository: AssignmentRepository) -> None:
    assignment = Assignment(
        id="1",
        survey_id="survey1",
        user_id="user1",
        created_at=datetime.now(tz=timezone.utc),
    )
    empty_assignment_repository.create_assignment(
        id=assignment.id,
        survey_id=assignment.survey_id,
        user_id=assignment.user_id,
        created_at=assignment.created_at,
    )
    scheduled_for = datetime.now(tz=timezone.utc) + timedelta(minutes=1)
    empty_assignment_repository.schedule_assignment(assignment.id, scheduled_for)

    got_assignment = empty_assignment_repository.get_assignment(assignment.id)
    assert got_assignment.scheduled_for == scheduled_for


def test_publish_assignment(empty_assignment_repository: AssignmentRepository) -> None:
    assignment = Assignment(
        id="1",
        survey_id="survey1",
        user_id="user1",
        created_at=datetime.now(tz=timezone.utc),
    )
    empty_assignment_repository.create_assignment(
        id=assignment.id,
        survey_id=assignment.survey_id,
        user_id=assignment.user_id,
        created_at=assignment.created_at,
    )
    published_at = datetime.now(tz=timezone.utc) + timedelta(minutes=1)
    expired_at = published_at + timedelta(hours=1)
    empty_assignment_repository.publish_assignment(assignment.id, published_at)

    got_assignment = empty_assignment_repository.get_assignment(assignment.id)
    assert got_assignment.published_at == published_at
    assert got_assignment.expired_at == expired_at


def test_notify_user(empty_assignment_repository: AssignmentRepository) -> None:
    assignment = Assignment(
        id="1",
        survey_id="survey1",
        user_id="user1",
        created_at=datetime.now(tz=timezone.utc),
    )
    empty_assignment_repository.create_assignment(
        id=assignment.id,
        survey_id=assignment.survey_id,
        user_id=assignment.user_id,
        created_at=assignment.created_at,
    )
    when = datetime.now(tz=timezone.utc)
    empty_assignment_repository.notify_user(assignment.id, when)
    assert empty_assignment_repository.get_assignment(assignment.id).notified_at == [
        when
    ]

    when2 = when + timedelta(minutes=1)
    empty_assignment_repository.notify_user(assignment.id, when2)
    assert empty_assignment_repository.get_assignment(assignment.id).notified_at == [
        when,
        when2,
    ]


def test_open_assignment(empty_assignment_repository: AssignmentRepository) -> None:
    assignment = Assignment(
        id="1",
        survey_id="survey1",
        user_id="user1",
        created_at=datetime.now(tz=timezone.utc),
    )
    empty_assignment_repository.create_assignment(
        id=assignment.id,
        survey_id=assignment.survey_id,
        user_id=assignment.user_id,
        created_at=assignment.created_at,
    )
    when = datetime.now(tz=timezone.utc)
    empty_assignment_repository.open_assignment(assignment.id, when)
    assert empty_assignment_repository.get_assignment(assignment.id).opened_at == [when]

    when2 = when + timedelta(minutes=1)
    empty_assignment_repository.open_assignment(assignment.id, when2)
    assert empty_assignment_repository.get_assignment(assignment.id).opened_at == [
        when,
        when2,
    ]


def test_submit_assignment(empty_assignment_repository: AssignmentRepository) -> None:
    assignment = Assignment(
        id="1",
        survey_id="survey1",
        user_id="user1",
        created_at=datetime.now(tz=timezone.utc),
    )
    empty_assignment_repository.create_assignment(
        id=assignment.id,
        survey_id=assignment.survey_id,
        user_id=assignment.user_id,
        created_at=assignment.created_at,
    )

    answers: list[AnswerType] = [
        "Very good",
        [1, 2],
        3,
    ]
    when = datetime.now(tz=timezone.utc)
    empty_assignment_repository.submit_assignment(
        assignment.id, when=when, answers=answers
    )
    got_assignment = empty_assignment_repository.get_assignment(assignment.id)
    assert got_assignment.submitted_at == when
    assert got_assignment.answers == answers


def test_get_pending_assignments(
    empty_assignment_repository: AssignmentRepository,
) -> None:
    ref_time = datetime.now(tz=timezone.utc)
    published_time = ref_time
    published_time_of_expired_assignment = published_time - timedelta(hours=2)
    answer_time = ref_time + timedelta(minutes=5)
    lookup_time = ref_time + timedelta(minutes=10)

    published_and_expired_assignment = Assignment(
        id="1",
        survey_id="survey1",
        user_id="user1",
        created_at=ref_time,
    )
    published_and_answered_assignment = Assignment(
        id="2",
        survey_id="survey1",
        user_id="user1",
        created_at=ref_time,
    )
    non_published_assignment = Assignment(
        id="3",
        survey_id="survey1",
        user_id="user1",
        created_at=ref_time,
    )
    published_and_pending_assignment_user1_a = Assignment(
        id="4",
        survey_id="survey1",
        user_id="user1",
        created_at=ref_time,
    )
    published_and_pending_assignment_user1_b = Assignment(
        id="5",
        survey_id="survey1",
        user_id="user1",
        created_at=ref_time,
    )
    published_and_pending_assignment_user2 = Assignment(
        id="6",
        survey_id="survey1",
        user_id="user2",
        created_at=ref_time,
    )
    for assignment in [
        published_and_expired_assignment,
        published_and_answered_assignment,
        non_published_assignment,
        published_and_pending_assignment_user1_a,
        published_and_pending_assignment_user1_b,
        published_and_pending_assignment_user2,
    ]:
        empty_assignment_repository.create_assignment(
            id=assignment.id,
            survey_id=assignment.survey_id,
            user_id=assignment.user_id,
            created_at=assignment.created_at,
        )
    empty_assignment_repository.publish_assignment(
        published_and_expired_assignment.id, published_time_of_expired_assignment
    )
    empty_assignment_repository.publish_assignment(
        published_and_answered_assignment.id, published_time
    )
    empty_assignment_repository.publish_assignment(
        published_and_pending_assignment_user1_a.id, published_time
    )
    empty_assignment_repository.publish_assignment(
        published_and_pending_assignment_user1_b.id, published_time
    )
    empty_assignment_repository.publish_assignment(
        published_and_pending_assignment_user2.id, published_time
    )

    empty_assignment_repository.submit_assignment(
        published_and_answered_assignment.id,
        when=answer_time,
        answers=["Excellent", [3, 4], 5],
    )

    got_pending_assignments = empty_assignment_repository.get_pending_assignments(
        "user1", lookup_time
    )
    got_pending_assignment_ids = [
        assignment.id for assignment in got_pending_assignments
    ]
    assert got_pending_assignment_ids == [
        published_and_pending_assignment_user1_a.id,
        published_and_pending_assignment_user1_b.id,
    ]
