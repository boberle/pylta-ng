from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from lta.domain.group import Group


@dataclass
class GroupNotFound(Exception):
    group_id: str


class GroupRepository(Protocol):
    @abstractmethod
    def list_groups(self) -> list[Group]: ...

    @abstractmethod
    def get_group(self, id: str) -> Group: ...

    @abstractmethod
    def create_group(self, id: str, name: str, created_at: datetime) -> None: ...

    @abstractmethod
    def remove_group(self, id: str) -> None: ...

    @abstractmethod
    def exists(self, id: str) -> bool: ...

    @abstractmethod
    def add_user_to_group(self, group_id: str, user_id: str) -> None: ...

    @abstractmethod
    def remove_user_from_group(self, group_id: str, user_id: str) -> None: ...

    @abstractmethod
    def set_users(self, group_id: str, user_ids: list[str]) -> None: ...
