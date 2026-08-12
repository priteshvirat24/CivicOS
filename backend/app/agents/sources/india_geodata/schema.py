from pydantic import BaseModel
from typing import List

class GeoData(BaseModel):
    common_name: str
    official_name: str
    capital: List[str]
    region: str
    population: int
    borders: List[str]
