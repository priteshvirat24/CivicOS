import asyncio
import logging
from typing import List

from app.agents.registry import registry
from app.agents.base import BaseOwnerAgent
from app.agents.verifier import VerifierAgent
from app.agents.event_bus import (
    bus, DataPRCreated, VerificationPassed, VerificationFailed,
    DataPRMerged, DatasetUpdated, DeploymentTriggered
)
from app.api.routers.prs import merge_pr
from app.db.database import SessionLocal

logger = logging.getLogger(__name__)

# Event Handlers
async def on_pr_created(event: DataPRCreated):
    logger.info(f"Orchestrator: PR {event.pr_id} created by {event.agent_id}. Triggering Verifier.")
    verifier = VerifierAgent()
    try:
        await verifier.verify_pr(event.pr_id)
    except Exception as e:
        logger.error(f"Orchestrator: Verifier failed to process PR {event.pr_id}: {e}")

async def on_verification_passed(event: VerificationPassed):
    logger.info(f"Orchestrator: Verification passed for PR {event.pr_id}. Triggering Merge.")
    
    # We must mock the DB session dependency that FastAPI normally injects
    async with SessionLocal() as session:
        try:
            # We call the core logic of merge_pr from the router. Wait, merge_pr depends on DB session.
            # To decouple properly, I should extract the merge logic from the router, but for MVP:
            from app.db.models import DBDataPR, DBDatasetVersion, DBProposedRecord, DBCanonicalRecord
            from app.services.audit import AuditService
            from sqlalchemy import select, desc
            from datetime import datetime
            
            result = await session.execute(select(DBDataPR).where(DBDataPR.id == event.pr_id))
            pr = result.scalar_one_or_none()
            if not pr or pr.status != "approved":
                return

            ver_res = await session.execute(select(DBDatasetVersion).order_by(desc(DBDatasetVersion.id)).limit(1))
            latest_version = ver_res.scalar_one()
            
            if latest_version.id != pr.base_dataset_version:
                # Concurrency failure
                pr.status = "failed"
                await AuditService.append(
                    session=session,
                    entity_type="pr",
                    entity_id=pr.id,
                    action="MERGE_FAILED",
                    new_value="error",
                    actor="system"
                )
                await session.commit()
                return

            new_version = DBDatasetVersion(id=latest_version.id + 1, description=f"Merged PR {pr.id}")
            session.add(new_version)
            
            rec_res = await session.execute(select(DBProposedRecord).where(DBProposedRecord.pr_id == event.pr_id))
            proposed_records = rec_res.scalars().all()
            
            for prec in proposed_records:
                old_rec_res = await session.execute(
                    select(DBCanonicalRecord).where(
                        DBCanonicalRecord.source_reference == prec.source_reference,
                        DBCanonicalRecord.status == "active"
                    )
                )
                old_rec = old_rec_res.scalar_one_or_none()
                if old_rec:
                    old_rec.status = "superseded"
                    old_rec.effective_at = datetime.utcnow()
                    
                new_canon = DBCanonicalRecord(
                    id=prec.id, source_id=prec.source_id, dataset_id=prec.dataset_id,
                    observed_at=prec.observed_at, effective_at=datetime.utcnow(),
                    last_updated_at=prec.last_updated_at, data=prec.data,
                    source_reference=prec.source_reference, content_hash=prec.content_hash,
                    schema_version=prec.schema_version, normalization_version=prec.normalization_version,
                    confidence=prec.confidence, provenance=prec.provenance, status="active",
                    created_in_version=new_version.id
                )
                session.add(new_canon)
                
            pr.status = "merged"
            pr.proposed_dataset_version = new_version.id
            await AuditService.append(
                session=session,
                entity_type="pr",
                entity_id=pr.id,
                action="STATUS_CHANGE",
                new_value="merged",
                actor="system"
            )
            
            await session.commit()
            
            await bus.publish(DataPRMerged(pr_id=pr.id, new_version=new_version.id))
            
        except Exception as e:
            logger.error(f"Orchestrator: Failed to merge PR {event.pr_id}: {e}")

async def on_pr_merged(event: DataPRMerged):
    logger.info(f"Orchestrator: PR {event.pr_id} merged. Dataset is now v{event.new_version}")
    await bus.publish(DatasetUpdated(version=event.new_version))

async def on_dataset_updated(event: DatasetUpdated):
    logger.info(f"Orchestrator: Dataset updated to v{event.version}. Triggering UI deployment.")
    await bus.publish(DeploymentTriggered(version=event.version))

async def on_verification_failed(event: VerificationFailed):
    logger.warning(f"Orchestrator: PR {event.pr_id} failed verification: {event.failed_checks}")

def setup_orchestrator():
    bus.subscribe(DataPRCreated, on_pr_created)
    bus.subscribe(VerificationPassed, on_verification_passed)
    bus.subscribe(VerificationFailed, on_verification_failed)
    bus.subscribe(DataPRMerged, on_pr_merged)
    bus.subscribe(DatasetUpdated, on_dataset_updated)
    bus.start()

from app.db.models import DBAgentRun, DBAgentState
import uuid
import time
from datetime import datetime
from sqlalchemy import update, select

class AgentScheduler:
    def __init__(self, max_concurrent: int = 4, timeout_seconds: int = 15, max_retries: int = 1):
        self.semaphore = asyncio.Semaphore(max_concurrent)
        self.timeout = timeout_seconds
        self.max_retries = max_retries

    async def execute_agent(self, agent: BaseOwnerAgent):
        async with self.semaphore:
            source_id = agent.source_id
            agent_id = agent.agent_id
            
            # Start Run Tracking
            run_id = str(uuid.uuid4())
            start_time = datetime.utcnow()
            
            async with SessionLocal() as session:
                db_run = DBAgentRun(
                    id=run_id, agent_id=agent_id, source_id=source_id,
                    started_at=start_time, status="running"
                )
                session.add(db_run)
                
                # Update State
                res = await session.execute(select(DBAgentState).where(DBAgentState.agent_id == agent_id))
                state = res.scalar_one_or_none()
                if not state:
                    state = DBAgentState(agent_id=agent_id, source_id=source_id)
                    session.add(state)
                state.last_run_at = start_time
                await session.commit()
            
            retries = 0
            success = False
            error_msg = None
            
            while retries <= self.max_retries and not success:
                try:
                    # Execute with timeout
                    await asyncio.wait_for(agent.run(run_id=run_id), timeout=self.timeout)
                    success = True
                except asyncio.TimeoutError:
                    error_msg = f"Agent timed out after {self.timeout}s"
                    retries += 1
                    logger.error(f"[{agent_id}] {error_msg}. Retry {retries}/{self.max_retries}")
                except Exception as e:
                    error_msg = str(e)
                    retries += 1
                    logger.error(f"[{agent_id}] Failed: {error_msg}. Retry {retries}/{self.max_retries}")
                    
                if not success and retries <= self.max_retries:
                    # Exponential backoff
                    await asyncio.sleep(2 ** retries)
            
            end_time = datetime.utcnow()
            duration_ms = int((end_time - start_time).total_seconds() * 1000)
            
            # Finalize Run Tracking
            async with SessionLocal() as session:
                res = await session.execute(select(DBAgentRun).where(DBAgentRun.id == run_id))
                db_run = res.scalar_one()
                db_run.completed_at = end_time
                db_run.duration_ms = duration_ms
                
                res_state = await session.execute(select(DBAgentState).where(DBAgentState.agent_id == agent_id))
                state = res_state.scalar_one()
                
                if success:
                    db_run.status = "success"
                    state.status = "healthy"
                    state.last_successful_run_at = end_time
                    state.last_error = None
                else:
                    db_run.status = "timeout" if "timed out" in (error_msg or "") else "failed"
                    db_run.error_message = error_msg
                    state.status = "failing"
                    state.last_error = error_msg
                    
                await session.commit()
                
            if success:
                print(f"✅ {agent_id} COMPLETED successfully in {duration_ms}ms")
            else:
                print(f"❌ {agent_id} FAILED after {self.max_retries} retries in {duration_ms}ms: {error_msg}")
                return Exception(error_msg)
            return True

async def run_all_agents(target_agent_id: str = None):
    adapters = registry.get_all_adapters()
    agents: List[BaseOwnerAgent] = []
    
    for adapter in adapters:
        meta = adapter.get_metadata()
        agent_id = f"agent_{meta['source_id']}"
        if target_agent_id and agent_id != target_agent_id:
            continue
        agents.append(BaseOwnerAgent(agent_id=agent_id, adapter=adapter))
        
    print(f"\\n--- Launching {len(agents)} Autonomous Source Agents (Parallel Scheduler) ---\\n")
    
    scheduler = AgentScheduler(max_concurrent=4, timeout_seconds=20, max_retries=1)
    
    tasks = [scheduler.execute_agent(agent) for agent in agents]
    await asyncio.gather(*tasks, return_exceptions=True)
    
    print(f"\\n--- Execution Cycle Finished ---")

if __name__ == "__main__":
    setup_orchestrator()
    asyncio.run(run_all_agents())
