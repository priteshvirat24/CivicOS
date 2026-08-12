from pydantic import BaseModel
from typing import List

class CovidStateData(BaseModel):
    state_code: str
    confirmed: int
    recovered: int
    deceased: int
    tested: int
    last_updated: str

class CovidList(BaseModel):
    states: List[CovidStateData]
