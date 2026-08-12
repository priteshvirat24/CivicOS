import json
import os
from typing import Any, Dict
from pydantic import BaseModel
from app.agents.sources.adapter import SourceAdapter
from app.models.canonical import CanonicalRecord, ProvenanceMetadata
from typing import List
from datetime import datetime
import hashlib
from .schema import StationList

class RailwaysAdapter(SourceAdapter):
    def __init__(self, use_fixture: bool = True):
        self.use_fixture = use_fixture

    async def fetch(self) -> Any:
        if self.use_fixture:
            with open(os.path.join(os.path.dirname(__file__), 'fixture.json'), 'r') as f:
                return json.load(f)
        raise NotImplementedError("Live fetch not enabled")

    def parse(self, raw_data: Any) -> Any:
        # datameet geojson FeatureCollection
        parsed = []
        for feature in raw_data.get("features", []):
            props = feature.get("properties", {})
            code = str(props.get("code", "")).strip()
            if not code:
                continue
            parsed.append({
                "name": str(props.get("name", "")),
                "code": code,
                "zone": str(props.get("zone", "")),
                "state": str(props.get("state", ""))
            })
        return parsed

    def normalize(self, parsed_data: Any) -> Dict[str, Any]:
        return {"stations": parsed_data}

    def validate(self, normalized_data: Dict[str, Any]) -> BaseModel:
        return StationList(**normalized_data)

    def get_metadata(self) -> Dict[str, str]:
        return {
            "source_id": "railways",
            "url": "https://raw.githubusercontent.com/datameet/railways/master/stations.json",
            "name": "Indian Railway Stations"
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
        
        for item in validated_model.stations:
            data_dict = item.model_dump()
            content_hash = hashlib.sha256(json.dumps(data_dict, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()
            
            record = CanonicalRecord(
                source_id=meta["source_id"],
                dataset_id=meta["source_id"] + "_dataset",
                observed_at=fetch_timestamp,
                effective_at=fetch_timestamp,
                data=data_dict,
                source_reference=item.code,
                content_hash=content_hash,
                schema_version="1.0.0",
                normalization_version="1.0.0",
                confidence=1.0,
                provenance=provenance
            )
            records.append(record)
            
        return records
