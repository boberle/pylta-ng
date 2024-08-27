from fastapi import FastAPI

import lta.api.backoffice.endpoints

app = FastAPI(openapi_url=None)

app.include_router(lta.api.backoffice.endpoints.router, prefix="/api/v1")
