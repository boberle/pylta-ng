from abc import abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from pydantic import EmailStr

from lta.domain.user import Device, User


@dataclass
class UserNotFound(Exception):
    user_id: str


class UserRepository(Protocol):
    @abstractmethod
    def list_users(self) -> list[User]: ...

    @abstractmethod
    def get_device_registrations_from_user_id(self, id: str) -> list[Device]: ...

    @abstractmethod
    def get_user(self, id: str) -> User: ...

    @abstractmethod
    def set_device_registration(self, id: str, device: Device) -> None: ...

    @abstractmethod
    def create_user(
        self, id: str, email_address: EmailStr, created_at: datetime
    ) -> None: ...

    @abstractmethod
    def exists(self, id: str) -> bool: ...
