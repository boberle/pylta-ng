from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class DeviceOS(str, Enum):
    ANDROID = "android"
    IOS = "ios"
    WEB = "web"
    WINDOWS = "windows"
    MACOS = "macos"


class Device(BaseModel):
    token: str
    os: DeviceOS
    version: str | None
    connections: list[datetime]

    def add_connection_time(self, connection_time: datetime) -> None:
        self.connections.append(connection_time)


class UserNotificationInfo(BaseModel):
    phone_number: str | None = None
    email_address: EmailStr | None = None
    devices: list[Device] = Field(default_factory=list)


class User(BaseModel):
    id: str
    email_address: EmailStr
    created_at: datetime
    notification_info: UserNotificationInfo = Field(
        default_factory=UserNotificationInfo
    )
