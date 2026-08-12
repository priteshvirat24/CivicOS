from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from typing import List, Dict, Any
import asyncio

from app.db.database import get_db
from app.db.models import DBAgentState, DBAgentRun
from app.agents.orchestrator import run_all_agents

router = APIRouter(prefix="/api/agents", tags=["agents"])

@router.get("/health")
async def get_agents_health(db: AsyncSession = Depends(get_db)):
    """
    Returns the comprehensive list of agents, their current status, last run durations, and last errors.
    """
    result = await db.execute(select(DBAgentState).order_by(DBAgentState.agent_id))
    states = result.scalars().all()
    
    health_data = []
    for state in states:
        # Get last run for duration
        run_res = await db.execute(
            select(DBAgentRun)
            .where(DBAgentRun.agent_id == state.agent_id)
            .order_by(desc(DBAgentRun.started_at))
            .limit(1)
        )
        last_run = run_res.scalar_one_or_none()
        
        health_data.append({
            "agent_id": state.agent_id,
            "source_id": state.source_id,
            "status": state.status,
            "last_run_at": state.last_run_at,
            "last_successful_run_at": state.last_successful_run_at,
            "last_change_detected_at": state.last_change_detected_at,
            "last_error": state.last_error,
            "last_hash": state.last_hash,
            "current_version": state.current_version,
            "last_run_duration_ms": last_run.duration_ms if last_run else None,
            "last_run_status": last_run.status if last_run else None
        })
        
    return {"status": "success", "agents": health_data}

@router.get("/{agent_id}/runs")
async def get_agent_runs(agent_id: str, limit: int = 20, offset: int = 0, db: AsyncSession = Depends(get_db)):
    """
    Returns the paginated run history for an agent.
    """
    result = await db.execute(
        select(DBAgentRun)
        .where(DBAgentRun.agent_id == agent_id)
        .order_by(desc(DBAgentRun.started_at))
        .limit(limit)
        .offset(offset)
    )
    runs = result.scalars().all()
    return {"status": "success", "runs": runs}

from pydantic import BaseModel

class TriggerRequest(BaseModel):
    agent_id: str = None

@router.post("/trigger")
async def trigger_agents(req: TriggerRequest, background_tasks: BackgroundTasks):
    """
    Allows triggering agents concurrently on-demand.
    """
    background_tasks.add_task(run_all_agents, req.agent_id)
    return {"status": "success", "message": "Agent scheduler triggered in background"}
