import os
import json
import urllib.request
import ssl

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

sources = {
    "covid19": "https://data.covid19india.org/v4/min/data.min.json",
    "railways": "https://raw.githubusercontent.com/datameet/railways/master/stations.json",
    "delhi_weather": "https://api.open-meteo.com/v1/forecast?latitude=28.61&longitude=77.23&current_weather=true",
    "india_population": "https://api.worldbank.org/v2/country/IN/indicator/SP.POP.TOTL?format=json",
    "india_gdp": "https://api.worldbank.org/v2/country/IN/indicator/NY.GDP.MKTP.CD?format=json",
    "delhi_openaq": "https://api.openaq.org/v2/latest?city=Delhi&country=IN",
    "mumbai_sunrise": "https://api.sunrise-sunset.org/json?lat=19.0760&lng=72.8777&formatted=0",
    "india_geodata": "https://restcountries.com/v3.1/name/india"
}

base_dir = "/Users/priteshhome/CivicOS/backend/app/agents/sources"

for name, url in sources.items():
    dir_path = os.path.join(base_dir, name)
    os.makedirs(dir_path, exist_ok=True)
    init_path = os.path.join(dir_path, "__init__.py")
    with open(init_path, "w") as f:
        pass
        
    print(f"Fetching {name} from {url}...")
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, context=ctx) as response:
            data = json.loads(response.read().decode())
            fixture_path = os.path.join(dir_path, "fixture.json")
            with open(fixture_path, "w") as f:
                json.dump(data, f, indent=2)
            print(f"Saved {fixture_path}")
    except Exception as e:
        print(f"Failed to fetch {name}: {e}")

# Create adapter interface
adapter_code = """from abc import ABC, abstractmethod
from typing import Any, Dict
import hashlib
import json
from pydantic import BaseModel

class SourceAdapter(ABC):
    @abstractmethod
    async def fetch(self) -> Any:
        pass

    @abstractmethod
    def parse(self, raw_data: Any) -> Any:
        pass

    @abstractmethod
    def normalize(self, parsed_data: Any) -> Dict[str, Any]:
        pass

    def fingerprint(self, normalized_data: Dict[str, Any]) -> str:
        # Deterministic JSON dump
        dumped = json.dumps(normalized_data, sort_keys=True, separators=(',', ':'))
        return hashlib.sha256(dumped.encode('utf-8')).hexdigest()

    @abstractmethod
    def validate(self, normalized_data: Dict[str, Any]) -> BaseModel:
        pass

    @abstractmethod
    def get_metadata(self) -> Dict[str, str]:
        pass
"""
with open(os.path.join(base_dir, "adapter.py"), "w") as f:
    f.write(adapter_code)

with open(os.path.join(base_dir, "__init__.py"), "w") as f:
    pass

print("Done setting up source directories and fixtures.")
