from typing import Literal

from pydantic import BaseModel


class Question(BaseModel):
    message: str


class SingleChoiceQuestion(Question):
    type: Literal["single-choice"] = "single-choice"
    choices: list[str]


class MultipleChoiceQuestion(Question):
    type: Literal["multiple-choice"] = "multiple-choice"
    choices: list[str]


class OpenEndedQuestion(Question):
    type: Literal["open-ended"] = "open-ended"
    max_length: int = 200


class NotificationMessage(BaseModel):
    title: str
    message: str


class Survey(BaseModel):
    id: str
    title: str
    welcome_message: str
    submit_message: str
    publish_notification: NotificationMessage
    soon_to_expire_notification: NotificationMessage
    questions: list[SingleChoiceQuestion | MultipleChoiceQuestion | OpenEndedQuestion]
