from datetime import datetime

from pydantic import BaseModel, Field

AnswerType = int | list[int] | str


class Assignment(BaseModel):
    id: str
    user_id: str
    survey_id: str
    created_at: datetime
    expired_at: datetime
    notified_at: list[datetime] = Field(default_factory=list)
    opened_at: list[datetime] = Field(default_factory=list)
    submitted_at: datetime | None = None
    answers: list[AnswerType] | None = None
