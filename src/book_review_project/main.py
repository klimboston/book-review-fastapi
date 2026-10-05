from fastapi import FastAPI

from src.book_review_project.routers import books, reviews, users

app = FastAPI(
    version="0.0.1b",
    title="Сервис отзывов и обзоров на книги",
    description="API для сервиса, позволяющего оставлять отзывы пользователей о различных книгах и авторах",
)

app.include_router(users.router)
app.include_router(books.router)
app.include_router(reviews.router)


@app.get("/")
def return_ok():
    return {"status": "ok"}
