from pydantic import BaseModel


class Group(BaseModel):
    id: str
    name: str
    user_ids: list[str]
