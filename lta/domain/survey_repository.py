from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol

from pydantic import BaseModel

from lta.domain.survey import (
    MultipleChoiceQuestion,
    NotificationMessage,
    OpenEndedQuestion,
    SingleChoiceQuestion,
    Survey,
)


@dataclass
class SurveyNotFound(Exception):
    survey_id: str


class SurveyCreation(BaseModel):
    title: str
    welcome_message: str
    submit_message: str
    publish_notification: NotificationMessage
    soon_to_expire_notification: NotificationMessage
    questions: list[SingleChoiceQuestion | MultipleChoiceQuestion | OpenEndedQuestion]


class SurveyRepository(Protocol):
    @abstractmethod
    def get_survey(self, id: str) -> Survey: ...

    @abstractmethod
    def create_survey(self, id: str, survey: SurveyCreation) -> None: ...

    @abstractmethod
    def list_surveys(self) -> list[Survey]: ...
