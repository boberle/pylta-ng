from abc import abstractmethod
from typing import Protocol

from pydantic import BaseModel


class Notification(BaseModel):
    title: str
    message: str


class PushNotificationPublisher(Protocol):
    @abstractmethod
    def publish(self, device_token: str, notification: Notification) -> None: ...


class EmailNotificationPublisher(Protocol):
    @abstractmethod
    def publish(self, recipient_email: str, notification: Notification) -> None: ...
