import logging
import uuid
import httpx
from datetime import datetime
from typing import Any, Dict, List

from sqlalchemy import select
from app.db.database import SessionLocal
from app.db.models import DBDataPR, DBProposedRecord, DBVerification
from app.services.audit import AuditService
from app.agents.registry import registry
from app.agents.detector import ChangeDetector
from app.models.canonical import Verification
from app.agents.event_bus import bus, VerificationStarted, VerificationPassed, VerificationFailed

logger = logging.getLogger(__name__)

class VerifierAgent:
    def __init__(self, agent_id: str = "core_verifier"):
        self.agent_id = agent_id

    async def verify_pr(self, pr_id: str) -> Verification:
        async with SessionLocal() as session:
            result = await session.execute(select(DBDataPR).where(DBDataPR.id == pr_id))
            pr = result.scalar_one_or_none()
            if not pr:
                raise ValueError(f"PR {pr_id} not found")

            if pr.status != "open":
                raise ValueError(f"PR {pr_id} is not open (status: {pr.status})")

            pr.status = "verifying"
            await session.commit()
            
            await bus.publish(VerificationStarted(
                pr_id=pr.id,
                verifier_agent_id=self.agent_id
            ))
            
            report = Verification(
                pr_id=pr.id,
                verifier_agent_id=self.agent_id,
                source_checked=pr.source_url,
                passed=False,
                checks_performed=[],
                passed_checks=[],
                failed_checks=[],
                evidence={},
                notes=""
            )
            
            try:
                # Retrieve proposed records
                rec_res = await session.execute(select(DBProposedRecord).where(DBProposedRecord.pr_id == pr.id))
                proposed_records = rec_res.scalars().all()

                # Step 1: Reachability & Adapter lookup
                report.checks_performed.append("source_reachable")
                adapter = registry.get_adapter(pr.source_id)
                if not adapter:
                    report.failed_checks.append("source_reachable")
                    report.notes = f"Adapter for {pr.source_id} not found."
                    return await self._finalize(session, pr, report)
                
                try:
                    raw_data = await adapter.fetch()
                    report.passed_checks.append("source_reachable")
                except Exception as e:
                    report.failed_checks.append("source_reachable")
                    report.evidence["fetch_error"] = str(e)
                    report.notes = "Source is unreachable."
                    return await self._finalize(session, pr, report)
                    
                # Step 2: Schema Validation & Typing
                report.checks_performed.extend(["schema_valid", "types_correct", "no_unexpected_fields"])
                try:
                    parsed = adapter.parse(raw_data)
                    normalized = adapter.normalize(parsed)
                    validated_model = adapter.validate(normalized)
                    canonical_records = adapter.to_canonical(
                        raw_data=raw_data,
                        parsed_data=parsed,
                        normalized_data=normalized,
                        validated_model=validated_model,
                        fetch_timestamp=datetime.utcnow()
                    )
                    report.passed_checks.extend(["schema_valid", "types_correct", "no_unexpected_fields"])
                except Exception as e:
                    report.failed_checks.extend(["schema_valid"])
                    report.evidence["schema_error"] = str(e)
                    report.notes = "Data from source violates strict schema."
                    return await self._finalize(session, pr, report)

                # Step 3: Semantic & Provenance Validation
                # We expect the live source payload hashes to match the proposed PR hashes
                report.checks_performed.extend(["proposed_value_exists", "proposed_value_matches", "provenance_valid"])
                
                live_hashes = {r.content_hash for r in canonical_records}
                proposed_hashes = {r.content_hash for r in proposed_records}
                
                detector = ChangeDetector(ignored_fields=adapter.get_ignored_fields())
                
                failed = False
                for prec in proposed_records:
                    if prec.content_hash not in live_hashes:
                        # Re-calculate hash to ensure it wasn't forged
                        computed = detector.hash_payload(prec.data)
                        if computed != prec.content_hash:
                            report.failed_checks.append("provenance_valid")
                            report.evidence["forged_hash"] = prec.content_hash
                            report.notes = "PR contains a forged content hash."
                            failed = True
                            break
                        else:
                            report.failed_checks.append("proposed_value_exists")
                            report.evidence["missing_record"] = prec.source_reference
                            report.notes = "Proposed changes do not exist in the live source."
                            failed = True
                            break
                            
                if failed:
                    return await self._finalize(session, pr, report)
                    
                report.passed_checks.extend(["proposed_value_exists", "proposed_value_matches", "provenance_valid"])
                
                # If all checks pass
                report.passed = True
                report.notes = "All independent verifications passed."
                return await self._finalize(session, pr, report)

            except Exception as e:
                report.notes = f"Internal verifier error: {str(e)}"
                return await self._finalize(session, pr, report)


    async def _finalize(self, session, pr: DBDataPR, report: Verification) -> Verification:
        pr.status = "approved" if report.passed else "rejected"
        
        db_rep = DBVerification(
            id=report.id,
            pr_id=report.pr_id,
            verifier_agent_id=report.verifier_agent_id,
            source_checked=report.source_checked,
            passed=report.passed,
            checks_performed=report.checks_performed,
            passed_checks=report.passed_checks,
            failed_checks=report.failed_checks,
            evidence=report.evidence,
            notes=report.notes,
            verified_at=report.verified_at
        )
        session.add(db_rep)
        
        await AuditService.append(
            session=session,
            entity_type="pr",
            entity_id=pr.id,
            action="VERIFICATION",
            new_value="passed" if report.passed else "failed",
            actor=self.agent_id
        )
        
        await session.commit()
        
        if report.passed:
            await bus.publish(VerificationPassed(pr_id=pr.id, verification_id=report.id))
        else:
            await bus.publish(VerificationFailed(pr_id=pr.id, verification_id=report.id, failed_checks=report.failed_checks))
            
        return report
