from sqlalchemy import Column, Integer, String, DateTime, JSON, Enum
from sqlalchemy.orm import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class PRStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"
    MERGED = "merged"

class DataPR(Base):
    """
    Represents a proposed change to the canonical dataset.
    """
    __tablename__ = "data_prs"

    id = Column(Integer, primary_key=True, index=True)
    source_id = Column(String, index=True, nullable=False)
    agent_id = Column(String, nullable=False)
    
    # The actual proposed data in canonical schema
    proposed_data = Column(JSON, nullable=False)
    
    status = Column(Enum(PRStatus), default=PRStatus.PENDING, index=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Optional fields for verification notes or rejection reasons
    verification_notes = Column(String, nullable=True)
