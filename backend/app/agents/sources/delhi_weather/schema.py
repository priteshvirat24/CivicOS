from pydantic import BaseModel

class WeatherCurrent(BaseModel):
    temperature: float
    windspeed: float
    winddirection: float
    time: str

class WeatherData(BaseModel):
    latitude: float
    longitude: float
    current_weather: WeatherCurrent
