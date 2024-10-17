from __future__ import annotations

from fastapi import APIRouter

import lta.api.backoffice.endpoint_group
import lta.api.backoffice.endpoint_schedule
import lta.api.backoffice.endpoint_survey
import lta.api.backoffice.endpoint_user

router = APIRouter()


router.include_router(lta.api.backoffice.endpoint_user.router, prefix="/users")
router.include_router(lta.api.backoffice.endpoint_survey.router, prefix="/surveys")
router.include_router(lta.api.backoffice.endpoint_schedule.router, prefix="/schedules")
router.include_router(lta.api.backoffice.endpoint_group.router, prefix="/groups")
