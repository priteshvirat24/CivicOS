import pytest_asyncio
import pytest
from httpx import AsyncClient, ASGITransport
import sys
import os
import json
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.database import engine, Base, SessionLocal
from app.db.models import DBDatasetVersion, DBDataPR, DBProposedRecord
from app.agents.verifier import VerifierAgent
from app.agents.detector import ChangeDetector

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
async def test_verifier_adversarial_rejection():
    # Setup malicious PRs and honest PRs
    detector = ChangeDetector()
    
    async with SessionLocal() as session:
        # PR 1: Forged Hash
        forged_data = {"key": "value"}
        forged_hash = "fake_hash_123"
        pr1 = DBDataPR(
            id="pr-forged", source_id="covid19", agent_id="agent_malicious",
            base_dataset_version=1, proposed_dataset_version=2,
            status="open", source_url="test", schema_version="1",
            normalization_version="1", agent_run_id="run1"
        )
        session.add(pr1)
        session.add(DBProposedRecord(
            id="rec-forged", pr_id="pr-forged", source_id="covid19", dataset_id="covid19",
            observed_at=datetime.utcnow(), effective_at=datetime.utcnow(),
            data=forged_data, source_reference="ref1", content_hash=forged_hash,
            schema_version="1", normalization_version="1", confidence=1.0, provenance={}
        ))
        
        # PR 2: Hallucinated Value (Hash matches data, but data doesn't exist in source)
        hallucinated_data = {"state_code": "XX", "confirmed": 999999999, "recovered": 0, "deceased": 0, "tested": 0, "last_updated": ""}
        hallucinated_hash = detector.hash_payload(hallucinated_data)
        pr2 = DBDataPR(
            id="pr-hallucinated", source_id="covid19", agent_id="agent_malicious",
            base_dataset_version=1, proposed_dataset_version=2,
            status="open", source_url="test", schema_version="1",
            normalization_version="1", agent_run_id="run2"
        )
        session.add(pr2)
        session.add(DBProposedRecord(
            id="rec-hallucinated", pr_id="pr-hallucinated", source_id="covid19", dataset_id="covid19",
            observed_at=datetime.utcnow(), effective_at=datetime.utcnow(),
            data=hallucinated_data, source_reference="ref2", content_hash=hallucinated_hash,
            schema_version="1", normalization_version="1", confidence=1.0, provenance={}
        ))
        
        await session.commit()

    verifier = VerifierAgent()
    
    from sqlalchemy import text
    # Test 1: Forged Hash should fail
    report1 = await verifier.verify_pr("pr-forged")
    assert not report1.passed
    assert "provenance_valid" in report1.failed_checks
    
    async with SessionLocal() as session:
        result = await session.execute(text("SELECT status FROM data_prs WHERE id='pr-forged'"))
        assert result.scalar() == "rejected"
        
    print("\\nVerifier caught forged hash!")
    
    # Test 2: Hallucinated Data should fail
    report2 = await verifier.verify_pr("pr-hallucinated")
    assert not report2.passed
    assert "proposed_value_exists" in report2.failed_checks
    
    async with SessionLocal() as session:
        result = await session.execute(text("SELECT status FROM data_prs WHERE id='pr-hallucinated'"))
        assert result.scalar() == "rejected"
        
    print("Verifier caught hallucinated data!")
