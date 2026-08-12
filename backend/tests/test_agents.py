import pytest
import sys
import os
import asyncio

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.agents.orchestrator import run_all_agents
from app.agents.registry import registry
from app.agents.base import BaseOwnerAgent
from app.db.database import engine, Base
import pytest_asyncio

@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_agent_orchestrator(monkeypatch, capsys):
    # We will "poison" one adapter (india_gdp) to simulate failure
    # and prove the other 7 agents continue operating.
    
    adapters = registry.get_all_adapters()
    
    # Poison india_gdp adapter
    for adapter in adapters:
        if adapter.get_metadata()["source_id"] == "india_gdp":
            async def broken_fetch(*args, **kwargs):
                raise ValueError("Simulated network outage for India GDP")
            monkeypatch.setattr(adapter, 'fetch', broken_fetch)
            
    # Mock registry so run_all_agents uses our modified adapters
    monkeypatch.setattr(registry, 'get_all_adapters', lambda: adapters)
            
    # Run all
    await run_all_agents()
    
    captured = capsys.readouterr().out
    
    # Assert failure isolation occurred
    assert "agent_india_gdp FAILED" in captured
    assert "Simulated network outage for India GDP" in captured
    assert "agent_covid19 COMPLETED successfully" in captured
    assert "agent_railways COMPLETED successfully" in captured
    assert "agent_delhi_weather COMPLETED successfully" in captured
    assert "agent_india_population COMPLETED successfully" in captured
    assert "agent_delhi_openaq COMPLETED successfully" in captured
    assert "agent_india_geodata COMPLETED successfully" in captured
    assert "agent_mumbai_sunrise COMPLETED successfully" in captured
    # wait demo might fail if the server is off, so we skip it.
    
    print("Failure isolation proven successfully.")
