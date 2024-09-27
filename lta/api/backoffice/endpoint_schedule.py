from __future__ import annotations

import uuid

import pydantic
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from lta.api.configuration import AppConfiguration, get_configuration
from lta.authentication import get_admin_user
from lta.domain.schedule import Schedule
from lta.domain.schedule_repository import ScheduleCreation

router = APIRouter()


class ScheduleItemResponse(Schedule):
    @staticmethod
    def from_domain(schedule: Schedule) -> ScheduleItemResponse:
        return pydantic.TypeAdapter(ScheduleItemResponse).validate_python(
            schedule.model_dump()
        )


class ScheduleListResponse(BaseModel):
    schedules: list[ScheduleItemResponse]


@router.get("/")
async def get_schedules(
    configuration: AppConfiguration = Depends(get_configuration),
    admin_id: str = Depends(get_admin_user),
) -> ScheduleListResponse:
    schedules = configuration.schedule_repository.list_schedules()
    return ScheduleListResponse(
        schedules=[ScheduleItemResponse.from_domain(schedule) for schedule in schedules]
    )


class ScheduleCreationRequest(ScheduleCreation): ...


@router.post("/")
def post_schedule(
    request: ScheduleCreationRequest,
    configuration: AppConfiguration = Depends(get_configuration),
    admin_id: str = Depends(get_admin_user),
) -> None:
    id = str(uuid.uuid4())
    configuration.schedule_repository.create_schedule(id, request)


@router.delete("/{schedule_id:str}/")
def delete_schedule(
    schedule_id: str,
    configuration: AppConfiguration = Depends(get_configuration),
    admin_id: str = Depends(get_admin_user),
) -> None:
    configuration.schedule_repository.delete_schedule(schedule_id)
