from __future__ import annotations

from fastapi import APIRouter

import lta.api.backoffice.endpoint_user

router = APIRouter()


router.include_router(lta.api.backoffice.endpoint_user.router, prefix="/users")
