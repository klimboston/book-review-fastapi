from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from src.book_review_project.config import settings

engine: AsyncEngine = create_async_engine(settings.database_url, echo=True)
