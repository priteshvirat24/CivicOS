import asyncio
from app.db.database import engine, Base, SessionLocal
from app.db.models import DBDatasetVersion
from sqlalchemy import select

async def init_models():
    async with engine.begin() as conn:
        # Create all tables
        await conn.run_sync(Base.metadata.create_all)
        
    async with SessionLocal() as session:
        # Ensure at least version 1 exists
        result = await session.execute(select(DBDatasetVersion).where(DBDatasetVersion.id == 1))
        version = result.scalar_one_or_none()
        if not version:
            v1 = DBDatasetVersion(id=1, description="Initial Schema")
            session.add(v1)
            await session.commit()

if __name__ == "__main__":
    asyncio.run(init_models())
