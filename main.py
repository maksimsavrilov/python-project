from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers.auth import router as auth_router
from routers.devices import router as devices_router

app = FastAPI(title="Smart Home API")

app.add_middleware(
    CORSMiddleware,
    # Явно разрешаем адрес, на котором запущен твой React в Podman
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173"
    ],
    allow_credentials=True, # Критически важно для работы с куками и Auth-заголовками
    allow_methods=["*"],    # Разрешаем все методы (GET, POST, OPTIONS)
    allow_headers=["*"],    # Разрешаем любые заголовки от фронтенда
)

app.include_router(auth_router)
app.include_router(devices_router)

