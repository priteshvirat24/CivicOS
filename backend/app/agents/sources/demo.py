from datetime import datetime
import httpx
from typing import Dict, Any, List

from .adapter import SourceAdapter
from app.models.canonical import CanonicalRecord

class DemoAdapter(SourceAdapter):
    """
    A controlled source adapter for the hackathon demo.
    Points to localhost:8000/api/demo/source
    """

    def get_metadata(self) -> Dict[str, str]:
        return {
            "source_id": "demo_scheme",
            "name": "Live Demo Scheme",
            "url": "http://localhost:8000/api/demo/source"
        }

    async def fetch(self) -> Dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(self.get_metadata()["url"])
            response.raise_for_status()
            return response.json()

    def parse(self, raw_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        return raw_data.get("records", [])

    def normalize(self, parsed_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return parsed_data

    def validate(self, normalized_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        return normalized_data

    def to_canonical(self, raw_data: Dict[str, Any], parsed_data: List[Dict[str, Any]], 
                     normalized_data: List[Dict[str, Any]], validated_model: List[Dict[str, Any]], 
                     fetch_timestamp: datetime) -> List[CanonicalRecord]:
        import hashlib
        import json
        from app.models.canonical import ProvenanceMetadata, CanonicalRecord
        
        records = []
        meta = self.get_metadata()
        raw_dump = json.dumps(raw_data, sort_keys=True)
        raw_hash = hashlib.sha256(raw_dump.encode('utf-8')).hexdigest()
        
        provenance = ProvenanceMetadata(
            agent_id="agent_" + meta["source_id"],
            fetch_url=meta["url"],
            fetch_timestamp=fetch_timestamp,
            raw_payload_hash=raw_hash,
            extraction_method="direct_api"
        )
        
        for item in validated_model:
            content_hash = hashlib.sha256(json.dumps(item, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()
            records.append(
                CanonicalRecord(
                    id=f"{meta['source_id']}_{item['id']}",
                    source_id=meta["source_id"],
                    dataset_id="demo_dataset",
                    observed_at=fetch_timestamp,
                    effective_at=fetch_timestamp,
                    last_updated_at=fetch_timestamp,
                    data=item,
                    source_reference=str(item["id"]),
                    content_hash=content_hash,
                    schema_version="1.0.0",
                    normalization_version="1.0.0",
                    confidence=1.0,
                    provenance=provenance
                )
            )
        return records
