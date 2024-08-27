from uuid import UUID

from pydantic import BaseModel


class Group(BaseModel):
    id: UUID
    user_ids: list[UUID]
