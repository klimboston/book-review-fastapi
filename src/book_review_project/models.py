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
    description: str | None = Field(default=None, max_length=500)
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
