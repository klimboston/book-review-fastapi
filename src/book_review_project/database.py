from sqlmodel import create_engine

from src.book_review_project.config import settings

sqlite_url = settings.DATABASE_URL
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})