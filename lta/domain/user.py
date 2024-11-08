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
    first_connection: datetime
    last_connection: datetime

    def add_connection_time(self, connection_time: datetime) -> None:
        self.last_connection = connection_time


class User(BaseModel):
    id: str
    email_address: EmailStr
    devices: list[Device] = Field(default_factory=list)
    created_at: datetime
    notification_email: EmailStr | None = None
