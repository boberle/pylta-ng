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
        survey_id="survey1",
        user_id="user1",
        created_at=ref_time,
    )
    assignment2 = Assignment(
        id="2",
        survey_id="survey1",
        user_id="user1",
        created_at=ref_time - timedelta(minutes=10),
    )
    assignment3 = Assignment(
        id="3",
        survey_id="survey1",
        user_id="user1",
        created_at=ref_time + timedelta(minutes=10),
    )
    assignment4 = Assignment(
        id="4",
        survey_id="survey1",
        user_id="user2",
        created_at=ref_time,
    )
    for assignment in [assignment1, assignment2, assignment3, assignment4]:
        empty_assignment_repository.create_assignment(
            id=assignment.id,
            survey_id=assignment.survey_id,
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
    empty_assignment_repository.schedule_assignment(
        assignment.user_id, assignment.id, scheduled_for
    )

    got_assignment = empty_assignment_repository.get_assignment(
        assignment.user_id, assignment.id
    )
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
    empty_assignment_repository.publish_assignment(
        assignment.user_id, assignment.id, published_at
    )

    got_assignment = empty_assignment_repository.get_assignment(
        assignment.user_id, assignment.id
    )
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
        created_at=ref_time - timedelta(minutes=10),
    )
    published_and_pending_assignment_user1_c = Assignment(
        id="6",
        survey_id="survey1",
        user_id="user1",
        created_at=ref_time + timedelta(minutes=10),
    )
    published_and_pending_assignment_user2 = Assignment(
        id="7",
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
        published_and_pending_assignment_user1_c,
        published_and_pending_assignment_user2,
    ]:
        empty_assignment_repository.create_assignment(
            id=assignment.id,
            survey_id=assignment.survey_id,
            user_id=assignment.user_id,
            created_at=assignment.created_at,
        )
    empty_assignment_repository.publish_assignment(
        published_and_expired_assignment.user_id,
        published_and_expired_assignment.id,
        published_time_of_expired_assignment,
    )
    empty_assignment_repository.publish_assignment(
        published_and_answered_assignment.user_id,
        published_and_answered_assignment.id,
        published_time,
    )
    empty_assignment_repository.publish_assignment(
        published_and_pending_assignment_user1_a.user_id,
        published_and_pending_assignment_user1_a.id,
        published_time,
    )
    empty_assignment_repository.publish_assignment(
        published_and_pending_assignment_user1_b.user_id,
        published_and_pending_assignment_user1_b.id,
        published_time,
    )
    empty_assignment_repository.publish_assignment(
        published_and_pending_assignment_user1_c.user_id,
        published_and_pending_assignment_user1_c.id,
        published_time,
    )
    empty_assignment_repository.publish_assignment(
        published_and_pending_assignment_user2.user_id,
        published_and_pending_assignment_user2.id,
        published_time,
    )

    empty_assignment_repository.submit_assignment(
        published_and_answered_assignment.user_id,
        published_and_answered_assignment.id,
        when=answer_time,
        answers=["Excellent", [3, 4], 5],
    )

    got_pending_assignment_ids = list(
        map(
            lambda x: x.id,
            empty_assignment_repository.list_pending_assignments("user1", lookup_time),
        )
    )
    assert got_pending_assignment_ids == [
        published_and_pending_assignment_user1_c.id,
        published_and_pending_assignment_user1_a.id,
        published_and_pending_assignment_user1_b.id,
    ]

    assert list(
        map(
            lambda x: x.id,
            empty_assignment_repository.list_pending_assignments("user2", lookup_time),
        )
    ) == [published_and_pending_assignment_user2.id]

    got_pending_assignment = empty_assignment_repository.get_next_pending_assignment(
        "user1", lookup_time
    )
    assert got_pending_assignment is not None
    assert got_pending_assignment.id == published_and_pending_assignment_user1_b.id

    got_pending_assignment = empty_assignment_repository.get_next_pending_assignment(
        "user2", lookup_time
    )
    assert got_pending_assignment is not None
    assert got_pending_assignment.id == published_and_pending_assignment_user2.id

    assert (
        empty_assignment_repository.get_next_pending_assignment("user3", lookup_time)
        is None
    )


def test_count_non_answered_assignments(
    empty_assignment_repository: AssignmentRepository,
) -> None:
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
        survey_id="survey2",
        user_id="user1",
        created_at=datetime.now(tz=timezone.utc),
    )
    assignment4 = Assignment(
        id="4",
        survey_id="survey2",
        user_id="user2",
        created_at=datetime.now(tz=timezone.utc),
    )
    for assignment in [assignment1, assignment2, assignment3, assignment4]:
        empty_assignment_repository.create_assignment(
            id=assignment.id,
            survey_id=assignment.survey_id,
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
        "publish_assignment",
        "schedule_assignment",
        "submit_assignment",
        "get_next_pending_assignment",
    }
    assert (
        set(filter(lambda attr: not attr.startswith("_"), dir(AssignmentRepository)))
        == checked
    )

    assignment1 = Assignment(
        id="1",
        survey_id="survey1",
        user_id="user1",
        created_at=datetime.now(tz=timezone.utc),
    )
    assignment2 = Assignment(
        id="2",
        survey_id="survey2",
        user_id="user2",
        created_at=datetime.now(tz=timezone.utc),
    )
    for assignment in [assignment1, assignment2]:
        empty_assignment_repository.create_assignment(
            id=assignment.id,
            survey_id=assignment.survey_id,
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

    # schedule
    empty_assignment_repository.schedule_assignment(
        assignment1.user_id, assignment1.id, ref_time
    )
    with pytest.raises(AssignmentNotFound):
        empty_assignment_repository.schedule_assignment(
            assignment2.user_id, assignment1.id, ref_time
        )

    # publish
    empty_assignment_repository.publish_assignment(
        assignment1.user_id, assignment1.id, ref_time
    )
    with pytest.raises(AssignmentNotFound):
        empty_assignment_repository.publish_assignment(
            assignment2.user_id, assignment1.id, ref_time
        )

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
