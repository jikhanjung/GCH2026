from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import heritage

app = FastAPI(title="지질유산 DB")

app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.include_router(heritage.router)
