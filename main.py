from fastapi import FastAPI

from routers.auth import router as auth_router
from routers.devices import router as devices_router

app = FastAPI(title="Smart Home API")

app.include_router(auth_router)
app.include_router(devices_router)

