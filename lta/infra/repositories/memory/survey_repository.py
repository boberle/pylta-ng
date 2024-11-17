from dataclasses import dataclass, field

from lta.domain.survey import Survey
from lta.domain.survey_repository import (
    TEST_SURVEY_ID,
    SurveyCreation,
    SurveyNotFound,
    SurveyRepository,
)


@dataclass
class InMemorySurveyRepository(SurveyRepository):
    surveys: dict[str, Survey] = field(default_factory=dict)

    def get_survey(self, id: str) -> Survey:
        if id == TEST_SURVEY_ID:
            return self.get_test_survey()

        if id not in self.surveys:
            raise SurveyNotFound(survey_id=id)
        return self.surveys[id]

    def create_survey(self, id: str, survey: SurveyCreation) -> None:
        stored_survey = Survey(
            id=id,
            title=survey.title,
            welcome_message=survey.welcome_message,
            submit_message=survey.submit_message,
            questions=survey.questions,
            notifications=survey.notifications,
        )
        self.surveys[stored_survey.id] = stored_survey

    def list_surveys(self) -> list[Survey]:
        return list(self.surveys.values())
