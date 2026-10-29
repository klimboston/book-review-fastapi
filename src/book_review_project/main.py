from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.book_review_project.core.config import settings
from src.book_review_project.routers import books, reviews, users
from src.book_review_project.services.rabbitmq_publisher import RabbitMQPublisher


@asynccontextmanager
async def lifespan(app: FastAPI):
    broker = RabbitMQPublisher(settings.rabbitmq_url)
    
    await broker.connect()
    app.state.rabbitmq_publisher = broker
    try:
        yield
    finally:
        await broker.close()

app = FastAPI(
    version="0.0.1b",
    title="Сервис отзывов и обзоров на книги",
    description="API для сервиса, позволяющего оставлять отзывы пользователей о различных книгах и авторах",
    lifespan=lifespan
)

app.include_router(users.router)
app.include_router(books.router)
app.include_router(reviews.router)


@app.get("/")
def return_ok():
    return {"status": "ok"}
