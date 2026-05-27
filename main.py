from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from database import create_tables
from routers import calendar, calculator, rates, feedback
from scheduler import scheduler
from seed import seed as run_seed


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    await run_seed()
    scheduler.start()
    yield
    scheduler.shutdown()


app = FastAPI(
    title="BuhBase API",
    description="Сервис для бухгалтеров Казахстана: налоговый календарь, калькулятор зарплаты, справочник ставок",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(calendar.router)
app.include_router(calculator.router)
app.include_router(rates.router)
app.include_router(feedback.router)


@app.get("/health")
async def health():
    return {"status": "ok"}
