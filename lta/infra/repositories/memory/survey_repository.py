from dataclasses import dataclass, field

from lta.domain.survey import Survey
from lta.domain.survey_repository import (
    SurveyCreation,
    SurveyNotFound,
    SurveyRepository,
)


@dataclass
class InMemorySurveyRepository(SurveyRepository):
    surveys: dict[str, Survey] = field(default_factory=dict)

    def get_survey(self, id: str) -> Survey:
        if id not in self.surveys:
            raise SurveyNotFound(survey_id=id)
        return self.surveys[id]

    def create_survey(self, id: str, survey: SurveyCreation) -> None:
        stored_survey = Survey(id=id, **survey.model_dump())
        self.surveys[stored_survey.id] = stored_survey

    def list_surveys(self) -> list[Survey]:
        return list(self.surveys.values())
