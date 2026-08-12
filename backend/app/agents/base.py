from abc import ABC
import logging
import uuid
import json
import os
import hashlib
from datetime import datetime
from typing import Any, Dict, List

from app.agents.sources.adapter import SourceAdapter
from app.agents.events import AgentEvent, EventType
from app.models.canonical import DataPR, Change
from app.agents.event_bus import bus, SourceChanged, DataPRCreated
from sqlalchemy import select, desc
from app.db.database import SessionLocal
from app.db.models import DBDataPR, DBChange, DBProposedRecord, DBDatasetVersion, DBAgentState
from app.agents.errors import SourceUnavailableError, RateLimitError, MalformedResponseError, SchemaDriftError
import httpx
from pydantic import ValidationError

logger = logging.getLogger(__name__)

STATE_FILE = "agent_states.json"

class BaseOwnerAgent:
    """
    Orchestrates the 10-step lifecycle for a single data source.
    """
    def __init__(self, agent_id: str, adapter: SourceAdapter):
        self.agent_id = agent_id
        self.adapter = adapter
        self.meta = adapter.get_metadata()
        self.source_id = self.meta["source_id"]

    def _emit(self, run_id: str, event_type: EventType, details: Dict[str, Any] = None):
        event = AgentEvent(
            agent_id=self.agent_id,
            run_id=run_id,
            event_type=event_type,
            details=details or {}
        )
        event.log()
        return event

    async def _get_previous_hash(self) -> str:
        async with SessionLocal() as session:
            res = await session.execute(select(DBAgentState).where(DBAgentState.agent_id == self.agent_id))
            state = res.scalar_one_or_none()
            if state and state.last_hash:
                return state.last_hash
        return None

    async def _update_state_status(self, status: str, error_msg: str = None, session=None):
        should_commit = False
        if not session:
            session = SessionLocal()
            should_commit = True
            
        res = await session.execute(select(DBAgentState).where(DBAgentState.agent_id == self.agent_id))
        state = res.scalar_one_or_none()
        if not state:
            state = DBAgentState(agent_id=self.agent_id, source_id=self.source_id)
            session.add(state)
            
        # Detect recovery
        if state.status in ["failing", "offline", "degraded"] and status == "healthy":
            status = "recovered"
            
        state.status = status
        state.last_error = error_msg
        
        if should_commit:
            await session.commit()
            await session.close()

    async def _save_current_hash(self, current_hash: str, session):
        res = await session.execute(select(DBAgentState).where(DBAgentState.agent_id == self.agent_id))
        state = res.scalar_one_or_none()
        if not state:
            state = DBAgentState(agent_id=self.agent_id, source_id=self.source_id)
            session.add(state)
        state.last_hash = current_hash
        state.last_change_detected_at = datetime.utcnow()

    async def _get_previous_records(self) -> List[CanonicalRecord]:
        from app.db.models import DBCanonicalRecord
        async with SessionLocal() as session:
            res = await session.execute(
                select(DBCanonicalRecord).where(
                    DBCanonicalRecord.source_id == self.source_id,
                    DBCanonicalRecord.status == "active"
                )
            )
            db_records = res.scalars().all()
            # Convert DB model to Pydantic model for diffing
            records = []
            for r in db_records:
                records.append(CanonicalRecord(
                    id=r.id,
                    source_id=r.source_id,
                    dataset_id=r.dataset_id,
                    observed_at=r.observed_at,
                    effective_at=r.effective_at,
                    last_updated_at=r.last_updated_at,
                    data=r.data,
                    source_reference=r.source_reference,
                    content_hash=r.content_hash,
                    schema_version=r.schema_version,
                    normalization_version=r.normalization_version,
                    confidence=r.confidence,
                    provenance=r.provenance
                ))
            return records

    async def run(self, run_id: str = None):
        if not run_id:
            run_id = str(uuid.uuid4())
        self._emit(run_id, EventType.SOURCE_CHECK_STARTED, {"url": self.meta["url"]})
        
        try:
            fetch_timestamp = datetime.utcnow()
            
            # Step 2: Fetching source
            try:
                raw_data = await self.adapter.fetch()
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    raise RateLimitError(str(e))
                raise SourceUnavailableError(str(e))
            except httpx.RequestError as e:
                raise SourceUnavailableError(str(e))
            except json.JSONDecodeError as e:
                raise MalformedResponseError(str(e))
            except Exception as e:
                if "json" in str(e).lower() or "decode" in str(e).lower():
                    raise MalformedResponseError(str(e))
                raise
                
            self._emit(run_id, EventType.SOURCE_FETCHED, {"source": self.source_id})
            
            # Step 5, 6, 7: Normalization & Canonicalization
            try:
                parsed = self.adapter.parse(raw_data)
                normalized = self.adapter.normalize(parsed)
            except KeyError as e:
                raise SchemaDriftError(f"Missing expected field: {e}")
            except Exception as e:
                raise SchemaDriftError(f"Error during parse/normalize: {e}")
                
            self._emit(run_id, EventType.NORMALIZATION_COMPLETED)
            
            try:
                validated_model = self.adapter.validate(normalized)
            except ValidationError as e:
                raise SchemaDriftError(f"Validation failed (schema drift): {e}")
            except Exception as e:
                self._emit(run_id, EventType.VALIDATION_FAILED, {"error": str(e)})
                raise
                
            try:
                canonical_records = self.adapter.to_canonical(
                    raw_data=raw_data,
                    parsed_data=parsed,
                    normalized_data=normalized,
                    validated_model=validated_model,
                    fetch_timestamp=fetch_timestamp
                )
            except KeyError as e:
                raise SchemaDriftError(f"Missing field in to_canonical: {e}")
            
            # Successful validation means the source is functionally healthy.
            await self._update_state_status("healthy")
            
            from app.agents.detector import ChangeDetector
            detector = ChangeDetector(ignored_fields=self.adapter.get_ignored_fields())
            
            # Semantic hash based on cleaned canonical data payloads
            current_canonical_dumps = [r.data for r in canonical_records]
            current_hash = detector.hash_payload(current_canonical_dumps)
            
            prev_hash = await self._get_previous_hash()
            if prev_hash == current_hash:
                self._emit(run_id, EventType.SOURCE_UNCHANGED, {"hash": current_hash})
                return
            
            self._emit(run_id, EventType.SOURCE_CHANGED, {"old_hash": prev_hash, "new_hash": current_hash})
            await bus.publish(SourceChanged(
                source_id=self.source_id,
                old_hash=prev_hash,
                new_hash=current_hash,
                agent_id=self.agent_id
            ))
            
            # Idempotency Check: Do not create duplicate PRs if one is already open
            async with SessionLocal() as session:
                existing_pr_res = await session.execute(
                    select(DBDataPR).where(
                        DBDataPR.source_id == self.source_id,
                        DBDataPR.status.in_(["open", "verifying"])
                    )
                )
                if existing_pr_res.scalar_one_or_none():
                    logger.info(f"Idempotency: An open PR already exists for source {self.source_id}. Skipping PR creation.")
                    return
            
            # Record-level Diffing
            old_records = await self._get_previous_records()
            old_records_map = {r.source_reference: r for r in old_records}
            
            changes = []
            for record in canonical_records:
                old_record = old_records_map.get(record.source_reference)
                if old_record:
                    field_diffs = detector.diff_records(old_record, record)
                    if field_diffs:
                        changes.append(Change(
                            record_id=record.id,
                            source_reference=record.source_reference,
                            previous_hash=old_record.content_hash,
                            new_hash=record.content_hash,
                            diff=field_diffs,
                            detected_at=fetch_timestamp
                        ))
                else:
                    # New record (no diff to show, just a new record hash)
                    changes.append(Change(
                        record_id=record.id,
                        source_reference=record.source_reference,
                        previous_hash=None,
                        new_hash=record.content_hash,
                        diff=[],
                        detected_at=fetch_timestamp
                    ))
            
            pr = DataPR(
                source_id=self.source_id,
                agent_id=self.agent_id,
                base_dataset_version=1, # Default placeholder, will be set below
                proposed_dataset_version=2, # Default placeholder
                changes=changes,
                proposed_records=canonical_records,
                source_url=self.meta["url"],
                schema_version="1.0",
                normalization_version="1.0",
                agent_run_id=run_id
            )
            
            # Persist PR to database
            
            async with SessionLocal() as session:
                # 1. Get latest dataset version
                ver_res = await session.execute(select(DBDatasetVersion).order_by(desc(DBDatasetVersion.id)).limit(1))
                latest_version = ver_res.scalar_one_or_none()
                if not latest_version:
                    base_version = 1
                else:
                    base_version = latest_version.id
                    
                pr.base_dataset_version = base_version
                pr.proposed_dataset_version = base_version + 1
                
                # 2. Insert DBDataPR
                db_pr = DBDataPR(
                    id=pr.id,
                    source_id=pr.source_id,
                    agent_id=pr.agent_id,
                    base_dataset_version=pr.base_dataset_version,
                    proposed_dataset_version=pr.proposed_dataset_version,
                    status=pr.status.value,
                    source_url=pr.source_url,
                    schema_version=pr.schema_version,
                    normalization_version=pr.normalization_version,
                    agent_run_id=pr.agent_run_id,
                    created_at=pr.created_at
                )
                session.add(db_pr)
                
                # 3. Insert DBChanges
                for c in pr.changes:
                    db_change = DBChange(
                        id=c.id,
                        pr_id=pr.id,
                        record_id=c.record_id,
                        source_reference=c.source_reference,
                        previous_hash=c.previous_hash,
                        new_hash=c.new_hash,
                        diff=[diff.model_dump(mode='json') for diff in c.diff],
                        detected_at=c.detected_at
                    )
                    session.add(db_change)
                
                # 4. Insert DBProposedRecords
                for r in pr.proposed_records:
                    db_prec = DBProposedRecord(
                        id=r.id,
                        pr_id=pr.id,
                        source_id=r.source_id,
                        dataset_id=r.dataset_id,
                        observed_at=r.observed_at,
                        effective_at=r.effective_at,
                        last_updated_at=r.last_updated_at,
                        data=r.data,
                        source_reference=r.source_reference,
                        content_hash=r.content_hash,
                        schema_version=r.schema_version,
                        normalization_version=r.normalization_version,
                        confidence=r.confidence,
                        provenance=r.provenance.model_dump(mode='json')
                    )
                    session.add(db_prec)
                    
                # 5. Audit Log
                from app.services.audit import AuditService
                await AuditService.append(
                    session=session,
                    entity_type="pr",
                    entity_id=pr.id,
                    action="PR_CREATED",
                    new_value=str(len(changes)) + " changes",
                    actor=self.agent_id
                )
                    
                # Step 9: Recording run (saving state)
                await self._save_current_hash(current_hash, session)
                await session.commit()
            
            self._emit(run_id, EventType.DATA_PR_CREATED, {"pr_id": pr.id, "records_changed": len(changes)})
            await bus.publish(DataPRCreated(
                pr_id=pr.id,
                source_id=self.source_id,
                agent_id=self.agent_id
            ))
            
            # Successful run
            return canonical_records
            
        except SourceUnavailableError as e:
            self._emit(run_id, EventType.SOURCE_OFFLINE, {"error": str(e)})
            await self._update_state_status("offline", str(e))
            raise
        except RateLimitError as e:
            self._emit(run_id, EventType.AGENT_FAILED, {"error": str(e)})
            await self._update_state_status("degraded", f"Rate limited: {str(e)}")
            raise
        except MalformedResponseError as e:
            self._emit(run_id, EventType.AGENT_FAILED, {"error": str(e)})
            await self._update_state_status("failing", f"Malformed response: {str(e)}")
            raise
        except SchemaDriftError as e:
            self._emit(run_id, EventType.SCHEMA_DRIFT, {"error": str(e)})
            await self._update_state_status("degraded", f"Schema drift: {str(e)}")
            raise
        except Exception as e:
            self._emit(run_id, EventType.AGENT_FAILED, {"error": str(e)})
            await self._update_state_status("failing", str(e))
            raise
