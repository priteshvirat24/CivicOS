import logging
import importlib
from typing import Dict, List, Optional
from app.agents.sources.adapter import SourceAdapter

logger = logging.getLogger(__name__)

class SourceRegistry:
    def __init__(self):
        self.adapters: Dict[str, SourceAdapter] = {}
        self._load_adapters()

    def _load_adapters(self):
        """Load adapters explicitly for the MVP."""
        from app.agents.sources.covid19.adapter import Covid19Adapter
        from app.agents.sources.railways.adapter import RailwaysAdapter
        from app.agents.sources.delhi_weather.adapter import DelhiWeatherAdapter
        from app.agents.sources.india_population.adapter import IndiaPopulationAdapter
        from app.agents.sources.india_gdp.adapter import IndiaGDPAdapter
        from app.agents.sources.delhi_openaq.adapter import DelhiOpenAQAdapter
        from app.agents.sources.mumbai_sunrise.adapter import MumbaiSunriseAdapter
        from app.agents.sources.india_geodata.adapter import IndiaGeoDataAdapter
        from app.agents.sources.demo import DemoAdapter

        adapters = [
            Covid19Adapter(),
            RailwaysAdapter(),
            DelhiWeatherAdapter(),
            IndiaPopulationAdapter(),
            IndiaGDPAdapter(),
            DelhiOpenAQAdapter(),
            MumbaiSunriseAdapter(),
            IndiaGeoDataAdapter(),
            DemoAdapter()
        ]

        for adapter in adapters:
            meta = adapter.get_metadata()
            source_id = meta["source_id"]
            self.adapters[source_id] = adapter
            logger.info(f"Loaded adapter for {source_id}: {meta['name']}")

    def get_adapter(self, source_id: str) -> Optional[SourceAdapter]:
        return self.adapters.get(source_id)

    def get_all_adapters(self) -> List[SourceAdapter]:
        return list(self.adapters.values())

# Global registry instance
registry = SourceRegistry()
