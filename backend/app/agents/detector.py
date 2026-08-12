import hashlib
import json
from typing import Any, Dict, List
from app.models.canonical import CanonicalRecord, FieldChange

class ChangeDetector:
    def __init__(self, ignored_fields: List[str] = None):
        self.ignored_fields = ignored_fields or []

    def strip_ignored(self, data: Any) -> Any:
        if isinstance(data, dict):
            return {
                k: self.strip_ignored(v) 
                for k, v in data.items() 
                if k not in self.ignored_fields
            }
        elif isinstance(data, list):
            # Sort lists of dicts if possible to ensure deterministic ordering
            # For simplicity, if elements are dicts, we sort by a deterministic string rep
            cleaned_list = [self.strip_ignored(item) for item in data]
            try:
                cleaned_list.sort(key=lambda x: json.dumps(x, sort_keys=True))
            except TypeError:
                pass
            return cleaned_list
        return data

    def hash_payload(self, data: Any) -> str:
        """Deterministic hash ignoring whitespace and irrelevant fields."""
        cleaned = self.strip_ignored(data)
        dumped = json.dumps(cleaned, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(dumped.encode('utf-8')).hexdigest()

    def diff_records(self, old_record: CanonicalRecord, new_record: CanonicalRecord) -> List[FieldChange]:
        """Deep diffs the 'data' field of two CanonicalRecords."""
        old_data = self.strip_ignored(old_record.data)
        new_data = self.strip_ignored(new_record.data)
        
        changes = []
        self._deep_diff("", old_data, new_data, changes)
        return changes

    def _deep_diff(self, path: str, old: Any, new: Any, changes: List[FieldChange]):
        if type(old) != type(new):
            changes.append(FieldChange(
                affected_field=path,
                old_value=old,
                new_value=new
            ))
            return
            
        if isinstance(old, dict):
            all_keys = set(old.keys()).union(set(new.keys()))
            for k in all_keys:
                new_path = f"{path}.{k}" if path else k
                if k not in old:
                    changes.append(FieldChange(affected_field=new_path, old_value=None, new_value=new[k]))
                elif k not in new:
                    changes.append(FieldChange(affected_field=new_path, old_value=old[k], new_value=None))
                else:
                    self._deep_diff(new_path, old[k], new[k], changes)
        elif isinstance(old, list):
            # If lists are exactly equal
            if old == new:
                return
            # For arrays, we do a simplistic diff: entire array replaced if different
            changes.append(FieldChange(affected_field=path, old_value=old, new_value=new))
        else:
            if old != new:
                changes.append(FieldChange(affected_field=path, old_value=old, new_value=new))
