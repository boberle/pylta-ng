import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any, Generator

import pytest

from lta.api.configuration import (
    get_firebase_app,
    get_firestore_client,
    get_project_name,
)
from lta.domain.assignment import (
    Assignment,
    OpenEndedQuestionAnswer,
    SingleQuestionAnswer,
)
from lta.domain.assignment_repository import AssignmentRepository
from lta.infra.repositories.firestore.assignment_repository import (
    FirestoreAssignmentRepository,
)
from lta.infra.repositories.memory.assignment_repository import (
    InMemoryAssignmentRepository,
)


@pytest.fixture()
def sample_assignment_1() -> Assignment:
    return Assignment(
        id="assignment1",
        title="Sample first survey!",
        user_id="user1",
        survey_id="survey1",
        created_at=datetime(2024, 1, 1, 1),
        expired_at=datetime(2024, 1, 2, 1),
    )


@pytest.fixture()
def sample_assignment_2() -> Assignment:
    return Assignment(
        id="assignment2",
        title="Sample first survey!",
        user_id="user1",
        survey_id="survey1",
        created_at=datetime(2024, 1, 1, 1),
        expired_at=datetime(2024, 1, 2, 1),
        submitted_at=datetime(2024, 1, 1, 3),
    )


@pytest.fixture()
def sample_assignment_3() -> Assignment:
    return Assignment(
        id="assignment3",
        title="Sample second survey!",
        user_id="user2",
        survey_id="survey2",
        created_at=datetime(2024, 2, 1, 1),
        expired_at=datetime(2024, 2, 2, 1),
    )


@pytest.fixture()
def prefilled_memory_assignment_repository(
    sample_assignment_1: Assignment,
    sample_assignment_2: Assignment,
    sample_assignment_3: Assignment,
) -> InMemoryAssignmentRepository:
    data: dict[str, dict[str, Assignment]] = defaultdict(dict)
    for assignment in [sample_assignment_1, sample_assignment_2, sample_assignment_3]:
        data[assignment.user_id][assignment.id] = assignment
    return InMemoryAssignmentRepository(data)


@pytest.fixture
def empty_firestore_assignment_repository() -> (
    Generator[AssignmentRepository, None, None]
):
    # TODO: factor
    get_firebase_app()
    yield FirestoreAssignmentRepository(get_firestore_client(use_emulator=True))
    request = urllib.request.Request(
        f"http://localhost:8080/emulator/v1/projects/{get_project_name()}/databases/(default)/documents",
        method="DELETE",
    )
    resp = urllib.request.urlopen(request)
    if resp.status != 200:
        raise RuntimeError("Failed to delete Firestore emulator data")


@pytest.fixture
def empty_memory_assignment_repository() -> InMemoryAssignmentRepository:
    return InMemoryAssignmentRepository()


@pytest.fixture(params=["memory", "firestore"])
def empty_assignment_repository(
    request: Any,
    empty_firestore_assignment_repository: FirestoreAssignmentRepository,
    empty_memory_assignment_repository: InMemoryAssignmentRepository,
) -> Generator[AssignmentRepository, None, None]:
    if request.param == "firestore":
        yield empty_firestore_assignment_repository
    else:
        yield empty_memory_assignment_repository


class AlwaysSubmittedAssignmentRepository(InMemoryAssignmentRepository):
    """
    Like an InMemoryAssignmentRepository, but when creating an assignment,
    the `submitted_at` and `answers` are filled up (with the `created_at` time).
    """

    def get_assignment(self, user_id: str, assignment_id: str) -> Assignment:
        assignment = super().get_assignment(user_id, assignment_id)
        assignment.submitted_at = datetime.now(tz=timezone.utc)
        assignment.answers = [
            SingleQuestionAnswer(selected_index=1),
            SingleQuestionAnswer(selected_index=2),
            OpenEndedQuestionAnswer(value="hello"),
        ]
        return assignment


@pytest.fixture
def always_submitted_assignment_repository() -> AlwaysSubmittedAssignmentRepository:
    return AlwaysSubmittedAssignmentRepository()
