from pydantic import BaseModel, Field, field_validator
from typing import Any, Dict, List, Optional
from datetime import datetime
import enum
import uuid
import hashlib
import json

class ProvenanceMetadata(BaseModel):
    agent_id: str
    fetch_url: str
    fetch_timestamp: datetime
    raw_payload_hash: str
    extraction_method: str = "direct_api"
    # additional metadata like LLM versions if used, headers, etc.

class SchemaVersion(BaseModel):
    version: str
    description: str
    released_at: datetime

class Source(BaseModel):
    id: str
    name: str
    url: str
    description: Optional[str] = None

class Dataset(BaseModel):
    id: str
    source_id: str
    name: str
    schema_version: str

class RecordStatus(str, enum.Enum):
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    DELETED = "deleted"
    PENDING_VERIFICATION = "pending_verification"

class CanonicalRecord(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str
    dataset_id: str
    observed_at: datetime
    effective_at: datetime
    last_updated_at: datetime = Field(default_factory=datetime.utcnow)
    data: Dict[str, Any] # Must be a serialized domain model
    source_reference: str # Strict unique ID from source to prevent duplication
    content_hash: str # Hash of the data field
    schema_version: str
    normalization_version: str
    confidence: float = Field(ge=0.0, le=1.0)
    provenance: ProvenanceMetadata
    status: RecordStatus = RecordStatus.PENDING_VERIFICATION

    @field_validator('content_hash')
    @classmethod
    def validate_hash(cls, v, info):
        # We can validate if the hash matches the data payload
        data = info.data.get('data')
        if data is not None:
            dumped = json.dumps(data, sort_keys=True, separators=(',', ':'))
            expected_hash = hashlib.sha256(dumped.encode('utf-8')).hexdigest()
            if v != expected_hash:
                raise ValueError(f"Content hash {v} does not match data hash {expected_hash}")
        return v

    @field_validator('source_reference')
    @classmethod
    def validate_source_ref(cls, v):
        if not v or not v.strip():
            raise ValueError("source_reference cannot be empty")
        return v

class Observation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    record_id: str
    observed_at: datetime
    raw_data_snippet: Optional[Dict[str, Any]] = None

class FieldChange(BaseModel):
    affected_field: str
    old_value: Any
    new_value: Any
    
class Change(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    record_id: str
    source_reference: str
    previous_hash: Optional[str] = None
    new_hash: str
    diff: List[FieldChange]
    detected_at: datetime

class DataPRStatus(str, enum.Enum):
    OPEN = "open"
    VERIFIED = "verified"
    REJECTED = "rejected"
    MERGED = "merged"

class DataPR(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_id: str
    agent_id: str
    base_dataset_version: int
    proposed_dataset_version: int
    changes: List[Change]
    proposed_records: List[CanonicalRecord]
    status: DataPRStatus = DataPRStatus.OPEN
    source_snapshot: Optional[str] = None
    source_url: str
    schema_version: str
    normalization_version: str
    agent_run_id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Verification(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    pr_id: str
    verifier_agent_id: str
    source_checked: str
    passed: bool
    checks_performed: List[str]
    passed_checks: List[str]
    failed_checks: List[str]
    evidence: Dict[str, Any]
    notes: str
    verified_at: datetime = Field(default_factory=datetime.utcnow)

class AgentRun(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_id: str
    source_id: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    status: str = "running"
    records_processed: int = 0
    prs_created: int = 0
    error_log: Optional[str] = None
