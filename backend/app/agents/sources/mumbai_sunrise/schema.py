from pydantic import BaseModel

class SunTimingData(BaseModel):
    sunrise: str
    sunset: str
    solar_noon: str
    day_length: int
    date: str
