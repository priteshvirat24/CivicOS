import pytest
from httpx import AsyncClient, ASGITransport
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest_asyncio
from app.main import app
from app.db.database import engine, Base, SessionLocal
from app.db.models import DBDatasetVersion, DBDataPR

@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        
    async with SessionLocal() as session:
        v1 = DBDatasetVersion(id=1, description="Initial Schema")
        session.add(v1)
        await session.commit()
    
    yield
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.mark.asyncio
async def test_pr_workflow_and_optimistic_concurrency():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        # First, insert a fake PR manually into the DB to test the API
        async with SessionLocal() as session:
            pr1 = DBDataPR(
                id="pr-1", source_id="test_source", agent_id="agent_1",
                base_dataset_version=1, proposed_dataset_version=2,
                status="open", source_url="http", schema_version="1",
                normalization_version="1", agent_run_id="run1"
            )
            
            pr2 = DBDataPR(
                id="pr-2", source_id="test_source", agent_id="agent_1",
                base_dataset_version=1, proposed_dataset_version=2,
                status="open", source_url="http", schema_version="1",
                normalization_version="1", agent_run_id="run2"
            )
            session.add(pr1)
            session.add(pr2)
            await session.commit()
        
        # 1. List PRs
        response = await ac.get("/api/prs")
        assert response.status_code == 200
        prs = response.json()
        assert len(prs) == 2
        
        # 2. Approve PR 1
        response = await ac.post("/api/prs/pr-1/approve")
        assert response.status_code == 200
        
        # 3. Merge PR 1
        response = await ac.post("/api/prs/pr-1/merge")
        assert response.status_code == 200
        assert response.json()["new_version"] == 2
        
        # 4. Approve PR 2
        response = await ac.post("/api/prs/pr-2/approve")
        assert response.status_code == 200
        
        # 5. Try to Merge PR 2 (Should Fail due to Optimistic Concurrency)
        response = await ac.post("/api/prs/pr-2/merge")
        assert response.status_code == 409
        assert "Optimistic concurrency failure" in response.json()["detail"]
        
        print("\\nOptimistic Concurrency works: PR 2 correctly rejected because the DB version advanced to 2 while PR 2 was based on 1.")
