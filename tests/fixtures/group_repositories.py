import urllib.request
from typing import Any, Generator

import pytest

from lta.api.configuration import (
    get_firebase_app,
    get_firestore_client,
    get_project_name,
)
from lta.domain.group_repository import GroupRepository
from lta.infra.repositories.firestore.group_repository import FirestoreGroupRepository
from lta.infra.repositories.memory.group_repository import InMemoryGroupRepository


@pytest.fixture
def empty_firestore_group_repository() -> Generator[GroupRepository, None, None]:
    get_firebase_app()
    yield FirestoreGroupRepository(get_firestore_client(use_emulator=True))
    request = urllib.request.Request(
        f"http://localhost:8080/emulator/v1/projects/{get_project_name()}/databases/(default)/documents",
        method="DELETE",
    )
    resp = urllib.request.urlopen(request)
    if resp.status != 200:
        raise RuntimeError("Failed to delete Firestore emulator data")


@pytest.fixture
def empty_memory_group_repository() -> GroupRepository:
    return InMemoryGroupRepository()


@pytest.fixture(params=["memory", "firestore"])
def empty_group_repository(
    request: Any,
    empty_firestore_group_repository: FirestoreGroupRepository,
    empty_memory_group_repository: InMemoryGroupRepository,
) -> Generator[GroupRepository, None, None]:
    if request.param == "firestore":
        yield empty_firestore_group_repository
    else:
        yield empty_memory_group_repository
