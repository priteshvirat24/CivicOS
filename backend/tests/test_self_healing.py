import pytest
from app.db.database import SessionLocal
from app.agents.base import BaseOwnerAgent
from app.agents.sources.adapter import SourceAdapter
from typing import Dict, Any, List
from datetime import datetime
from app.models.canonical import CanonicalRecord
from app.agents.errors import SchemaDriftError, MalformedResponseError

class FaultyAdapter(SourceAdapter):
    def __init__(self):
        self.state = "healthy"
        self.last_fetch = {"id": "1", "data": "good"}

    def get_metadata(self) -> Dict[str, str]:
        return {"source_id": "faulty_source", "name": "Faulty Source", "url": "mock://faulty"}

    async def fetch(self) -> Dict[str, Any]:
        if self.state == "malformed":
            import json
            raise json.JSONDecodeError("Expecting value", "<html>bad</html>", 0)
        return self.last_fetch

    def parse(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        if self.state == "schema_drift":
            raise KeyError("Missing expected field: 'data'")
        return [raw_data]

    def normalize(self, parsed_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return parsed_data

    def validate(self, normalized_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return normalized_data

    def to_canonical(self, raw_data, parsed_data, normalized_data, validated_model, fetch_timestamp) -> List[CanonicalRecord]:
        import hashlib
        import json
        records = []
        for item in validated_model:
            # Pydantic validation requires the exact hash of the dumped dict
            import json
            import hashlib
            dumped = json.dumps(item, separators=(',', ':'), sort_keys=True)
            h = hashlib.sha256(dumped.encode('utf-8')).hexdigest()
            import uuid
            records.append(
                CanonicalRecord(
                    id=str(uuid.uuid4()),
                    source_id="faulty_source",
                    dataset_id="faulty_dataset",
                    observed_at=fetch_timestamp,
                    effective_at=fetch_timestamp,
                    last_updated_at=fetch_timestamp,
                    data=item,
                    source_reference=str(item["id"]),
                    content_hash=h,
                    schema_version="1.0",
                    normalization_version="1.0",
                    confidence=1.0,
                    provenance={
                        "source_url": "mock://faulty",
                        "fetch_url": "mock://faulty",
                        "fetch_timestamp": fetch_timestamp.isoformat(),
                        "agent_id": "agent_faulty",
                        "raw_payload_hash": h
                    }
                )
            )
        return records

@pytest.mark.asyncio
async def test_agent_self_healing():
    from app.db.database import engine, Base
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
        
    adapter = FaultyAdapter()
    agent = BaseOwnerAgent("agent_faulty", adapter)

    # 1. Healthy Run
    adapter.state = "healthy"
    records = await agent.run("run_healthy")
    assert len(records) == 1
    
    async with SessionLocal() as session:
        from app.db.models import DBAgentState
        from sqlalchemy import select
        state = (await session.execute(select(DBAgentState).where(DBAgentState.agent_id == "agent_faulty"))).scalar_one()
        assert state.status == "healthy"
        hash_v1 = state.last_hash

    # 2. Malformed Run
    adapter.state = "malformed"
    with pytest.raises(MalformedResponseError):
        await agent.run("run_malformed")
        
    async with SessionLocal() as session:
        state = (await session.execute(select(DBAgentState).where(DBAgentState.agent_id == "agent_faulty"))).scalar_one()
        assert state.status == "failing"
        assert "Malformed response" in state.last_error
        # Proof: Last known good hash is NOT corrupted
        assert state.last_hash == hash_v1

    # 3. Schema Drift Run
    adapter.state = "schema_drift"
    with pytest.raises(SchemaDriftError):
        await agent.run("run_drift")
        
    async with SessionLocal() as session:
        state = (await session.execute(select(DBAgentState).where(DBAgentState.agent_id == "agent_faulty"))).scalar_one()
        assert state.status == "degraded"
        assert "Schema drift" in state.last_error
        # Proof: Last known good hash is NOT corrupted
        assert state.last_hash == hash_v1

    # 4. Recovery Run
    async with SessionLocal() as session:
        from app.db.models import DBDataPR
        from sqlalchemy import update
        await session.execute(update(DBDataPR).where(DBDataPR.agent_id == "agent_faulty").values(status="rejected"))
        await session.commit()
        
    adapter.state = "healthy"
    adapter.last_fetch = {"id": "1", "data": "recovered"} # simulate a change to see if it processes
    await agent.run("run_recovery")
    
    async with SessionLocal() as session:
        state = (await session.execute(select(DBAgentState).where(DBAgentState.agent_id == "agent_faulty"))).scalar_one()
        assert state.status == "recovered"
        assert state.last_hash != hash_v1 # Hash updated since we successfully recovered and processed new data
