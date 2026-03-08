"""
Kafka A2A Bridge — self-contained pattern (no public a2a.server.apps.kafka needed)

IMPORTANT: a2a.server.apps.kafka does NOT exist in PyPI.
Use aiokafka directly as shown here.

Message format:
  Request:  {"message_id": str, "reply_topic": str, "text": str}
  Response: {"message_id": str, "text": str}
"""
import asyncio
import json
import uuid
import logging
from typing import Optional

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from google.adk.agents.base_agent import BaseAgent
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types as genai_types

logger = logging.getLogger(__name__)


# ─── SERVER (Formation Agent side) ───────────────────────────────────────────

class KafkaServerApp:
    """Wraps an ADK agent as a Kafka consumer that processes text requests."""

    def __init__(self, agent: BaseAgent, bootstrap_servers: str,
                 request_topic: str, consumer_group_id: str = "adk-agent-group"):
        self.agent = agent
        self.bootstrap_servers = bootstrap_servers
        self.request_topic = request_topic
        self.consumer_group_id = consumer_group_id
        self._runner: Optional[Runner] = None

    async def _get_runner(self) -> Runner:
        if not self._runner:
            self._runner = Runner(
                app_name=self.agent.name,
                agent=self.agent,
                artifact_service=InMemoryArtifactService(),
                session_service=InMemorySessionService(),
                memory_service=InMemoryMemoryService(),
            )
        return self._runner

    async def _process(self, request: dict, producer: AIOKafkaProducer) -> None:
        msg_id = request.get("message_id", str(uuid.uuid4()))
        reply_topic = request.get("reply_topic")
        text = request.get("text", "")

        runner = await self._get_runner()
        session = await runner.session_service.create_session(
            app_name=runner.app_name, user_id="kafka-user")

        response_text = ""
        async for event in runner.run_async(
            user_id="kafka-user",
            session_id=session.id,
            new_message=genai_types.Content(
                role="user", parts=[genai_types.Part(text=text)]
            ),
        ):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    if hasattr(part, "text") and part.text:
                        response_text += part.text

        reply = {"message_id": msg_id, "text": response_text}
        await producer.send_and_wait(reply_topic, json.dumps(reply).encode())

    async def run(self) -> None:
        consumer = AIOKafkaConsumer(
            self.request_topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.consumer_group_id,
            auto_offset_reset="latest",
        )
        producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers)
        await consumer.start()
        await producer.start()
        logger.info(f"Kafka agent listening on '{self.request_topic}'")

        try:
            async for msg in consumer:
                request = json.loads(msg.value.decode())
                await self._process(request, producer)
        finally:
            await consumer.stop()
            await producer.stop()


async def create_kafka_server(agent: BaseAgent, *, bootstrap_servers: str,
                               request_topic: str, **kwargs) -> KafkaServerApp:
    return KafkaServerApp(agent, bootstrap_servers, request_topic)


# ─── CLIENT (Satellite Dashboard side) ───────────────────────────────────────

class KafkaA2AClient:
    """Send requests to a Kafka-based A2A agent and await replies."""

    def __init__(self, bootstrap_servers: str, request_topic: str, reply_topic: str):
        self.bootstrap_servers = bootstrap_servers
        self.request_topic = request_topic
        self.reply_topic = reply_topic
        self.pending: dict[str, asyncio.Future] = {}
        self._producer: Optional[AIOKafkaProducer] = None
        self._consumer_task: Optional[asyncio.Task] = None

    async def start(self):
        self._producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers)
        await self._producer.start()
        self._consumer_task = asyncio.create_task(self._consume_replies())

    async def stop(self):
        if self._consumer_task:
            self._consumer_task.cancel()
        if self._producer:
            await self._producer.stop()

    async def _consume_replies(self):
        consumer = AIOKafkaConsumer(
            self.reply_topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id="client-reply-group",
            auto_offset_reset="latest",
        )
        await consumer.start()
        try:
            async for msg in consumer:
                reply = json.loads(msg.value.decode())
                future = self.pending.pop(reply.get("message_id"), None)
                if future and not future.done():
                    future.set_result(reply)
        finally:
            await consumer.stop()

    async def send(self, text: str, timeout: float = 120.0) -> dict:
        """Send a text request and wait for the agent's reply."""
        msg_id = str(uuid.uuid4())
        loop = asyncio.get_event_loop()
        future = loop.create_future()
        self.pending[msg_id] = future  # register BEFORE sending (no race condition)

        message = {
            "message_id": msg_id,
            "reply_topic": self.reply_topic,
            "text": text,
        }
        await self._producer.send_and_wait(
            self.request_topic, json.dumps(message).encode()
        )
        return await asyncio.wait_for(future, timeout=timeout)


# ─── USAGE ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # SERVER side (formation agent)
    from my_agent import root_agent  # your ADK agent

    async def run_server():
        server = await create_kafka_server(
            root_agent,
            bootstrap_servers="localhost:9092",
            request_topic="a2a-formation-request",
        )
        await server.run()

    # CLIENT side (satellite dashboard)
    async def run_client_example():
        client = KafkaA2AClient(
            bootstrap_servers="localhost:9092",
            request_topic="a2a-formation-request",
            reply_topic="a2a-reply-satellite",
        )
        await client.start()
        reply = await client.send("Create a CIRCLE formation for 15 pods")
        print("Agent replied:", reply["text"])
        await client.stop()

    asyncio.run(run_server())
