from datetime import datetime

from pydantic import BaseModel, Field


class SingleChoiceAnswer(BaseModel):
    selected_index: int
    specify_answer: str | None = None


class MultipleChoiceAnswer(BaseModel):
    selected_indices: list[int]
    specify_answer: str | None = None


class OpenEndedAnswer(BaseModel):
    value: str


AnswerType = SingleChoiceAnswer | MultipleChoiceAnswer | OpenEndedAnswer | None


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
