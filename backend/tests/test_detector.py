import pytest
import sys
import os
from datetime import datetime
from pydantic import BaseModel

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.agents.detector import ChangeDetector
from app.models.canonical import CanonicalRecord, ProvenanceMetadata

def get_dummy_provenance():
    return ProvenanceMetadata(
        agent_id="test_agent",
        fetch_url="http://test",
        fetch_timestamp=datetime.utcnow(),
        raw_payload_hash="dummy"
    )

def test_detector_false_positives():
    detector = ChangeDetector(ignored_fields=["last_updated"])
    
    # Test 1: Ignored Fields & Key Ordering
    data1 = {"income_limit": 300000, "status": "active", "last_updated": "2026-08-12T10:00:00Z"}
    data2 = {"status": "active", "last_updated": "2026-08-12T11:00:00Z", "income_limit": 300000}
    
    hash1 = detector.hash_payload(data1)
    hash2 = detector.hash_payload(data2)
    assert hash1 == hash2, "Detector failed to ignore noise or ordering"

    # Test 2: Nested Lists Ordering
    data3 = {"cities": [{"name": "A"}, {"name": "B"}]}
    data4 = {"cities": [{"name": "B"}, {"name": "A"}]}
    assert detector.hash_payload(data3) == detector.hash_payload(data4), "Detector failed on list element ordering"

def test_detector_deep_diff():
    detector = ChangeDetector()
    
    data1 = {"eligibility": {"income_limit": 300000, "age": 18}}
    data2 = {"eligibility": {"income_limit": 500000, "age": 18}}
    
    import json, hashlib
    h1 = hashlib.sha256(json.dumps(data1, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()
    h2 = hashlib.sha256(json.dumps(data2, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()

    old_record = CanonicalRecord(
        source_id="test", dataset_id="ds", observed_at=datetime.utcnow(), effective_at=datetime.utcnow(),
        source_reference="rec1", content_hash=h1, schema_version="1", normalization_version="1",
        confidence=1.0, provenance=get_dummy_provenance(),
        data=data1
    )
    
    new_record = CanonicalRecord(
        source_id="test", dataset_id="ds", observed_at=datetime.utcnow(), effective_at=datetime.utcnow(),
        source_reference="rec1", content_hash=h2, schema_version="1", normalization_version="1",
        confidence=1.0, provenance=get_dummy_provenance(),
        data=data2
    )
    
    diffs = detector.diff_records(old_record, new_record)
    
    assert len(diffs) == 1
    assert diffs[0].affected_field == "eligibility.income_limit"
    assert diffs[0].old_value == 300000
    assert diffs[0].new_value == 500000

    print("\\nDiff engine passed semantic deep diffing!")
    
if __name__ == "__main__":
    test_detector_false_positives()
    test_detector_deep_diff()
