import asyncio
import logging
import os
import sys

# Setup logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Ensure backend root is in PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.agents.orchestrator import run_all_agents
from app.db.database import engine

async def poll_sources():
    # Poll interval (default 5 minutes = 300 seconds)
    interval_seconds = int(os.environ.get("POLL_INTERVAL_SECONDS", 300))
    logger.info(f"Starting background worker. Polling every {interval_seconds} seconds.")
    
    while True:
        try:
            logger.info("Triggering autonomous polling cycle...")
            await run_all_agents()
        except Exception as e:
            logger.error(f"Error during polling cycle: {e}")
            
        await asyncio.sleep(interval_seconds)

if __name__ == "__main__":
    try:
        asyncio.run(poll_sources())
    except KeyboardInterrupt:
        logger.info("Worker stopped.")
