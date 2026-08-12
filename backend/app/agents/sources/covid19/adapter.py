import json
import os
from typing import Any, Dict
from pydantic import BaseModel
from app.agents.sources.adapter import SourceAdapter
from app.models.canonical import CanonicalRecord, ProvenanceMetadata
from typing import List
from datetime import datetime
import hashlib
from .schema import CovidList

class Covid19Adapter(SourceAdapter):
    def __init__(self, use_fixture: bool = True):
        self.use_fixture = use_fixture

    async def fetch(self) -> Any:
        if self.use_fixture:
            fixture_path = os.path.join(os.path.dirname(__file__), 'fixture.json')
            with open(fixture_path, 'r') as f:
                return json.load(f)
        raise NotImplementedError("Live fetch not enabled")

    def parse(self, raw_data: Any) -> Any:
        parsed = []
        for state_code, data in raw_data.items():
            if state_code == "TT": # Skip total country row
                continue
            total = data.get("total", {})
            meta = data.get("meta", {})
            parsed.append({
                "state_code": state_code,
                "confirmed": total.get("confirmed", 0),
                "recovered": total.get("recovered", 0),
                "deceased": total.get("deceased", 0),
                "tested": total.get("tested", 0),
                "last_updated": meta.get("last_updated", "")
            })
        return parsed

    def normalize(self, parsed_data: Any) -> Dict[str, Any]:
        return {"states": parsed_data}

    def validate(self, normalized_data: Dict[str, Any]) -> BaseModel:
        return CovidList(**normalized_data)

    def get_metadata(self) -> Dict[str, str]:
        return {
            "source_id": "covid19",
            "url": "https://data.covid19india.org/v4/min/data.min.json",
            "name": "COVID-19 India Stats"
        }

    def to_canonical(self, raw_data: Any, parsed_data: Any, normalized_data: Dict[str, Any], validated_model: BaseModel, fetch_timestamp: datetime) -> List[CanonicalRecord]:
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
        
        for item in validated_model.states:
            data_dict = item.model_dump()
            content_hash = hashlib.sha256(json.dumps(data_dict, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()
            
            record = CanonicalRecord(
                source_id=meta["source_id"],
                dataset_id=meta["source_id"] + "_dataset",
                observed_at=fetch_timestamp,
                effective_at=fetch_timestamp,
                data=data_dict,
                source_reference=item.state_code,
                content_hash=content_hash,
                schema_version="1.0.0",
                normalization_version="1.0.0",
                confidence=1.0,
                provenance=provenance
            )
            records.append(record)
            
        return records
