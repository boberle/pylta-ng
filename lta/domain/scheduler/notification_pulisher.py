from abc import abstractmethod
from typing import Protocol

from pydantic import BaseModel


class Notification(BaseModel):
    title: str
    message: str


class NotificationPublisher(Protocol):
    @abstractmethod
    def publish(self, device_token: str, notification: Notification) -> None: ...
