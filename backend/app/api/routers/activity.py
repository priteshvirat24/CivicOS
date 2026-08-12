from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc, union_all
from typing import List, Dict, Any
import asyncio

from app.db.database import get_db
from app.db.models import DBAgentRun, DBDataPR, DBAuditLog

router = APIRouter(prefix="/api/activity", tags=["activity"])

@router.get("/")
async def get_activity_feed(limit: int = 50, db: AsyncSession = Depends(get_db)):
    """
    Returns a unified chronological activity feed composed of Agent Runs and PR activities.
    """
    
    # We will fetch recent events from runs, PRs, and audit logs and merge them in Python
    # for simplicity, since unifying via SQL can be complex across disjoint models.
    
    # 1. Fetch recent agent runs
    runs_res = await db.execute(
        select(DBAgentRun)
        .order_by(desc(DBAgentRun.started_at))
        .limit(limit)
    )
    runs = runs_res.scalars().all()
    
    # 2. Fetch recent PRs
    prs_res = await db.execute(
        select(DBDataPR)
        .order_by(desc(DBDataPR.created_at))
        .limit(limit)
    )
    prs = prs_res.scalars().all()
    
    events = []
    
    # Map Runs
    for run in runs:
        events.append({
            "type": "agent_run",
            "timestamp": run.started_at,
            "agent_id": run.agent_id,
            "source_id": run.source_id,
            "status": run.status,
            "duration_ms": run.duration_ms,
            "error": run.error_message,
            "message": f"Agent {run.agent_id} completed check on {run.source_id}" if run.status == 'success' else f"Agent {run.agent_id} failed check on {run.source_id}"
        })
        
    # Map PRs
    for pr in prs:
        events.append({
            "type": "data_pr",
            "timestamp": pr.created_at,
            "pr_id": pr.id,
            "agent_id": pr.agent_id,
            "source_id": pr.source_id,
            "status": pr.status,
            "message": f"Data PR {pr.id[:8]} created by {pr.agent_id} for {pr.source_id}"
        })
        
    # Sort descending
    events.sort(key=lambda x: x["timestamp"], reverse=True)
    
    return {"status": "success", "events": events[:limit]}
