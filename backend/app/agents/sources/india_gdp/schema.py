from pydantic import BaseModel
from typing import List

class GDPRecord(BaseModel):
    country: str
    year: str
    gdp_usd: float

class GDPData(BaseModel):
    records: List[GDPRecord]
