from datetime import datetime

from pydantic import BaseModel, Field


class SingleQuestionAnswer(BaseModel):
    selected_index: int
    specify_answer: str | None = None


class MultipleQuestionAnswer(BaseModel):
    selected_indices: list[int]
    specify_answer: str | None = None


class OpenEndedQuestionAnswer(BaseModel):
    value: str


AnswerType = SingleQuestionAnswer | MultipleQuestionAnswer | OpenEndedQuestionAnswer


class Assignment(BaseModel):
    id: str
    title: str
    user_id: str
    survey_id: str
    created_at: datetime
    expired_at: datetime
    notified_at: list[datetime] = Field(default_factory=list)
    opened_at: list[datetime] = Field(default_factory=list)
    submitted_at: datetime | None = None
    answers: list[AnswerType] | None = None
