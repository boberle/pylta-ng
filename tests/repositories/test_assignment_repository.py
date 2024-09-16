from datetime import datetime, timedelta, timezone

import pytest

from lta.domain.assignment import AnswerType, Assignment
from lta.domain.assignment_repository import AssignmentNotFound, AssignmentRepository


def test_get_assignment(empty_assignment_repository: AssignmentRepository) -> None:
    created_at = datetime.now(tz=timezone.utc)
    assignment = Assignment(
        id="1",
        title="Assignment 1",
        survey_id="survey1",
        user_id="user1",
        created_at=created_at,
        expired_at=created_at + timedelta(hours=1),
    )
    empty_assignment_repository.create_assignment(
        id=assignment.id,
        survey_id=assignment.survey_id,
        survey_title=assignment.title,
        user_id=assignment.user_id,
        created_at=assignment.created_at,
    )
    assert (
        empty_assignment_repository.get_assignment(assignment.user_id, assignment.id)
        == assignment
    )


def test_get_assignment_not_found(
    empty_assignment_repository: AssignmentRepository,
) -> None:
    with pytest.raises(AssignmentNotFound):
        empty_assignment_repository.get_assignment("user1", "nonexistent")


def test_list_and_count_assignments(
    empty_assignment_repository: AssignmentRepository,
) -> None:
    ref_time = datetime.now(tz=timezone.utc)
    assignment1 = Assignment(
        id="1",
        title="Assignment 1",
        survey_id="survey1",
        user_id="user1",
        created_at=ref_time,
        expired_at=ref_time + timedelta(hours=1),
    )
    assignment2 = Assignment(
        id="2",
        title="Assignment 2",
        survey_id="survey1",
        user_id="user1",
        created_at=ref_time - timedelta(minutes=10),
        expired_at=ref_time + timedelta(minutes=50),
    )
    assignment3 = Assignment(
        id="3",
        title="Assignment 3",
        survey_id="survey1",
        user_id="user1",
        created_at=ref_time + timedelta(minutes=10),
        expired_at=ref_time + timedelta(hours=1, minutes=10),
    )
    assignment4 = Assignment(
        id="4",
        title="Assignment 4",
        survey_id="survey1",
        user_id="user2",
        created_at=ref_time,
        expired_at=ref_time + timedelta(hours=1),
    )
    for assignment in [assignment1, assignment2, assignment3, assignment4]:
        empty_assignment_repository.create_assignment(
            id=assignment.id,
            survey_id=assignment.survey_id,
            survey_title=assignment.title,
            user_id=assignment.user_id,
            created_at=assignment.created_at,
        )

    assert empty_assignment_repository.list_assignments("user1") == [
        assignment3,
        assignment1,
        assignment2,
    ]
    assert empty_assignment_repository.list_assignments("user1", limit=2) == [
        assignment3,
        assignment1,
    ]
    assert empty_assignment_repository.list_assignments("user2") == [assignment4]
    assert empty_assignment_repository.list_assignments("user3") == []

    assert empty_assignment_repository.count_assignments("user1") == 3
    assert empty_assignment_repository.count_assignments("user2") == 1
    assert empty_assignment_repository.count_assignments("user3") == 0


def test_notify_user(empty_assignment_repository: AssignmentRepository) -> None:
    created_at = datetime.now(tz=timezone.utc)
    assignment = Assignment(
        id="1",
        title="Assignment 1",
        survey_id="survey1",
        user_id="user1",
        created_at=created_at,
        expired_at=created_at + timedelta(hours=1),
    )
    empty_assignment_repository.create_assignment(
        id=assignment.id,
        survey_id=assignment.survey_id,
        survey_title=assignment.title,
        user_id=assignment.user_id,
        created_at=assignment.created_at,
    )
    when = datetime.now(tz=timezone.utc)
    empty_assignment_repository.notify_user(assignment.user_id, assignment.id, when)
    assert empty_assignment_repository.get_assignment(
        assignment.user_id, assignment.id
    ).notified_at == [when]

    when2 = when + timedelta(minutes=1)
    empty_assignment_repository.notify_user(assignment.user_id, assignment.id, when2)
    assert empty_assignment_repository.get_assignment(
        assignment.user_id, assignment.id
    ).notified_at == [
        when,
        when2,
    ]


def test_open_assignment(empty_assignment_repository: AssignmentRepository) -> None:
    created_at = datetime.now(tz=timezone.utc)
    assignment = Assignment(
        id="1",
        title="Assignment 1",
        survey_id="survey1",
        user_id="user1",
        created_at=created_at,
        expired_at=created_at + timedelta(hours=1),
    )
    empty_assignment_repository.create_assignment(
        id=assignment.id,
        survey_id=assignment.survey_id,
        survey_title=assignment.title,
        user_id=assignment.user_id,
        created_at=assignment.created_at,
    )
    when = datetime.now(tz=timezone.utc)
    empty_assignment_repository.open_assignment(assignment.user_id, assignment.id, when)
    assert empty_assignment_repository.get_assignment(
        assignment.user_id, assignment.id
    ).opened_at == [when]

    when2 = when + timedelta(minutes=1)
    empty_assignment_repository.open_assignment(
        assignment.user_id, assignment.id, when2
    )
    assert empty_assignment_repository.get_assignment(
        assignment.user_id, assignment.id
    ).opened_at == [
        when,
        when2,
    ]


def test_submit_assignment(empty_assignment_repository: AssignmentRepository) -> None:
    created_at = datetime.now(tz=timezone.utc)
    assignment = Assignment(
        id="1",
        title="Assignment 1",
        survey_id="survey1",
        user_id="user1",
        created_at=created_at,
        expired_at=created_at + timedelta(hours=1),
    )
    empty_assignment_repository.create_assignment(
        id=assignment.id,
        survey_id=assignment.survey_id,
        survey_title=assignment.title,
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
        assignment.user_id,
        assignment.id,
        when=when,
        answers=answers,
    )
    got_assignment = empty_assignment_repository.get_assignment(
        assignment.user_id, assignment.id
    )
    assert got_assignment.submitted_at == when
    assert got_assignment.answers == answers


def test_list_pending_assignments(
    empty_assignment_repository: AssignmentRepository,
) -> None:
    lookup_time = datetime.now(tz=timezone.utc)

    expired_assignment = Assignment(
        id="1",
        title="Assignment 1",
        survey_id="survey1",
        user_id="user1",
        created_at=lookup_time - timedelta(hours=3),
        expired_at=lookup_time - timedelta(hours=2),
    )
    answered_assignment = Assignment(
        id="2",
        title="Assignment 2",
        survey_id="survey1",
        user_id="user1",
        created_at=lookup_time - timedelta(minutes=30),
        expired_at=lookup_time + timedelta(minutes=30),
    )
    pending_assignment_user1_a = Assignment(
        id="4",
        title="Assignment 4",
        survey_id="survey1",
        user_id="user1",
        created_at=lookup_time - timedelta(minutes=10),
        expired_at=lookup_time + timedelta(minutes=50),
    )
    pending_assignment_user1_b = Assignment(
        id="5",
        title="Assignment 5",
        survey_id="survey1",
        user_id="user1",
        created_at=lookup_time - timedelta(minutes=30),
        expired_at=lookup_time + timedelta(minutes=30),
    )
    pending_assignment_user1_c = Assignment(
        id="6",
        title="Assignment 6",
        survey_id="survey1",
        user_id="user1",
        created_at=lookup_time,
        expired_at=lookup_time + timedelta(hours=1),
    )
    pending_assignment_user2 = Assignment(
        id="7",
        title="Assignment 7",
        survey_id="survey1",
        user_id="user2",
        created_at=lookup_time - timedelta(minutes=30),
        expired_at=lookup_time + timedelta(minutes=30),
    )
    for assignment in [
        expired_assignment,
        answered_assignment,
        pending_assignment_user1_a,
        pending_assignment_user1_b,
        pending_assignment_user1_c,
        pending_assignment_user2,
    ]:
        empty_assignment_repository.create_assignment(
            id=assignment.id,
            survey_id=assignment.survey_id,
            survey_title=assignment.title,
            user_id=assignment.user_id,
            created_at=assignment.created_at,
        )

    empty_assignment_repository.submit_assignment(
        answered_assignment.user_id,
        answered_assignment.id,
        when=lookup_time - timedelta(minutes=15),
        answers=["Very good", [1, 2], 3],
    )

    got_pending_assignment_ids = list(
        map(
            lambda x: x.id,
            empty_assignment_repository.list_pending_assignments("user1", lookup_time),
        )
    )
    assert got_pending_assignment_ids == [
        pending_assignment_user1_c.id,
        pending_assignment_user1_a.id,
        pending_assignment_user1_b.id,
    ]

    assert list(
        map(
            lambda x: x.id,
            empty_assignment_repository.list_pending_assignments("user2", lookup_time),
        )
    ) == [pending_assignment_user2.id]

    got_pending_assignment = empty_assignment_repository.get_next_pending_assignment(
        "user1", lookup_time
    )
    assert got_pending_assignment is not None
    assert got_pending_assignment.id == pending_assignment_user1_b.id

    got_pending_assignment = empty_assignment_repository.get_next_pending_assignment(
        "user2", lookup_time
    )
    assert got_pending_assignment is not None
    assert got_pending_assignment.id == pending_assignment_user2.id

    assert (
        empty_assignment_repository.get_next_pending_assignment("user3", lookup_time)
        is None
    )


def test_count_non_answered_assignments(
    empty_assignment_repository: AssignmentRepository,
) -> None:
    created_at = datetime.now(tz=timezone.utc)
    assignment1 = Assignment(
        id="1",
        title="Assignment 1",
        survey_id="survey1",
        user_id="user1",
        created_at=created_at,
        expired_at=created_at + timedelta(hours=1),
    )
    assignment2 = Assignment(
        id="2",
        title="Assignment 2",
        survey_id="survey2",
        user_id="user1",
        created_at=created_at,
        expired_at=created_at + timedelta(hours=1),
    )
    assignment3 = Assignment(
        id="3",
        title="Assignment 3",
        survey_id="survey2",
        user_id="user1",
        created_at=created_at,
        expired_at=created_at + timedelta(hours=1),
    )
    assignment4 = Assignment(
        id="4",
        title="Assignment 4",
        survey_id="survey2",
        user_id="user2",
        created_at=created_at,
        expired_at=created_at + timedelta(hours=1),
    )
    for assignment in [assignment1, assignment2, assignment3, assignment4]:
        empty_assignment_repository.create_assignment(
            id=assignment.id,
            survey_id=assignment.survey_id,
            survey_title=assignment.title,
            user_id=assignment.user_id,
            created_at=assignment.created_at,
        )

    empty_assignment_repository.submit_assignment(
        assignment1.user_id,
        assignment1.id,
        when=datetime.now(tz=timezone.utc),
        answers=["Excellent", [3, 4], 5],
    )

    assert empty_assignment_repository.count_non_answered_assignments("user1") == 2
    assert empty_assignment_repository.count_non_answered_assignments("user2") == 1
    assert empty_assignment_repository.count_non_answered_assignments("user3") == 0


def test_assignment_is_own_by_user(
    empty_assignment_repository: AssignmentRepository,
) -> None:
    """
    This test checks that the assignment request is owned by the user. In other terms, that `user_id` in the parameter
    of the method match the `user_id` in the assignment.

    To test that all the AssignmentRepository methods are checked, and to prevent any oversight when adding a new method,
    all methods checked (or ignored, for some methods, this test doesn't make sense) are listed in the `checked` set below.
    """
    checked = {
        "count_assignments",
        "count_non_answered_assignments",
        "create_assignment",
        "get_assignment",
        "list_assignments",
        "list_pending_assignments",
        "notify_user",
        "open_assignment",
        "submit_assignment",
        "get_next_pending_assignment",
    }
    assert (
        set(filter(lambda attr: not attr.startswith("_"), dir(AssignmentRepository)))
        == checked
    )

    created_at = datetime.now(tz=timezone.utc)
    assignment1 = Assignment(
        id="1",
        title="Assignment 1",
        survey_id="survey1",
        user_id="user1",
        created_at=created_at,
        expired_at=created_at + timedelta(hours=1),
    )
    assignment2 = Assignment(
        id="2",
        title="Assignment 2",
        survey_id="survey2",
        user_id="user2",
        created_at=created_at,
        expired_at=created_at + timedelta(hours=1),
    )
    for assignment in [assignment1, assignment2]:
        empty_assignment_repository.create_assignment(
            id=assignment.id,
            survey_id=assignment.survey_id,
            survey_title=assignment.title,
            user_id=assignment.user_id,
            created_at=assignment.created_at,
        )

    # get
    assert empty_assignment_repository.get_assignment(
        assignment1.user_id, assignment1.id
    )
    with pytest.raises(AssignmentNotFound):
        empty_assignment_repository.get_assignment(assignment2.user_id, assignment1.id)

    ref_time = datetime.now(tz=timezone.utc)

    # notify
    empty_assignment_repository.notify_user(
        assignment1.user_id, assignment1.id, ref_time
    )
    with pytest.raises(AssignmentNotFound):
        empty_assignment_repository.notify_user(
            assignment2.user_id, assignment1.id, ref_time
        )

    # open
    empty_assignment_repository.open_assignment(
        assignment1.user_id, assignment1.id, ref_time
    )
    with pytest.raises(AssignmentNotFound):
        empty_assignment_repository.open_assignment(
            assignment2.user_id, assignment1.id, ref_time
        )

    # submit
    answers: list[AnswerType] = ["Excellent", [3, 4], 5]
    empty_assignment_repository.submit_assignment(
        assignment1.user_id, assignment1.id, ref_time, answers=answers
    )
    with pytest.raises(AssignmentNotFound):
        empty_assignment_repository.submit_assignment(
            assignment2.user_id, assignment1.id, ref_time, answers=answers
        )
