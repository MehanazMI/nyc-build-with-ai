import asyncio
import json
import random
import logging
import os
import uuid
from dotenv import load_dotenv

# Load env from project root
load_dotenv()

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from pydantic import BaseModel
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer


# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("satellite_dashboard")
logger.setLevel(logging.INFO)

from contextlib import asynccontextmanager

# Global state
PODS = []
TARGET_PODS = []
FORMATION = "FREEFORM"
kafka_producer: AIOKafkaProducer = None
pending_replies: dict = {}  # message_id -> asyncio.Future


def init_pods():
    global PODS, TARGET_PODS
    PODS = [{"id": i, "x": random.randint(50, 850), "y": random.randint(100, 600)} for i in range(15)]
    TARGET_PODS = [p.copy() for p in PODS]


init_pods()


BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
REQUEST_TOPIC = "a2a-formation-request"
REPLY_TOPIC = "a2a-reply-satellite-dashboard"


async def reply_consumer_task():
    """Background task that listens for agent replies on the reply topic."""
    consumer = AIOKafkaConsumer(
        REPLY_TOPIC,
        bootstrap_servers=BOOTSTRAP_SERVERS,
        group_id="satellite-reply-consumer",
        auto_offset_reset="latest",
    )
    await consumer.start()
    logger.info(f"Reply consumer started on topic '{REPLY_TOPIC}'")
    try:
        async for msg in consumer:
            try:
                reply = json.loads(msg.value.decode("utf-8"))
                message_id = reply.get("message_id")
                if message_id and message_id in pending_replies:
                    future = pending_replies.pop(message_id)
                    if not future.done():
                        future.set_result(reply)
                else:
                    logger.debug(f"Received reply for unknown message_id: {message_id}")
            except Exception as e:
                logger.error(f"Error processing reply: {e}")
    finally:
        await consumer.stop()


@asynccontextmanager
async def lifespan(app: FastAPI):
    global kafka_producer
    logger.info("Initializing Kafka Producer...")

    kafka_producer = AIOKafkaProducer(bootstrap_servers=BOOTSTRAP_SERVERS)
    try:
        await kafka_producer.start()
        logger.info("Kafka Producer started.")
    except Exception as e:
        logger.error(f"Failed to start Kafka Producer: {e}")

    # Start reply consumer as background task
    reply_task = asyncio.create_task(reply_consumer_task())

    yield

    reply_task.cancel()
    try:
        await reply_task
    except asyncio.CancelledError:
        pass

    if kafka_producer:
        await kafka_producer.stop()
        logger.info("Kafka Producer stopped.")


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"https://.*\.cloudshell\.dev|http://localhost.*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class FormationRequest(BaseModel):
    formation: str


@app.get("/stream")
async def message_stream(request: Request):
    async def event_generator():
        logger.info("New SSE stream connected")
        try:
            while True:
                current_pods = list(PODS)

                # Send updates one by one to simulate low-bandwidth scanning
                for pod in current_pods:
                    payload = {"pod": pod}
                    yield {
                        "event": "pod_update",
                        "data": json.dumps(payload)
                    }
                    await asyncio.sleep(0.02)

                # Send formation info occasionally
                yield {
                    "event": "formation_update",
                    "data": json.dumps({"formation": FORMATION})
                }

                # Main loop delay
                await asyncio.sleep(0.5)

        except asyncio.CancelledError:
            logger.info("SSE stream disconnected (cancelled)")
        except Exception as e:
            logger.error(f"SSE stream error: {e}")

    return EventSourceResponse(event_generator())


@app.post("/formation")
async def set_formation(req: FormationRequest):
    global FORMATION, PODS
    FORMATION = req.formation
    logger.info(f"Received formation request: {FORMATION}")

    if not kafka_producer:
        logger.error("Kafka Producer is not initialized!")
        return {"status": "error", "message": "Backend Not Connected"}

    try:
        prompt = f"Create a {FORMATION} formation"
        msg_id = str(uuid.uuid4())

        # Build request message
        message = {
            "message_id": msg_id,
            "reply_topic": REPLY_TOPIC,
            "text": prompt,
        }

        # Register future before sending to avoid race condition
        loop = asyncio.get_event_loop()
        future: asyncio.Future = loop.create_future()
        pending_replies[msg_id] = future

        logger.info(f"Sending Kafka message (id={msg_id}): '{prompt}'")
        await kafka_producer.send_and_wait(REQUEST_TOPIC, json.dumps(message).encode("utf-8"))

        # Wait for reply (timeout 120s for GenAI latency)
        try:
            response = await asyncio.wait_for(future, timeout=120.0)
        except asyncio.TimeoutError:
            pending_replies.pop(msg_id, None)
            return {"status": "error", "message": "Agent timeout"}

        content = response.get("text", "")
        logger.info(f"Agent response: {content[:100]}...")

        if content:
            try:
                clean_content = content.replace("```json", "").replace("```", "").strip()
                coords = json.loads(clean_content)

                if isinstance(coords, list):
                    logger.info(f"Parsed {len(coords)} coordinates.")
                    for i, pod_target in enumerate(coords):
                        if i < len(PODS):
                            PODS[i]["x"] = pod_target["x"]
                            PODS[i]["y"] = pod_target["y"]
                    return {"status": "success", "formation": FORMATION}
                else:
                    logger.error("Response JSON is not a list.")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse Agent JSON response: {e}")

    except Exception as e:
        logger.error(f"Error calling agent via Kafka: {e}")
        return {"status": "error", "message": str(e)}


class PodUpdate(BaseModel):
    id: int
    x: int
    y: int


@app.post("/update_pod")
async def update_pod_manual(update: PodUpdate):
    """Manual override for drag-and-drop."""
    global FORMATION
    FORMATION = "RANDOM"

    found = False
    for p in PODS:
        if p["id"] == update.id:
            p["x"] = update.x
            p["y"] = update.y
            found = True
            break

    for t in TARGET_PODS:
        if t["id"] == update.id:
            t["x"] = update.x
            t["y"] = update.y
            break

    return {"status": "updated", "id": update.id}


from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Serve Static Assets (JS/CSS)
dist_dir = os.path.join(os.path.dirname(__file__), "../frontend/dist")

if os.path.exists(dist_dir):
    app.mount("/assets", StaticFiles(directory=os.path.join(dist_dir, "assets")), name="assets")

    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        possible_file = os.path.join(dist_dir, full_path)
        if os.path.isfile(possible_file):
            return FileResponse(possible_file)
        return FileResponse(os.path.join(dist_dir, "index.html"))
else:
    logger.warning("Frontend build not found. Please run 'npm run build' in frontend/.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8083, proxy_headers=True, forwarded_allow_ips="*")
