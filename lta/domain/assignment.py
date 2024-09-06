from datetime import datetime

from pydantic import BaseModel, Field

AnswerType = int | list[int] | str


class Assignment(BaseModel):
    id: str
    user_id: str
    survey_id: str
    created_at: datetime
    scheduled_for: datetime | None = None
    published_at: datetime | None = None
    expired_at: datetime | None = None
    notified_at: list[datetime] = Field(default_factory=list)
    opened_at: list[datetime] = Field(default_factory=list)
    submitted_at: datetime | None = None
    answers: list[AnswerType] | None = None
