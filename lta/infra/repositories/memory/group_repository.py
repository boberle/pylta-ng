from dataclasses import dataclass, field
from datetime import datetime

from lta.domain.group import Group
from lta.domain.group_repository import GroupNotFound, GroupRepository


@dataclass
class InMemoryGroupRepository(GroupRepository):
    groups: dict[str, Group] = field(default_factory=dict)

    def list_groups(self) -> list[Group]:
        return list(self.groups.values())

    def get_group(self, id: str) -> Group:
        if id not in self.groups:
            raise GroupNotFound(group_id=id)
        return self.groups[id]

    def create_group(self, id: str, name: str, created_at: datetime) -> None:
        if id in self.groups:
            raise ValueError(f"Group with id {id} already exists.")
        self.groups[id] = Group(id=id, name=name, user_ids=[])

    def remove_group(self, id: str) -> None:
        if id not in self.groups:
            raise GroupNotFound(group_id=id)
        del self.groups[id]

    def exists(self, id: str) -> bool:
        return id in self.groups

    def add_user_to_group(self, group_id: str, user_id: str) -> None:
        if group_id not in self.groups:
            raise GroupNotFound(group_id=group_id)
        if user_id not in self.groups[group_id].user_ids:
            self.groups[group_id].user_ids.append(user_id)

    def remove_user_from_group(self, group_id: str, user_id: str) -> None:
        if group_id not in self.groups:
            raise GroupNotFound(group_id=group_id)
        if user_id in self.groups[group_id].user_ids:
            self.groups[group_id].user_ids.remove(user_id)
