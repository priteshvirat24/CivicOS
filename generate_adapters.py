import os

base_dir = "/Users/priteshhome/CivicOS/backend/app/agents/sources"

adapters_config = {
    "covid19": {
        "url": "https://data.covid19india.org/v4/min/data.min.json",
        "name": "COVID-19 India Stats",
        "schema_code": '''from pydantic import BaseModel
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
''',
        "adapter_code": '''import json
import os
from typing import Any, Dict
from pydantic import BaseModel
from app.agents.sources.adapter import SourceAdapter
from .schema import CovidList

class Covid19Adapter(SourceAdapter):
    def __init__(self, use_fixture: bool = True):
        self.use_fixture = use_fixture

    async def fetch(self) -> Any:
        if self.use_fixture:
            fixture_path = os.path.join(os.path.dirname(__file__), 'fixture.json')
            with open(fixture_path, 'r') as f:
                return json.load(f)
        raise NotImplementedError("Live fetch not enabled")

    def parse(self, raw_data: Any) -> Any:
        parsed = []
        for state_code, data in raw_data.items():
            if state_code == "TT": # Skip total country row
                continue
            total = data.get("total", {})
            meta = data.get("meta", {})
            parsed.append({
                "state_code": state_code,
                "confirmed": total.get("confirmed", 0),
                "recovered": total.get("recovered", 0),
                "deceased": total.get("deceased", 0),
                "tested": total.get("tested", 0),
                "last_updated": meta.get("last_updated", "")
            })
        return parsed

    def normalize(self, parsed_data: Any) -> Dict[str, Any]:
        return {"states": parsed_data}

    def validate(self, normalized_data: Dict[str, Any]) -> BaseModel:
        return CovidList(**normalized_data)

    def get_metadata(self) -> Dict[str, str]:
        return {
            "source_id": "covid19",
            "url": "https://data.covid19india.org/v4/min/data.min.json",
            "name": "COVID-19 India Stats"
        }
'''
    },
    "railways": {
        "url": "https://raw.githubusercontent.com/datameet/railways/master/stations.json",
        "name": "Indian Railway Stations",
        "schema_code": '''from pydantic import BaseModel
from typing import List

class Station(BaseModel):
    name: str
    code: str
    zone: str
    state: str

class StationList(BaseModel):
    stations: List[Station]
''',
        "adapter_code": '''import json
import os
from typing import Any, Dict
from pydantic import BaseModel
from app.agents.sources.adapter import SourceAdapter
from .schema import StationList

class RailwaysAdapter(SourceAdapter):
    def __init__(self, use_fixture: bool = True):
        self.use_fixture = use_fixture

    async def fetch(self) -> Any:
        if self.use_fixture:
            with open(os.path.join(os.path.dirname(__file__), 'fixture.json'), 'r') as f:
                return json.load(f)
        raise NotImplementedError("Live fetch not enabled")

    def parse(self, raw_data: Any) -> Any:
        # datameet geojson FeatureCollection
        parsed = []
        for feature in raw_data.get("features", []):
            props = feature.get("properties", {})
            code = str(props.get("code", "")).strip()
            if not code:
                continue
            parsed.append({
                "name": str(props.get("name", "")),
                "code": code,
                "zone": str(props.get("zone", "")),
                "state": str(props.get("state", ""))
            })
        return parsed

    def normalize(self, parsed_data: Any) -> Dict[str, Any]:
        return {"stations": parsed_data}

    def validate(self, normalized_data: Dict[str, Any]) -> BaseModel:
        return StationList(**normalized_data)

    def get_metadata(self) -> Dict[str, str]:
        return {
            "source_id": "railways",
            "url": "https://raw.githubusercontent.com/datameet/railways/master/stations.json",
            "name": "Indian Railway Stations"
        }
'''
    },
    "delhi_weather": {
        "schema_code": '''from pydantic import BaseModel

class WeatherCurrent(BaseModel):
    temperature: float
    windspeed: float
    winddirection: float
    time: str

class WeatherData(BaseModel):
    latitude: float
    longitude: float
    current_weather: WeatherCurrent
''',
        "adapter_code": '''import json
import os
from typing import Any, Dict
from pydantic import BaseModel
from app.agents.sources.adapter import SourceAdapter
from .schema import WeatherData

class DelhiWeatherAdapter(SourceAdapter):
    def __init__(self, use_fixture: bool = True):
        self.use_fixture = use_fixture

    async def fetch(self) -> Any:
        if self.use_fixture:
            with open(os.path.join(os.path.dirname(__file__), 'fixture.json'), 'r') as f:
                return json.load(f)
        raise NotImplementedError("Live fetch not enabled")

    def parse(self, raw_data: Any) -> Any:
        return {
            "latitude": float(raw_data.get("latitude", 0)),
            "longitude": float(raw_data.get("longitude", 0)),
            "current_weather": raw_data.get("current_weather", {})
        }

    def normalize(self, parsed_data: Any) -> Dict[str, Any]:
        return parsed_data

    def validate(self, normalized_data: Dict[str, Any]) -> BaseModel:
        return WeatherData(**normalized_data)

    def get_metadata(self) -> Dict[str, str]:
        return {
            "source_id": "delhi_weather",
            "url": "https://api.open-meteo.com/v1/forecast?latitude=28.61&longitude=77.23&current_weather=true",
            "name": "New Delhi Weather"
        }
'''
    },
    "india_population": {
        "schema_code": '''from pydantic import BaseModel
from typing import List

class PopulationRecord(BaseModel):
    country: str
    year: str
    population: int

class PopulationData(BaseModel):
    records: List[PopulationRecord]
''',
        "adapter_code": '''import json
import os
from typing import Any, Dict
from pydantic import BaseModel
from app.agents.sources.adapter import SourceAdapter
from .schema import PopulationData

class IndiaPopulationAdapter(SourceAdapter):
    def __init__(self, use_fixture: bool = True):
        self.use_fixture = use_fixture

    async def fetch(self) -> Any:
        if self.use_fixture:
            with open(os.path.join(os.path.dirname(__file__), 'fixture.json'), 'r') as f:
                return json.load(f)
        raise NotImplementedError("Live fetch not enabled")

    def parse(self, raw_data: Any) -> Any:
        parsed = []
        if len(raw_data) > 1:
            for item in raw_data[1]:
                if item.get("value") is not None:
                    parsed.append({
                        "country": item["country"]["value"],
                        "year": item["date"],
                        "population": int(item["value"])
                    })
        return parsed

    def normalize(self, parsed_data: Any) -> Dict[str, Any]:
        return {"records": parsed_data}

    def validate(self, normalized_data: Dict[str, Any]) -> BaseModel:
        return PopulationData(**normalized_data)

    def get_metadata(self) -> Dict[str, str]:
        return {
            "source_id": "india_population",
            "url": "https://api.worldbank.org/v2/country/IN/indicator/SP.POP.TOTL?format=json",
            "name": "India Population Stats"
        }
'''
    },
    "india_gdp": {
        "schema_code": '''from pydantic import BaseModel
from typing import List

class GDPRecord(BaseModel):
    country: str
    year: str
    gdp_usd: float

class GDPData(BaseModel):
    records: List[GDPRecord]
''',
        "adapter_code": '''import json
import os
from typing import Any, Dict
from pydantic import BaseModel
from app.agents.sources.adapter import SourceAdapter
from .schema import GDPData

class IndiaGDPAdapter(SourceAdapter):
    def __init__(self, use_fixture: bool = True):
        self.use_fixture = use_fixture

    async def fetch(self) -> Any:
        if self.use_fixture:
            with open(os.path.join(os.path.dirname(__file__), 'fixture.json'), 'r') as f:
                return json.load(f)
        raise NotImplementedError("Live fetch not enabled")

    def parse(self, raw_data: Any) -> Any:
        parsed = []
        if len(raw_data) > 1:
            for item in raw_data[1]:
                if item.get("value") is not None:
                    parsed.append({
                        "country": item["country"]["value"],
                        "year": item["date"],
                        "gdp_usd": float(item["value"])
                    })
        return parsed

    def normalize(self, parsed_data: Any) -> Dict[str, Any]:
        return {"records": parsed_data}

    def validate(self, normalized_data: Dict[str, Any]) -> BaseModel:
        return GDPData(**normalized_data)

    def get_metadata(self) -> Dict[str, str]:
        return {
            "source_id": "india_gdp",
            "url": "https://api.worldbank.org/v2/country/IN/indicator/NY.GDP.MKTP.CD?format=json",
            "name": "India GDP Stats"
        }
'''
    },
    "delhi_openaq": {
        "schema_code": '''from pydantic import BaseModel
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
''',
        "adapter_code": '''import json
import os
from typing import Any, Dict
from pydantic import BaseModel
from app.agents.sources.adapter import SourceAdapter
from .schema import AirQualityData

class DelhiOpenAQAdapter(SourceAdapter):
    def __init__(self, use_fixture: bool = True):
        self.use_fixture = use_fixture

    async def fetch(self) -> Any:
        if self.use_fixture:
            with open(os.path.join(os.path.dirname(__file__), 'fixture.json'), 'r') as f:
                return json.load(f)
        raise NotImplementedError("Live fetch not enabled")

    def parse(self, raw_data: Any) -> Any:
        current = raw_data.get("current", {})
        return {
            "latitude": float(raw_data.get("latitude", 0)),
            "longitude": float(raw_data.get("longitude", 0)),
            "time": current.get("time", ""),
            "readings": {
                "pm10": current.get("pm10", 0),
                "pm2_5": current.get("pm2_5", 0),
                "carbon_monoxide": current.get("carbon_monoxide", 0),
                "nitrogen_dioxide": current.get("nitrogen_dioxide", 0),
                "sulphur_dioxide": current.get("sulphur_dioxide", 0),
                "ozone": current.get("ozone", 0)
            }
        }

    def normalize(self, parsed_data: Any) -> Dict[str, Any]:
        return parsed_data

    def validate(self, normalized_data: Dict[str, Any]) -> BaseModel:
        return AirQualityData(**normalized_data)

    def get_metadata(self) -> Dict[str, str]:
        return {
            "source_id": "delhi_openaq",
            "url": "https://air-quality-api.open-meteo.com/v1/air-quality",
            "name": "Delhi Air Quality (Open-Meteo)"
        }
'''
    },
    "mumbai_sunrise": {
        "schema_code": '''from pydantic import BaseModel

class SunTimingData(BaseModel):
    sunrise: str
    sunset: str
    solar_noon: str
    day_length: int
    date: str
''',
        "adapter_code": '''import json
import os
from typing import Any, Dict
from pydantic import BaseModel
from app.agents.sources.adapter import SourceAdapter
from .schema import SunTimingData

class MumbaiSunriseAdapter(SourceAdapter):
    def __init__(self, use_fixture: bool = True):
        self.use_fixture = use_fixture

    async def fetch(self) -> Any:
        if self.use_fixture:
            with open(os.path.join(os.path.dirname(__file__), 'fixture.json'), 'r') as f:
                return json.load(f)
        raise NotImplementedError("Live fetch not enabled")

    def parse(self, raw_data: Any) -> Any:
        results = raw_data.get("results", {})
        return {
            "sunrise": str(results.get("sunrise", "")),
            "sunset": str(results.get("sunset", "")),
            "solar_noon": str(results.get("solar_noon", "")),
            "day_length": int(results.get("day_length", 0)),
            "date": "2026-08-12" # mocked date for testing since API might not include date explicitly
        }

    def normalize(self, parsed_data: Any) -> Dict[str, Any]:
        return parsed_data

    def validate(self, normalized_data: Dict[str, Any]) -> BaseModel:
        return SunTimingData(**normalized_data)

    def get_metadata(self) -> Dict[str, str]:
        return {
            "source_id": "mumbai_sunrise",
            "url": "https://api.sunrise-sunset.org/json",
            "name": "Mumbai Sun Timings"
        }
'''
    },
    "india_geodata": {
        "schema_code": '''from pydantic import BaseModel
from typing import List

class GeoData(BaseModel):
    common_name: str
    official_name: str
    capital: List[str]
    region: str
    population: int
    borders: List[str]
''',
        "adapter_code": '''import json
import os
from typing import Any, Dict
from pydantic import BaseModel
from app.agents.sources.adapter import SourceAdapter
from .schema import GeoData

class IndiaGeoDataAdapter(SourceAdapter):
    def __init__(self, use_fixture: bool = True):
        self.use_fixture = use_fixture

    async def fetch(self) -> Any:
        if self.use_fixture:
            with open(os.path.join(os.path.dirname(__file__), 'fixture.json'), 'r') as f:
                return json.load(f)
        raise NotImplementedError("Live fetch not enabled")

    def parse(self, raw_data: Any) -> Any:
        if not raw_data:
            return {}
        data = raw_data[0] # List of 1 element
        return {
            "common_name": data.get("name", {}).get("common", ""),
            "official_name": data.get("name", {}).get("official", ""),
            "capital": data.get("capital", []),
            "region": data.get("region", ""),
            "population": int(data.get("population", 0)),
            "borders": data.get("borders", [])
        }

    def normalize(self, parsed_data: Any) -> Dict[str, Any]:
        return parsed_data

    def validate(self, normalized_data: Dict[str, Any]) -> BaseModel:
        return GeoData(**normalized_data)

    def get_metadata(self) -> Dict[str, str]:
        return {
            "source_id": "india_geodata",
            "url": "https://restcountries.com/v3.1/name/india",
            "name": "India Geo Data"
        }
'''
    }
}

for name, config in adapters_config.items():
    dir_path = os.path.join(base_dir, name)
    with open(os.path.join(dir_path, "schema.py"), "w") as f:
        f.write(config["schema_code"])
    with open(os.path.join(dir_path, "adapter.py"), "w") as f:
        f.write(config["adapter_code"])

print("Adapters generated!")
