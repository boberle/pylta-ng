from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

import lta.api.backoffice.endpoints
import lta.api.common.endpoints
import lta.api.scheduler.endpoints
import lta.api.userapp.endpoints
from lta.api.configuration import (
    get_allowed_origins,
    get_application_service,
    get_use_google_cloud_logging,
)
from lta.log import setup_google_cloud_logging

if get_use_google_cloud_logging():
    setup_google_cloud_logging()

app = FastAPI(openapi_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


application_service = get_application_service()

if application_service == "back":
    app.include_router(lta.api.backoffice.endpoints.router, prefix="/api/v1")
    app.include_router(lta.api.userapp.endpoints.router, prefix="/api/mobile/v1")
    app.include_router(lta.api.common.endpoints.router, prefix="/api/mobile/v1")

elif application_service == "scheduler":
    app.include_router(lta.api.scheduler.endpoints.router)

elif application_service == "all":
    app.include_router(lta.api.backoffice.endpoints.router, prefix="/api/v1")
    app.include_router(lta.api.userapp.endpoints.router, prefix="/api/mobile/v1")
    app.include_router(lta.api.scheduler.endpoints.router)
    app.include_router(lta.api.common.endpoints.router, prefix="/api/mobile/v1")

else:
    raise ValueError(f"Invalid application service: {application_service}")
