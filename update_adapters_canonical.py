import os

base_dir = "/Users/priteshhome/CivicOS/backend/app/agents/sources"

adapters_config = {
    "covid19": {
        "iterator": "validated_model.states",
        "reference_key": "item.state_code",
        "data_dump": "item.model_dump()"
    },
    "railways": {
        "iterator": "validated_model.stations",
        "reference_key": "item.code",
        "data_dump": "item.model_dump()"
    },
    "delhi_weather": {
        "iterator": "[validated_model]",
        "reference_key": "f'{item.latitude}_{item.longitude}'",
        "data_dump": "item.model_dump()"
    },
    "india_population": {
        "iterator": "validated_model.records",
        "reference_key": "f'{item.country}_{item.year}'",
        "data_dump": "item.model_dump()"
    },
    "india_gdp": {
        "iterator": "validated_model.records",
        "reference_key": "f'{item.country}_{item.year}'",
        "data_dump": "item.model_dump()"
    },
    "delhi_openaq": {
        "iterator": "[validated_model]",
        "reference_key": "f'{item.latitude}_{item.longitude}_{item.time}'",
        "data_dump": "item.model_dump()"
    },
    "mumbai_sunrise": {
        "iterator": "[validated_model]",
        "reference_key": "item.date",
        "data_dump": "item.model_dump()"
    },
    "india_geodata": {
        "iterator": "[validated_model]",
        "reference_key": "item.common_name",
        "data_dump": "item.model_dump()"
    }
}

for name, config in adapters_config.items():
    adapter_path = os.path.join(base_dir, name, "adapter.py")
    with open(adapter_path, "r") as f:
        content = f.read()

    if "from app.models.canonical import" not in content:
        replacement = """from app.agents.sources.adapter import SourceAdapter
from app.models.canonical import CanonicalRecord, ProvenanceMetadata
from typing import List
from datetime import datetime
import hashlib"""
        content = content.replace("from app.agents.sources.adapter import SourceAdapter", replacement)

    if "def to_canonical" not in content:
        method_str = f"""
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
        
        for item in {config['iterator']}:
            data_dict = {config['data_dump']}
            content_hash = hashlib.sha256(json.dumps(data_dict, sort_keys=True, separators=(',', ':')).encode('utf-8')).hexdigest()
            
            record = CanonicalRecord(
                source_id=meta["source_id"],
                dataset_id=meta["source_id"] + "_dataset",
                observed_at=fetch_timestamp,
                effective_at=fetch_timestamp,
                data=data_dict,
                source_reference={config['reference_key']},
                content_hash=content_hash,
                schema_version="1.0.0",
                normalization_version="1.0.0",
                confidence=1.0,
                provenance=provenance
            )
            records.append(record)
            
        return records
"""
        content += method_str

    with open(adapter_path, "w") as f:
        f.write(content)

print("Updated all adapters with to_canonical method.")
