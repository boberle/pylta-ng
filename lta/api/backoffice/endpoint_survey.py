from __future__ import annotations

import uuid
from typing import Literal

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from lta.api.configuration import AppConfiguration, get_configuration
from lta.authentication import get_admin_user
from lta.domain.survey import Survey
from lta.domain.survey_repository import SurveyCreation

router = APIRouter()


class SurveyItemResponse(BaseModel):
    id: str
    title: str

    @staticmethod
    def from_domain(survey: Survey) -> SurveyItemResponse:
        return SurveyItemResponse(
            id=survey.id,
            title=survey.title,
        )


class SurveyListResponse(BaseModel):
    surveys: list[SurveyItemResponse]


@router.get("/")
async def get_surveys(
    configuration: AppConfiguration = Depends(get_configuration),
    admin_id: str = Depends(get_admin_user),
) -> SurveyListResponse:
    surveys = configuration.survey_repository.list_surveys()
    return SurveyListResponse(
        surveys=[SurveyItemResponse.from_domain(survey) for survey in surveys]
    )


class SurveyDetailsQuestion(BaseModel):
    message: str
    type: Literal["single-choice", "multiple-choice", "open-ended"]


class SurveyDetailsResponse(BaseModel):
    id: str
    title: str
    questions: list[SurveyDetailsQuestion]

    @staticmethod
    def from_domain(survey: Survey) -> SurveyDetailsResponse:
        return SurveyDetailsResponse(
            id=survey.id,
            title=survey.title,
            questions=[
                SurveyDetailsQuestion(
                    message=question.message,
                    type=question.type,
                )
                for question in survey.questions
            ],
        )


@router.get("/{survey_id:str}/")
async def get_survey(
    survey_id: str,
    configuration: AppConfiguration = Depends(get_configuration),
    admin_id: str = Depends(get_admin_user),
) -> SurveyDetailsResponse:
    survey = configuration.survey_repository.get_survey(survey_id)
    return SurveyDetailsResponse.from_domain(survey)


class SurveyCreationRequest(SurveyCreation): ...


@router.post("/")
def post_survey(
    request: SurveyCreationRequest,
    configuration: AppConfiguration = Depends(get_configuration),
    admin_id: str = Depends(get_admin_user),
) -> None:
    id = str(uuid.uuid4())
    configuration.survey_repository.create_survey(id, request)
