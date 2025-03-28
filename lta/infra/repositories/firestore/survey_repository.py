import json
from dataclasses import dataclass
from typing import List, Literal

import pydantic
from google.cloud import firestore
from pydantic import ConfigDict

from lta.domain.survey import Survey
from lta.domain.survey_repository import (
    TEST_SURVEY_ID,
    SurveyCreation,
    SurveyNotFound,
    SurveyRepository,
)


class StoredSurvey(Survey):
    revision: Literal[1] = 1
    model_config = ConfigDict(extra="forbid")


@dataclass
class FirestoreSurveyRepository(SurveyRepository):
    client: firestore.Client
    collection_name: str = "surveys"

    def get_survey(self, id: str) -> Survey:
        if id == TEST_SURVEY_ID:
            return self.get_test_survey()

        doc_ref = self.client.collection(self.collection_name).document(id)
        doc = doc_ref.get()
        if not doc.exists:
            raise SurveyNotFound(survey_id=id)
        stored_survey = pydantic.TypeAdapter(StoredSurvey).validate_python(
            doc.to_dict()
        )
        return pydantic.TypeAdapter(Survey).validate_python(stored_survey.model_dump())

    def create_survey(self, id: str, survey: SurveyCreation) -> None:
        doc_ref = self.client.collection(self.collection_name).document(id)
        stored_survey: StoredSurvey = pydantic.TypeAdapter(
            StoredSurvey
        ).validate_python(dict(id=id, **survey.model_dump()))
        # Because the question conditions are dictionaries with int keys, we need to convert them to strings
        # because Firestore does not support dictionaries with integer keys. The simplest way I have
        # found is to convert them to json.
        json_data = stored_survey.model_dump_json()
        doc_ref.set(json.loads(json_data))

    def list_surveys(self) -> List[Survey]:
        surveys_ref = self.client.collection(self.collection_name)
        docs = surveys_ref.stream()
        stored_surveys = (
            pydantic.TypeAdapter(StoredSurvey).validate_python(doc.to_dict())
            for doc in docs
        )
        return pydantic.TypeAdapter(list[Survey]).validate_python(
            [s.model_dump() for s in stored_surveys]
        )
