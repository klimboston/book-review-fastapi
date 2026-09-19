from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlmodel import SQLModel

from src.book_review_project.database import engine
from src.book_review_project.routers import books, reviews, users


async def create_db_and_tables():
    async with engine.begin() as con:
        await con.run_sync(SQLModel.metadata.create_all)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield


app = FastAPI(
    version="0.0.1b",
    title="Сервис отзывов и обзоров на книги",
    description="API для сервиса, позволяющего оставлять отзывы пользователей о различных книгах и авторах",
    lifespan=lifespan,
)

app.include_router(users.router)
app.include_router(books.router)
app.include_router(reviews.router)


@app.get("/")
def return_ok():
    return {"status": "ok"}
