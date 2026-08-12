from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

import os

# Allow overriding DB path for production docker volumes
db_path = os.environ.get("DATABASE_URL", "sqlite+aiosqlite:///./civicos.db")
SQLALCHEMY_DATABASE_URL = db_path

engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL, echo=False
)

SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()

async def get_db():
    async with SessionLocal() as session:
        yield session
