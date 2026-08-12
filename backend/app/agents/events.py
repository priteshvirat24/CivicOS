from pydantic import BaseModel, Field
from datetime import datetime
import enum
import uuid
from typing import Optional, Any, Dict

class EventType(str, enum.Enum):
    SOURCE_CHECK_STARTED = "SOURCE_CHECK_STARTED"
    SOURCE_FETCHED = "SOURCE_FETCHED"
    SOURCE_CHANGED = "SOURCE_CHANGED"
    SOURCE_UNCHANGED = "SOURCE_UNCHANGED"
    NORMALIZATION_COMPLETED = "NORMALIZATION_COMPLETED"
    DATA_PR_CREATED = "DATA_PR_CREATED"
    VERIFICATION_FAILED = "verification_failed"
    VERIFICATION_PASSED = "verification_passed"
    DATA_PR_MERGED = "data_pr_merged"
    SCHEMA_DRIFT = "schema_drift"
    SOURCE_OFFLINE = "source_offline"
    VALIDATION_FAILED = "VALIDATION_FAILED"
    AGENT_FAILED = "AGENT_FAILED"

class AgentEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    agent_id: str
    run_id: str
    event_type: EventType
    details: Dict[str, Any] = Field(default_factory=dict)
    
    def log(self):
        print(f"[{self.timestamp.isoformat()}] [{self.agent_id}] [{self.event_type.value}] - {self.details}")
