from fastapi import FastAPI

from app import settings
from app.routers import router
from app.clients.crypto import client as crypto_client


app = FastAPI(
    debug=settings.debug,
    description=("Synthesia hiring challenge API"),
    docs_url=None,
    openapi_url="/api/docs/openapi.json",
    redoc_url="/api/docs",
    title="Synthesia Challenge API",
    version="0.1.0",
)


@app.on_event("startup")
async def startup():
    await crypto_client.start()


@app.on_event("shutdown")
async def shutdown():
    await crypto_client.stop()


app.include_router(router)
