from pydantic import BaseModel
from sqlmodel import Field, Relationship, SQLModel


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(max_length=40, index=True)
    email: str = Field(unique=True, index=True)
    books: list["Book"] = Relationship(back_populates="user")
    user_reviews: list["Review"] = Relationship(back_populates="user")
    hashed_password: str = Field(exclude=True)


class Book(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="user.id")
    title: str = Field(index=True)
    author: str = Field(index=True)
    description: str | None = Field(default=None)
    user: "User" = Relationship(back_populates="books")
    book_reviews: list["Review"] = Relationship(back_populates="book")


class Review(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int | None = Field(default=None, foreign_key="user.id")
    book_id: int | None = Field(default=None, foreign_key="book.id")
    text: str = Field(max_length=1000)
    rating: int = Field(ge=1, le=5)
    user: "User" = Relationship(back_populates="user_reviews")
    book: "Book" = Relationship(back_populates="book_reviews")


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