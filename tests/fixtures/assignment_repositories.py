import urllib.request
from typing import Any, Generator

import pytest

from lta.api.configuration import (
    get_firebase_app,
    get_firestore_client,
    get_project_name,
)
from lta.domain.assignment_repository import AssignmentRepository
from lta.infra.repositories.firestore.assignment_repository import (
    FirestoreAssignmentRepository,
)
from lta.infra.repositories.memory.assignment_repository import (
    InMemoryAssignmentRepository,
)


@pytest.fixture()
def prefilled_memory_assignment_repository() -> InMemoryAssignmentRepository:
    raise NotImplementedError("Prefilled memory assignment repository not implemented")


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
def empty_memory_assignment_repository() -> AssignmentRepository:
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
