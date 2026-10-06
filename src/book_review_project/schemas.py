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
    password: str = Field(min_length=7)


class UserLogin(BaseModel):
    email: str
    password: str


class UserWithBooks(BaseModel):
    id: int
    username: str
    email: str
    books: list[BookPublic] = []


class ChangeReview(BaseModel):
    text: str | None = Field(min_length=1, max_length=400, default=None)
    rating: int | None = Field(ge=1, le=5, default=None)    

class ReviewPublic(BaseModel):
    id: int | None
    text: str
    rating: int
    user_id: int | None


class ReviewCreate(BaseModel):
    text: str = Field(min_length=1, max_length=400)
    rating: int = Field(ge=1, le=5)
    book_id: int


class CreateBook(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    author: str
    description: str | None = Field(default=None, max_length=500)
    
class ChangeBook(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    author: str | None = Field(default=None)
    description: str | None = Field(default=None, max_length=500)    

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
