from dataclasses import dataclass, field
from datetime import datetime

from lta.domain.user import Device, User
from lta.domain.user_repository import UserNotFound, UserRepository


@dataclass
class InMemoryUserRepository(UserRepository):
    users: dict[str, User] = field(default_factory=dict)

    def list_users(self) -> list[User]:
        return list(self.users.values())

    def get_device_registrations_from_user_id(self, id: str) -> list[Device]:
        if id not in self.users:
            raise UserNotFound(user_id=id)
        return list(self.users[id].devices)

    def get_user(self, id: str) -> User:
        if id not in self.users:
            raise UserNotFound(user_id=id)
        return self.users[id]

    def set_device_registration(self, id: str, device: Device) -> None:
        if id not in self.users:
            raise UserNotFound(user_id=id)
        for device_ in self.users[id].devices:
            if device_.token == device.token:
                return
        self.users[id].devices.append(device)

    def create_user(self, id: str) -> User:
        user = User(
            id=id, email_address="user@idontexist.net", created_at=datetime.now()
        )
        self.users[id] = user
        return user

    def exists(self, id: str) -> bool:
        return id in self.users
