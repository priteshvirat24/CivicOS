from sqlalchemy import Column, String, Integer, Float, DateTime, Boolean, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime

from .database import Base

class DBDatasetVersion(Base):
    __tablename__ = "dataset_versions"
    id = Column(Integer, primary_key=True, index=True) # E.g., 1, 2, 3...
    created_at = Column(DateTime, default=datetime.utcnow)
    description = Column(String, nullable=True)

class DBDataPR(Base):
    __tablename__ = "data_prs"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    source_id = Column(String, index=True)
    agent_id = Column(String)
    base_dataset_version = Column(Integer, ForeignKey("dataset_versions.id"))
    proposed_dataset_version = Column(Integer) # This would become the new version if merged
    status = Column(String, default="open") # open, verifying, approved, rejected, merged, failed
    source_snapshot = Column(String, nullable=True)
    source_url = Column(String)
    schema_version = Column(String)
    normalization_version = Column(String)
    agent_run_id = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    changes = relationship("DBChange", back_populates="pr", cascade="all, delete-orphan")
    proposed_records = relationship("DBProposedRecord", back_populates="pr", cascade="all, delete-orphan")

class DBChange(Base):
    __tablename__ = "changes"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    pr_id = Column(String, ForeignKey("data_prs.id"))
    record_id = Column(String)
    source_reference = Column(String)
    previous_hash = Column(String, nullable=True)
    new_hash = Column(String)
    diff = Column(JSON) # List of FieldChange objects serialized
    detected_at = Column(DateTime)
    
    pr = relationship("DBDataPR", back_populates="changes")

class DBProposedRecord(Base):
    __tablename__ = "proposed_records"
    id = Column(String, primary_key=True)
    pr_id = Column(String, ForeignKey("data_prs.id"))
    source_id = Column(String)
    dataset_id = Column(String)
    observed_at = Column(DateTime)
    effective_at = Column(DateTime)
    last_updated_at = Column(DateTime)
    data = Column(JSON)
    source_reference = Column(String)
    content_hash = Column(String)
    schema_version = Column(String)
    normalization_version = Column(String)
    confidence = Column(Float)
    provenance = Column(JSON)
    
    pr = relationship("DBDataPR", back_populates="proposed_records")

class DBCanonicalRecord(Base):
    __tablename__ = "canonical_records"
    id = Column(String, primary_key=True)
    source_id = Column(String, index=True)
    dataset_id = Column(String, index=True)
    observed_at = Column(DateTime)
    effective_at = Column(DateTime)
    last_updated_at = Column(DateTime)
    data = Column(JSON)
    source_reference = Column(String, index=True) # Need this to be indexed for fast lookups
    content_hash = Column(String)
    schema_version = Column(String)
    normalization_version = Column(String)
    confidence = Column(Float)
    provenance = Column(JSON)
    status = Column(String) # active, superseded, deleted
    created_in_version = Column(Integer, ForeignKey("dataset_versions.id"))

class DBVerification(Base):
    __tablename__ = "verifications"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    pr_id = Column(String, ForeignKey("data_prs.id"))
    verifier_agent_id = Column(String)
    source_checked = Column(String)
    passed = Column(Boolean)
    checks_performed = Column(JSON)
    passed_checks = Column(JSON)
    failed_checks = Column(JSON)
    evidence = Column(JSON)
    notes = Column(String)
    verified_at = Column(DateTime, default=datetime.utcnow)

class DBAuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    entity_type = Column(String) # pr, record
    entity_id = Column(String)
    action = Column(String) # e.g. STATUS_CHANGE
    old_value = Column(String, nullable=True)
    new_value = Column(String, nullable=True)
    actor = Column(String) # agent_id or user_id
    timestamp = Column(DateTime, default=datetime.utcnow)
    previous_log_id = Column(String, ForeignKey("audit_logs.id"), nullable=True)
    signature = Column(String, unique=True, nullable=True)

class DBAgentRun(Base):
    __tablename__ = "agent_runs"
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    agent_id = Column(String, index=True)
    source_id = Column(String, index=True)
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    status = Column(String, default="running") # running, success, failed, timeout
    error_message = Column(String, nullable=True)
    records_processed = Column(Integer, default=0)

class DBAgentState(Base):
    __tablename__ = "agent_states"
    agent_id = Column(String, primary_key=True)
    source_id = Column(String, index=True)
    status = Column(String, default="healthy") # healthy, failing
    last_run_at = Column(DateTime, nullable=True)
    last_successful_run_at = Column(DateTime, nullable=True)
    last_change_detected_at = Column(DateTime, nullable=True)
    last_error = Column(String, nullable=True)
    last_hash = Column(String, nullable=True)
    current_version = Column(String, nullable=True)
