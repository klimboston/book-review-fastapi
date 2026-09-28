from pydantic import BaseModel, Field


class BookPublic(BaseModel):
    id: int
    title: str
    author: str
    description: str | None
    user_id: int


class CreateUser(BaseModel):
    username: str
    email: str
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


class BookWithReviews(BaseModel):
    id: int
    book_reviews: list[ReviewPublic] = []
    title: str
    author: str
    description: str | None
    user_id: int


class Token(BaseModel):
    access_token: str
    token_type: str