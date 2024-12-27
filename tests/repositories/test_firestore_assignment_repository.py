import json
from datetime import datetime, timezone

from lta.domain.assignment import (
    SingleQuestionAnswer,
    MultipleQuestionAnswer,
    OpenEndedQuestionAnswer,
)
from lta.infra.repositories.firestore.assignment_repository import StoredAssignment


def test_answer_deserialization_revision_2() -> None:
    stored_assignment = StoredAssignment(
        id="dummy_id",
        title="Dummy Title",
        user_id="dummy_user_id",
        survey_id="dummy_survey_id",
        created_at=datetime.now(tz=timezone.utc),
        expired_at=datetime.now(tz=timezone.utc),
        notified_at=[datetime.now(tz=timezone.utc)],
        opened_at=[datetime.now(tz=timezone.utc)],
        submitted_at=None,
        answers=json.dumps(
            dict(
                revision=2,
                answers=[
                    dict(selected_index=0, specify_answer="abc"),
                    dict(selected_indices=[1, 2], specify_answer=None),
                    dict(value="Sample answer"),
                ],
            )
        ),
    )
    got_answers = stored_assignment.to_domain().answers
    expected_answers = [
        SingleQuestionAnswer(selected_index=0, specify_answer="abc"),
        MultipleQuestionAnswer(selected_indices=[1, 2]),
        OpenEndedQuestionAnswer(value="Sample answer"),
    ]
    assert got_answers == expected_answers


def test_answer_deserialization_revision_1() -> None:
    stored_assignment = StoredAssignment(
        id="dummy_id",
        title="Dummy Title",
        user_id="dummy_user_id",
        survey_id="dummy_survey_id",
        created_at=datetime.now(tz=timezone.utc),
        expired_at=datetime.now(tz=timezone.utc),
        notified_at=[datetime.now(tz=timezone.utc)],
        opened_at=[datetime.now(tz=timezone.utc)],
        submitted_at=None,
        answers=json.dumps(
            [0, [1, 2], "Sample answer"],
        ),
    )
    got_answers = stored_assignment.to_domain().answers
    expected_answers = [
        SingleQuestionAnswer(selected_index=0),
        MultipleQuestionAnswer(selected_indices=[1, 2]),
        OpenEndedQuestionAnswer(value="Sample answer"),
    ]
    assert got_answers == expected_answers
