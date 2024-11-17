from abc import abstractmethod
from dataclasses import dataclass
from typing import Protocol

from pydantic import BaseModel, Field

from lta.domain.survey import (
    MultipleChoiceQuestion,
    OpenEndedQuestion,
    SingleChoiceQuestion,
    Survey,
    SurveyNotificationInfo,
    get_test_survey,
)

TEST_SURVEY_ID = "__test__"


@dataclass
class SurveyNotFound(Exception):
    survey_id: str


class SurveyCreation(BaseModel):
    title: str
    welcome_message: str
    submit_message: str
    questions: list[SingleChoiceQuestion | MultipleChoiceQuestion | OpenEndedQuestion]
    notification_info: SurveyNotificationInfo = Field(
        default_factory=SurveyNotificationInfo
    )


class SurveyRepository(Protocol):

    def get_test_survey(self) -> Survey:
        return get_test_survey()

    @abstractmethod
    def get_survey(self, id: str) -> Survey: ...

    @abstractmethod
    def create_survey(self, id: str, survey: SurveyCreation) -> None: ...

    @abstractmethod
    def list_surveys(self) -> list[Survey]: ...
