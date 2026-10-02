from pydantic import BaseModel, EmailStr, Field


class BookPublic(BaseModel):
    id: int
    title: str
    author: str
    description: str | None
    user_id: int


class CreateUser(BaseModel):
    """Схема запроса создания пользователя, должна содержать имя пользователя,
    email и пароль.
    """

    username: str
    email: EmailStr
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserWithBooks(BaseModel):
    id: int
    username: str
    email: str
    books: list[BookPublic] = []


class ReviewPublic(BaseModel):
    id: int | None
    text: str
    rating: int
    user_id: int | None


class ReviewCreate(BaseModel):
    text: str
    rating: int
    book_id: int


class CreateBook(BaseModel):
    title: str
    author: str
    description: str | None = Field(default=None)

class BookWithReviews(BaseModel):
    id: int
    user_id: int
    title: str
    author: str
    description: str | None
    book_reviews: list[ReviewPublic] = []


class Token(BaseModel):
    access_token: str
    token_type: str
