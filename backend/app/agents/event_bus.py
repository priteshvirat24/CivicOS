import asyncio
import logging
from typing import Any, Callable, Coroutine, Dict, List, Type
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

# Base Event
class BaseEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
# Specific Events
class SourceChanged(BaseEvent):
    source_id: str
    old_hash: str | None
    new_hash: str
    agent_id: str

class DataPRCreated(BaseEvent):
    pr_id: str
    source_id: str
    agent_id: str

class VerificationStarted(BaseEvent):
    pr_id: str
    verifier_agent_id: str

class VerificationPassed(BaseEvent):
    pr_id: str
    verification_id: str

class VerificationFailed(BaseEvent):
    pr_id: str
    verification_id: str
    failed_checks: List[str]

class DataPRMerged(BaseEvent):
    pr_id: str
    new_version: int

class DatasetUpdated(BaseEvent):
    version: int

class DeploymentTriggered(BaseEvent):
    version: int

EventHandler = Callable[[BaseEvent], Coroutine[Any, Any, None]]

class EventBus:
    def __init__(self):
        self.subscribers: Dict[Type[BaseEvent], List[EventHandler]] = {}
        self.queue = None
        self._worker_task = None
        self.running = False

    def subscribe(self, event_type: Type[BaseEvent], handler: EventHandler):
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
        self.subscribers[event_type].append(handler)
        logger.info(f"Subscribed handler {handler.__name__} to {event_type.__name__}")

    async def publish(self, event: BaseEvent):
        logger.info(f"Publishing event: {type(event).__name__} ({event.event_id})")
        if self.queue:
            await self.queue.put(event)

    async def _worker(self):
        while self.running and self.queue:
            event = await self.queue.get()
            event_type = type(event)
            handlers = self.subscribers.get(event_type, [])
            
            for handler in handlers:
                try:
                    await handler(event)
                except Exception as e:
                    logger.error(f"Error in handler {handler.__name__} for event {event_type.__name__}: {e}")
            
            self.queue.task_done()

    def start(self):
        if not self.running:
            self.queue = asyncio.Queue()
            self.running = True
            self._worker_task = asyncio.create_task(self._worker())
            logger.info("EventBus started")

    async def stop(self):
        self.running = False
        if self._worker_task:
            self._worker_task.cancel()
            try:
                await self._worker_task
            except asyncio.CancelledError:
                pass
        logger.info("EventBus stopped")

# Global Event Bus instance
bus = EventBus()
