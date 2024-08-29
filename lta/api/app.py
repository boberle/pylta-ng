from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

import lta.api.backoffice.endpoints
from lta.api.configuration import get_allowed_origins

app = FastAPI(openapi_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=get_allowed_origins(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(lta.api.backoffice.endpoints.router, prefix="/api/v1")
