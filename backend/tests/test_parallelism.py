import pytest
import pytest_asyncio
import asyncio
from datetime import datetime
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.database import engine, Base, SessionLocal
from app.db.models import DBAgentRun, DBAgentState
from app.agents.base import BaseOwnerAgent
from app.agents.orchestrator import AgentScheduler
from app.agents.sources.adapter import SourceAdapter

# Mock Adapters for Concurrency Testing

class FastSuccessAdapter(SourceAdapter):
    def get_metadata(self):
        return {"source_id": "fast_success", "name": "Fast Success", "url": "mock"}
    
    async def fetch(self):
        # Simulate an I/O bound network request
        await asyncio.sleep(1.0)
        return {"data": "success"}

    def parse(self, raw_data): return raw_data
    def normalize(self, parsed_data): return parsed_data
    def validate(self, normalized_data): return normalized_data
    def to_canonical(self, raw_data, parsed_data, normalized_data, validated_model, fetch_timestamp):
        return []

class InstantFailureAdapter(SourceAdapter):
    def get_metadata(self):
        return {"source_id": "instant_fail", "name": "Instant Fail", "url": "mock"}
    
    async def fetch(self):
        # Fail immediately
        raise Exception("Mocked adapter crash!")

    def parse(self, raw_data): pass
    def normalize(self, parsed_data): pass
    def validate(self, normalized_data): pass
    def to_canonical(self, raw_data, parsed_data, normalized_data, validated_model, fetch_timestamp): pass

class HangingAdapter(SourceAdapter):
    def get_metadata(self):
        return {"source_id": "hanging", "name": "Hanging", "url": "mock"}
    
    async def fetch(self):
        # Simulate a stuck request that never completes
        await asyncio.sleep(999)
        return {}

    def parse(self, raw_data): pass
    def normalize(self, parsed_data): pass
    def validate(self, normalized_data): pass
    def to_canonical(self, raw_data, parsed_data, normalized_data, validated_model, fetch_timestamp): pass


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

from sqlalchemy import text

@pytest.mark.asyncio
async def test_genuine_parallelism_and_isolation():
    # Setup our 3 Mock Agents
    agent_fast1 = BaseOwnerAgent("agent_fast_1", FastSuccessAdapter())
    agent_fast2 = BaseOwnerAgent("agent_fast_2", FastSuccessAdapter())
    agent_fail = BaseOwnerAgent("agent_fail", InstantFailureAdapter())
    agent_hang = BaseOwnerAgent("agent_hang", HangingAdapter())
    
    # Configure scheduler with a very short timeout
    scheduler = AgentScheduler(max_concurrent=4, timeout_seconds=2, max_retries=0)
    
    agents = [agent_fast1, agent_fast2, agent_fail, agent_hang]
    
    start_time = datetime.utcnow()
    
    # Launch them concurrently
    tasks = [scheduler.execute_agent(agent) for agent in agents]
    await asyncio.gather(*tasks, return_exceptions=True)
    
    end_time = datetime.utcnow()
    duration_sec = (end_time - start_time).total_seconds()
    
    # ASSERTION 1: True Concurrency
    # If sequential, it would take 1s + 1s + 2s (timeout) = ~4s
    # In parallel, the longest task is the timeout (2s). Total time should be ~2s.
    assert duration_sec < 2.5, f"Execution was NOT fully parallel. Took {duration_sec}s."
    
    # ASSERTION 2: Isolated Failures
    async with SessionLocal() as session:
        # Check Agent 1 Status (Success)
        res = await session.execute(text("SELECT status FROM agent_runs WHERE agent_id = 'agent_fast_1' ORDER BY started_at DESC LIMIT 1"))
        assert res.scalar() == "success"
        
        # Check Agent 2 Status (Success)
        res = await session.execute(text("SELECT status FROM agent_runs WHERE agent_id = 'agent_fast_2' ORDER BY started_at DESC LIMIT 1"))
        assert res.scalar() == "success"
        
        # Check Failing Agent Status (Failed)
        res = await session.execute(text("SELECT status FROM agent_runs WHERE agent_id = 'agent_fail' ORDER BY started_at DESC LIMIT 1"))
        assert res.scalar() == "failed"
        
        # Check Hanging Agent Status (Timeout)
        res = await session.execute(text("SELECT status FROM agent_runs WHERE agent_id = 'agent_hang' ORDER BY started_at DESC LIMIT 1"))
        assert res.scalar() == "timeout"
        
        # Check that Health States correctly updated
        res = await session.execute(text("SELECT status FROM agent_states WHERE agent_id = 'agent_fast_1'"))
        assert res.scalar() == "healthy"
        
        res = await session.execute(text("SELECT status FROM agent_states WHERE agent_id = 'agent_hang'"))
        assert res.scalar() == "failing"
