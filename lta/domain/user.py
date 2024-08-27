from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field


class DeviceOS(str, Enum):
    ANDROID = "android"
    IOS = "ios"
    WEB = "web"


class Device(BaseModel):
    token: str
    os: DeviceOS
    version: str | None
    connection: datetime


class User(BaseModel):
    id: str
    email_address: EmailStr
    devices: list[Device] = Field(default_factory=list)
    created_at: datetime
