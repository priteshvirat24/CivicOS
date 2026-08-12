import hashlib
import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.db.models import DBAuditLog
import uuid
from datetime import datetime
from typing import Optional

class AuditService:
    @staticmethod
    def hash_log(log_data: dict, previous_signature: Optional[str]) -> str:
        # Canonicalize the dictionary for hashing
        payload = {
            "entity_type": log_data.get("entity_type"),
            "entity_id": log_data.get("entity_id"),
            "action": log_data.get("action"),
            "old_value": log_data.get("old_value"),
            "new_value": log_data.get("new_value"),
            "actor": log_data.get("actor"),
            "timestamp": log_data.get("timestamp"),
            "previous_signature": previous_signature
        }
        dumped = json.dumps(payload, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(dumped.encode('utf-8')).hexdigest()

    @classmethod
    async def append(cls, session: AsyncSession, entity_type: str, entity_id: str, action: str, actor: str, old_value: str = None, new_value: str = None):
        # 1. Fetch the last log in the system to get its signature
        res = await session.execute(
            select(DBAuditLog).order_by(desc(DBAuditLog.timestamp), desc(DBAuditLog.id)).limit(1)
        )
        last_log = res.scalar_one_or_none()
        
        previous_signature = last_log.signature if last_log else None
        previous_log_id = last_log.id if last_log else None
        
        timestamp = datetime.utcnow()
        log_data = {
            "entity_type": entity_type,
            "entity_id": entity_id,
            "action": action,
            "old_value": old_value,
            "new_value": new_value,
            "actor": actor,
            "timestamp": timestamp.isoformat()
        }
        
        signature = cls.hash_log(log_data, previous_signature)
        
        new_log = DBAuditLog(
            id=str(uuid.uuid4()),
            entity_type=entity_type,
            entity_id=entity_id,
            action=action,
            old_value=old_value,
            new_value=new_value,
            actor=actor,
            timestamp=timestamp,
            previous_log_id=previous_log_id,
            signature=signature
        )
        session.add(new_log)
        # Flush to make it available for the next append if there are multiple in one transaction
        await session.flush()
        return new_log
