from pydantic import BaseModel
from typing import Dict, Optional

class AQIReadings(BaseModel):
    pm10: Optional[float]
    pm2_5: Optional[float]
    carbon_monoxide: Optional[float]
    nitrogen_dioxide: Optional[float]
    sulphur_dioxide: Optional[float]
    ozone: Optional[float]

class AirQualityData(BaseModel):
    latitude: float
    longitude: float
    time: str
    readings: AQIReadings
