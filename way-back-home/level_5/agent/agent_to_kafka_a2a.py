# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

import asyncio
import json
import logging
import uuid
from typing import Optional, Union, Any, List

from aiokafka import AIOKafkaConsumer, AIOKafkaProducer

from google.adk.agents.base_agent import BaseAgent
from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
from google.adk.auth.credential_service.in_memory_credential_service import InMemoryCredentialService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types as genai_types

logger = logging.getLogger(__name__)


class KafkaServerApp:
    """A Kafka-based A2A server that consumes requests and sends replies.
    
    Messages are JSON with structure:
      Request:  {"message_id": str, "reply_topic": str, "text": str}
      Response: {"message_id": str, "text": str}
    """

    def __init__(
        self,
        agent: BaseAgent,
        bootstrap_servers: str | List[str],
        request_topic: str = "a2a-formation-request",
        consumer_group_id: str = "a2a-agent-group",
    ):
        self.agent = agent
        self.bootstrap_servers = bootstrap_servers
        self.request_topic = request_topic
        self.consumer_group_id = consumer_group_id
        self._runner: Optional[Runner] = None

    async def _get_runner(self) -> Runner:
        if self._runner is None:
            self._runner = Runner(
                app_name=self.agent.name or "adk_agent",
                agent=self.agent,
                artifact_service=InMemoryArtifactService(),
                session_service=InMemorySessionService(),
                memory_service=InMemoryMemoryService(),
                credential_service=InMemoryCredentialService(),
            )
        return self._runner

    async def _handle_message(self, request: dict, producer: AIOKafkaProducer) -> None:
        """Process one incoming request message and send reply."""
        message_id = request.get("message_id", str(uuid.uuid4()))
        reply_topic = request.get("reply_topic", "a2a-reply-satellite-dashboard")
        text = request.get("text", "")

        logger.info(f"Processing request {message_id}: {text[:80]}")

        try:
            runner = await self._get_runner()
            session_service = runner.session_service
            app_name = runner.app_name

            # Create a session
            session = await session_service.create_session(
                app_name=app_name,
                user_id="kafka-user",
            )

            # Build the user message
            content = genai_types.Content(
                role="user",
                parts=[genai_types.Part(text=text)]
            )

            # Run the agent
            response_text = ""
            async for event in runner.run_async(
                user_id="kafka-user",
                session_id=session.id,
                new_message=content,
            ):
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, "text") and part.text:
                            response_text += part.text

            logger.info(f"Agent response for {message_id}: {response_text[:100]}")

            # Send reply
            reply = {
                "message_id": message_id,
                "text": response_text,
            }
            await producer.send_and_wait(reply_topic, json.dumps(reply).encode("utf-8"))
            logger.info(f"Reply sent to topic '{reply_topic}'")

        except Exception as e:
            logger.error(f"Error handling message {message_id}: {e}")
            # Still send an error reply so client doesn't time out
            error_reply = {"message_id": message_id, "text": f"Error: {e}", "error": True}
            try:
                await producer.send_and_wait(reply_topic, json.dumps(error_reply).encode("utf-8"))
            except Exception:
                pass

    async def run(self) -> None:
        """Start consuming requests and processing them."""
        logger.info(f"Starting Kafka Server on topic '{self.request_topic}'...")

        consumer = AIOKafkaConsumer(
            self.request_topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.consumer_group_id,
            auto_offset_reset="latest",
        )
        producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers)

        await consumer.start()
        await producer.start()
        logger.info("Kafka Server started. Listening for requests...")

        try:
            async for msg in consumer:
                try:
                    request = json.loads(msg.value.decode("utf-8"))
                    await self._handle_message(request, producer)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON in message: {e}")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
        finally:
            await consumer.stop()
            await producer.stop()


async def create_kafka_server(
    agent: BaseAgent,
    *,
    bootstrap_servers: str | List[str] = "localhost:9092",
    request_topic: str = "a2a-formation-request",
    consumer_group_id: str = "a2a-agent-group",
    **kwargs: Any,
) -> KafkaServerApp:
    """Convert an ADK agent to a Kafka A2A server application.

    Returns:
        A KafkaServerApp that can be run with .run()
    """
    adk_logger = logging.getLogger("google_adk")
    adk_logger.setLevel(logging.INFO)

    return KafkaServerApp(
        agent=agent,
        bootstrap_servers=bootstrap_servers,
        request_topic=request_topic,
        consumer_group_id=consumer_group_id,
    )
