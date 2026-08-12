from pydantic import BaseModel
from typing import List

class Station(BaseModel):
    name: str
    code: str
    zone: str
    state: str

class StationList(BaseModel):
    stations: List[Station]
