from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.db.database import get_db
from app.db.models import DBCanonicalRecord

router = APIRouter(prefix="/api/dataset", tags=["dataset"])

@router.get("/")
async def get_active_dataset(db: AsyncSession = Depends(get_db)):
    """
    Returns the active canonical records to populate the Dataset Explorer.
    """
    res = await db.execute(
        select(DBCanonicalRecord)
        .where(DBCanonicalRecord.status == "active")
        .order_by(DBCanonicalRecord.last_updated_at.desc())
    )
    records = res.scalars().all()
    
    return {"status": "success", "records": records}

@router.get("/{record_id}/provenance")
async def get_record_provenance(record_id: str, db: AsyncSession = Depends(get_db)):
    """
    Returns the full cryptographic provenance chain for a specific record.
    """
    from app.db.models import DBDataPR, DBChange, DBVerification, DBAuditLog
    
    # 1. Fetch Canonical Record
    res = await db.execute(select(DBCanonicalRecord).where(DBCanonicalRecord.id == record_id))
    record = res.scalar_one_or_none()
    if not record:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Record not found")
        
    # 2. Fetch the Data PR it came from
    # We can infer PR from the ProposedRecord if we had a link, or we can look up the DBChange for this record
    change_res = await db.execute(
        select(DBChange).where(DBChange.record_id == record_id).order_by(DBChange.detected_at.desc()).limit(1)
    )
    change = change_res.scalar_one_or_none()
    
    pr = None
    verification = None
    diff = None
    source_evidence = None
    
    if change:
        diff = change.diff
        pr_res = await db.execute(select(DBDataPR).where(DBDataPR.id == change.pr_id))
        pr = pr_res.scalar_one_or_none()
        
        if pr:
            source_evidence = pr.source_snapshot
            ver_res = await db.execute(select(DBVerification).where(DBVerification.pr_id == pr.id))
            verification = ver_res.scalar_one_or_none()
            
    # 3. Fetch Audit Logs related to this record or PR
    audit_res = await db.execute(
        select(DBAuditLog).where(
            (DBAuditLog.entity_id == record_id) | 
            (DBAuditLog.entity_id == (pr.id if pr else ""))
        ).order_by(DBAuditLog.timestamp.desc())
    )
    audits = audit_res.scalars().all()
    
    return {
        "status": "success",
        "record": record,
        "pr": pr,
        "change": change,
        "diff": diff,
        "verification": verification,
        "source_evidence": source_evidence,
        "audit_trail": audits
    }
