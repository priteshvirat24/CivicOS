from pydantic import BaseModel
from typing import List

class PopulationRecord(BaseModel):
    country: str
    year: str
    population: int

class PopulationData(BaseModel):
    records: List[PopulationRecord]
