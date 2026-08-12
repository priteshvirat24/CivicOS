import pytest_asyncio
import pytest
import asyncio
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.database import engine, Base, SessionLocal
from app.db.models import DBDatasetVersion, DBDataPR
from sqlalchemy import text
from app.agents.event_bus import bus, DataPRCreated, VerificationPassed, VerificationFailed, DataPRMerged, DatasetUpdated
from app.agents.orchestrator import setup_orchestrator
from app.agents.registry import registry
from app.agents.base import BaseOwnerAgent

@pytest_asyncio.fixture(autouse=True)
async def setup_db_and_bus():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        
    async with SessionLocal() as session:
        v1 = DBDatasetVersion(id=1, description="Initial Schema")
        session.add(v1)
        await session.commit()
        
    # Start EventBus and Orchestrator
    setup_orchestrator()
    
    yield
    
    # Cleanup
    await bus.stop()
    bus.subscribers.clear()
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        
    # Delete state file to ensure fresh agent runs
    if os.path.exists("agent_states.json"):
        os.remove("agent_states.json")
    if os.path.exists("agent_records.json"):
        os.remove("agent_records.json")

@pytest.mark.asyncio
async def test_e2e_autonomous_lifecycle():
    # 1. Grab a registered adapter (we will use covid19 for example)
    adapter = registry.get_adapter("covid19")
    agent = BaseOwnerAgent("agent_covid19", adapter)
    
    # Track events to assert the chain happened
    events_seen = []
    
    def tracker(event):
        events_seen.append(type(event))
        
    async def track_created(e): tracker(e)
    async def track_passed(e): tracker(e)
    async def track_merged(e): tracker(e)
    async def track_updated(e): tracker(e)
    
    # Intercept events
    bus.subscribe(DataPRCreated, track_created)
    bus.subscribe(VerificationPassed, track_passed)
    bus.subscribe(DataPRMerged, track_merged)
    bus.subscribe(DatasetUpdated, track_updated)
    
    # 2. Trigger the agent
    await agent.run()
    
    # Wait for the event bus to process the chain
    await asyncio.sleep(2.0)
    
    # 3. Assertions
    assert DataPRCreated in events_seen
    assert VerificationPassed in events_seen
    assert DataPRMerged in events_seen
    assert DatasetUpdated in events_seen
    
    # Check DB state
    async with SessionLocal() as session:
        result = await session.execute(text("SELECT status FROM data_prs ORDER BY created_at DESC LIMIT 1"))
        assert result.scalar() == "merged"
        
        result = await session.execute(text("SELECT id FROM dataset_versions ORDER BY id DESC LIMIT 1"))
        assert result.scalar() == 2
        
    # 4. Idempotency Test: Run the agent again immediately
    events_seen.clear()
    
    await agent.run()
    await asyncio.sleep(0.2)
    
    # Because there are no new changes, SOURCE_UNCHANGED is emitted internally,
    # and no DataPRCreated event should be emitted.
    assert DataPRCreated not in events_seen
    
    # Check that there is still only 1 PR in the DB
    async with SessionLocal() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM data_prs"))
        assert result.scalar() == 1

@pytest.mark.asyncio
async def test_e2e_idempotency_concurrent_prs():
    adapter = registry.get_adapter("covid19")
    agent = BaseOwnerAgent("agent_covid19", adapter)
    
    # Inject a fake 'open' PR for this source directly into DB
    async with SessionLocal() as session:
        pr_open = DBDataPR(
            id="fake-open-pr", source_id="covid19", agent_id="agent_covid19",
            base_dataset_version=1, proposed_dataset_version=2,
            status="open", source_url="test", schema_version="1",
            normalization_version="1", agent_run_id="run_x"
        )
        session.add(pr_open)
        await session.commit()
        
    events_seen = []
    async def track_created_2(e): events_seen.append(e)
    bus.subscribe(DataPRCreated, track_created_2)
    
    # Run the agent
    # Even if data has changed (since it's a fresh run with no state file),
    # it should detect the existing open PR and ABORT.
    await agent.run()
    await asyncio.sleep(0.2)
    
    assert len(events_seen) == 0
    
    # DB PR count should still be 1
    async with SessionLocal() as session:
        result = await session.execute(text("SELECT COUNT(*) FROM data_prs"))
        assert result.scalar() == 1
