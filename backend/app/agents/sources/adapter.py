from abc import ABC, abstractmethod
from typing import Any, Dict, List
import hashlib
import json
from pydantic import BaseModel
from datetime import datetime
from app.models.canonical import CanonicalRecord, ProvenanceMetadata

class SourceAdapter(ABC):
    @abstractmethod
    async def fetch(self) -> Any:
        pass

    @abstractmethod
    def parse(self, raw_data: Any) -> Any:
        pass

    @abstractmethod
    def normalize(self, parsed_data: Any) -> Dict[str, Any]:
        pass

    def fingerprint(self, normalized_data: Dict[str, Any]) -> str:
        # Deterministic JSON dump
        dumped = json.dumps(normalized_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(dumped.encode('utf-8')).hexdigest()

    @abstractmethod
    def validate(self, normalized_data: Dict[str, Any]) -> BaseModel:
        pass

    @abstractmethod
    def get_metadata(self) -> Dict[str, str]:
        pass

    def get_ignored_fields(self) -> List[str]:
        """Returns a list of keys to strip during change detection (e.g. fetch timestamps)."""
        return []

    @abstractmethod
    def to_canonical(self, raw_data: Any, parsed_data: Any, normalized_data: Dict[str, Any], validated_model: BaseModel, fetch_timestamp: datetime) -> List[CanonicalRecord]:
        """Converts the source-specific data into a strict CanonicalRecord envelope with provenance."""
        pass
