from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
import json
from datetime import datetime

from app.db.database import get_db
from app.db.models import DBDataPR, DBChange, DBProposedRecord, DBCanonicalRecord, DBDatasetVersion, DBVerification
from app.services.audit import AuditService

router = APIRouter(prefix="/api/prs", tags=["prs"])

@router.get("")
async def list_prs(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DBDataPR).order_by(desc(DBDataPR.created_at)))
    prs = result.scalars().all()
    return [{"id": pr.id, "source_id": pr.source_id, "status": pr.status, "created_at": pr.created_at} for pr in prs]

@router.get("/{pr_id}")
async def get_pr(pr_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DBDataPR).where(DBDataPR.id == pr_id))
    pr = result.scalar_one_or_none()
    if not pr:
        raise HTTPException(status_code=404, detail="PR not found")
        
    return {
        "id": pr.id,
        "source_id": pr.source_id,
        "agent_id": pr.agent_id,
        "status": pr.status,
        "base_dataset_version": pr.base_dataset_version,
        "proposed_dataset_version": pr.proposed_dataset_version,
        "created_at": pr.created_at
    }

@router.get("/{pr_id}/diff")
async def get_pr_diff(pr_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DBChange).where(DBChange.pr_id == pr_id))
    changes = result.scalars().all()
    return [{"record_id": c.record_id, "diff": c.diff} for c in changes]

@router.get("/{pr_id}/provenance")
async def get_pr_provenance(pr_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DBProposedRecord).where(DBProposedRecord.pr_id == pr_id))
    records = result.scalars().all()
    return [{"record_id": r.id, "provenance": r.provenance} for r in records]

@router.post("/{pr_id}/approve")
async def approve_pr(pr_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DBDataPR).where(DBDataPR.id == pr_id))
    pr = result.scalar_one_or_none()
    if not pr:
        raise HTTPException(status_code=404, detail="PR not found")
        
    if pr.status != "open" and pr.status != "verifying":
        raise HTTPException(status_code=400, detail=f"Cannot approve PR in status {pr.status}")
        
    pr.status = "approved"
    
    await AuditService.append(
        session=db,
        entity_type="pr",
        entity_id=pr.id,
        action="STATUS_CHANGE",
        new_value="approved",
        actor="verifier"
    )
    await db.commit()
    return {"status": "success", "message": "PR approved"}

@router.post("/{pr_id}/reject")
async def reject_pr(pr_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DBDataPR).where(DBDataPR.id == pr_id))
    pr = result.scalar_one_or_none()
    if not pr:
        raise HTTPException(status_code=404, detail="PR not found")
        
    pr.status = "rejected"
    await AuditService.append(
        session=db,
        entity_type="pr",
        entity_id=pr.id,
        action="STATUS_CHANGE",
        new_value="rejected",
        actor="verifier"
    )
    await db.commit()
    return {"status": "success", "message": "PR rejected"}

@router.post("/{pr_id}/merge")
async def merge_pr(pr_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DBDataPR).where(DBDataPR.id == pr_id))
    pr = result.scalar_one_or_none()
    if not pr:
        raise HTTPException(status_code=404, detail="PR not found")
        
    if pr.status != "approved":
        raise HTTPException(status_code=400, detail="PR must be approved before merging")

    # Optimistic Concurrency Check
    # Get current latest version
    ver_res = await db.execute(select(DBDatasetVersion).order_by(desc(DBDatasetVersion.id)).limit(1))
    latest_version = ver_res.scalar_one()
    
    if latest_version.id != pr.base_dataset_version:
        # CONCURRENCY FAILURE!
        pr.status = "failed"
        await AuditService.append(
            session=db,
            entity_type="pr",
            entity_id=pr.id,
            action="MERGE_FAILED",
            new_value=str(latest_version.id),
            actor="system"
        )
        await db.commit()
        raise HTTPException(status_code=409, detail=f"Optimistic concurrency failure. PR base version {pr.base_dataset_version} is behind current version {latest_version.id}")

    # Create new dataset version
    new_version = DBDatasetVersion(id=latest_version.id + 1, description=f"Merged PR {pr.id}")
    db.add(new_version)
    
    # Get proposed records
    rec_res = await db.execute(select(DBProposedRecord).where(DBProposedRecord.pr_id == pr_id))
    proposed_records = rec_res.scalars().all()
    
    for prec in proposed_records:
        # Supersede old canonical record if it exists
        old_rec_res = await db.execute(
            select(DBCanonicalRecord).where(
                DBCanonicalRecord.source_reference == prec.source_reference,
                DBCanonicalRecord.status == "active"
            )
        )
        old_rec = old_rec_res.scalar_one_or_none()
        if old_rec:
            old_rec.status = "superseded"
            old_rec.effective_at = datetime.utcnow() # Ends its valid timeframe
            
        # Create new active record
        new_canon = DBCanonicalRecord(
            id=prec.id,
            source_id=prec.source_id,
            dataset_id=prec.dataset_id,
            observed_at=prec.observed_at,
            effective_at=datetime.utcnow(),
            last_updated_at=prec.last_updated_at,
            data=prec.data,
            source_reference=prec.source_reference,
            content_hash=prec.content_hash,
            schema_version=prec.schema_version,
            normalization_version=prec.normalization_version,
            confidence=prec.confidence,
            provenance=prec.provenance,
            status="active",
            created_in_version=new_version.id
        )
        db.add(new_canon)
        
    pr.status = "merged"
    pr.proposed_dataset_version = new_version.id
    
    await AuditService.append(
        session=db,
        entity_type="pr",
        entity_id=pr.id,
        action="STATUS_CHANGE",
        new_value="merged",
        actor="system"
    )
    
    await db.commit()
    
    return {"status": "success", "message": "PR merged successfully", "new_version": new_version.id}

@router.get("/{pr_id}/verification")
async def get_pr_verification(pr_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(DBVerification).where(DBVerification.pr_id == pr_id).order_by(desc(DBVerification.verified_at)))
    verifications = result.scalars().all()
    return verifications

@router.post("/{pr_id}/verify")
async def trigger_verification(pr_id: str, db: AsyncSession = Depends(get_db)):
    from app.agents.verifier import VerifierAgent
    verifier = VerifierAgent()
    try:
        report = await verifier.verify_pr(pr_id)
        return {"status": "success", "report": report.model_dump()}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
