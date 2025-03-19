from dataclasses import dataclass, field
from datetime import datetime

from pydantic import EmailStr

from lta.domain.user import Device, DeviceOS, User, UserNotificationInfo
from lta.domain.user_repository import UserNotFound, UserRepository


@dataclass
class InMemoryUserRepository(UserRepository):
    users: dict[str, User] = field(default_factory=dict)

    def list_users(self) -> list[User]:
        return list(self.users.values())

    def get_device_registrations_from_user_id(self, id: str) -> list[Device]:
        if id not in self.users:
            raise UserNotFound(user_id=id)
        return list(self.users[id].notification_info.devices)

    def get_user(self, id: str) -> User:
        if id not in self.users:
            raise UserNotFound(user_id=id)
        return self.users[id]

    def add_device_registration(
        self, id: str, token: str, os: DeviceOS, version: str | None, date: datetime
    ) -> None:
        if id not in self.users:
            raise UserNotFound(user_id=id)

        for device in self.users[id].notification_info.devices:
            if device.token == token:
                device.add_connection_time(date)
                return

        self.users[id].notification_info.devices.append(
            Device(
                token=token,
                os=os,
                version=version,
                connections=[date],
            )
        )

    def create_user(
        self,
        id: str,
        email_address: EmailStr,
        created_at: datetime,
        notification_email: EmailStr | None = None,
        phone_number: str | None = None,
    ) -> None:
        user = User(
            id=id,
            email_address=email_address,
            created_at=created_at,
            notification_info=UserNotificationInfo(
                email_address=notification_email,
                phone_number=phone_number,
            ),
        )
        self.users[id] = user

    def exists(self, id: str) -> bool:
        return id in self.users
