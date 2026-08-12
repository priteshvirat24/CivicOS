import pytest
import sys
import os
from datetime import datetime

# Ensure backend app is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.agents.registry import registry
from app.models.canonical import CanonicalRecord

@pytest.mark.asyncio
async def test_all_sources():
    adapters = registry.get_all_adapters()
    assert len(adapters) == 9, "Expected exactly 9 adapters to be registered"
    
    fetch_timestamp = datetime.utcnow()

    for adapter in adapters:
        meta = adapter.get_metadata()
        print(f"\\n--- Testing Adapter: {meta['name']} ({meta['source_id']}) ---")
        
        # 1. Fetch data
        raw_data = await adapter.fetch()
        assert raw_data is not None, f"Failed to fetch data for {meta['source_id']}"
        
        # 2. Parse data
        parsed_data = adapter.parse(raw_data)
        assert parsed_data is not None, f"Failed to parse data for {meta['source_id']}"
        
        # 3. Normalize data
        normalized_data = adapter.normalize(parsed_data)
        assert isinstance(normalized_data, dict), f"Normalized data must be a dict for {meta['source_id']}"
        
        # 4. Validate against domain schema
        validated_model = adapter.validate(normalized_data)
        assert validated_model is not None, f"Validation returned None for {meta['source_id']}"
        
        # 5. Convert to Canonical Records (The Provenance Core)
        canonical_records = adapter.to_canonical(
            raw_data=raw_data,
            parsed_data=parsed_data,
            normalized_data=normalized_data,
            validated_model=validated_model,
            fetch_timestamp=fetch_timestamp
        )
        
        assert len(canonical_records) > 0, f"No canonical records generated for {meta['source_id']}"
        
        # 6. Strict Validations on Canonical Record
        for record in canonical_records:
            assert isinstance(record, CanonicalRecord)
            assert record.source_id == meta['source_id']
            assert record.source_reference != "", "Source reference must be populated"
            assert record.provenance is not None
            assert record.provenance.fetch_url == meta['url']
            assert record.provenance.raw_payload_hash != ""
            assert record.content_hash != ""
            # Pydantic will have automatically run @field_validators for duplicate/malformed checks internally!
            
        print(f"✅ Successfully created {len(canonical_records)} canonical records with strict provenance for {meta['source_id']}.")
        print(f"Sample Provenance: \\n{canonical_records[0].provenance.model_dump_json(indent=2)}")
