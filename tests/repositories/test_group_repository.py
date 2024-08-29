from datetime import datetime, timezone

import pytest

from lta.domain.group_repository import GroupNotFound, GroupRepository


def test_list_groups(empty_group_repository: GroupRepository) -> None:
    empty_group_repository.create_group(
        "group1", "Group 1", datetime.now(tz=timezone.utc)
    )
    empty_group_repository.create_group(
        "group2", "Group 2", datetime.now(tz=timezone.utc)
    )

    groups = empty_group_repository.list_groups()
    assert len(groups) == 2
    assert any(group.id == "group1" for group in groups)
    assert any(group.id == "group2" for group in groups)


def test_get_group(empty_group_repository: GroupRepository) -> None:
    empty_group_repository.create_group(
        "group1", "Group 1", datetime.now(tz=timezone.utc)
    )
    group = empty_group_repository.get_group("group1")
    assert group.id == "group1"
    assert group.name == "Group 1"

    with pytest.raises(GroupNotFound):
        empty_group_repository.get_group("nonexistent_group")


def test_create_group(empty_group_repository: GroupRepository) -> None:
    empty_group_repository.create_group(
        "group1", "Group 1", datetime.now(tz=timezone.utc)
    )
    group = empty_group_repository.get_group("group1")
    assert group.id == "group1"
    assert group.name == "Group 1"

    with pytest.raises(ValueError):
        empty_group_repository.create_group(
            "group1", "Group 1", datetime.now(tz=timezone.utc)
        )


def test_remove_group(empty_group_repository: GroupRepository) -> None:
    empty_group_repository.create_group(
        "group1", "Group 1", datetime.now(tz=timezone.utc)
    )
    empty_group_repository.remove_group("group1")

    with pytest.raises(GroupNotFound):
        empty_group_repository.get_group("group1")

    with pytest.raises(GroupNotFound):
        empty_group_repository.remove_group("nonexistent_group")


def test_exists(empty_group_repository: GroupRepository) -> None:
    empty_group_repository.create_group(
        "group1", "Group 1", datetime.now(tz=timezone.utc)
    )
    assert empty_group_repository.exists("group1")
    assert not empty_group_repository.exists("nonexistent_group")


def test_add_user_to_group(empty_group_repository: GroupRepository) -> None:
    empty_group_repository.create_group(
        "group1", "Group 1", datetime.now(tz=timezone.utc)
    )
    empty_group_repository.add_user_to_group("group1", "user1")
    group = empty_group_repository.get_group("group1")
    assert "user1" in group.user_ids

    with pytest.raises(GroupNotFound):
        empty_group_repository.add_user_to_group("nonexistent_group", "user1")


def test_remove_user_from_group(empty_group_repository: GroupRepository) -> None:
    empty_group_repository.create_group(
        "group1", "Group 1", datetime.now(tz=timezone.utc)
    )
    empty_group_repository.add_user_to_group("group1", "user1")
    empty_group_repository.remove_user_from_group("group1", "user1")
    group = empty_group_repository.get_group("group1")
    assert "user1" not in group.user_ids

    with pytest.raises(GroupNotFound):
        empty_group_repository.remove_user_from_group("nonexistent_group", "user1")
