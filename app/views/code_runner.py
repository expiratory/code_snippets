import asyncio
import json
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.mq import publish_event
from app.redis import get_redis
from app.schemas.code_runner import CodeRunRequest

router = APIRouter(prefix="/code", tags=["code"])


@router.websocket("/ws/run")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    redis_gen = get_redis()
    redis_client = await anext(redis_gen)
    pubsub = redis_client.pubsub()

    try:
        while True:
            data = await websocket.receive_text()
            try:
                payload = json.loads(data)
                # Validate payload using Pydantic
                request = CodeRunRequest(**payload)
            except Exception as e:
                await websocket.send_json({"error": f"Invalid request: {str(e)}"})
                continue

            task_id = str(uuid.uuid4())

            # Subscribe to result channel
            await pubsub.subscribe(f"task_results:{task_id}")

            # Publish task to RabbitMQ
            await publish_event(
                "code_execution_tasks",
                "run_code",
                {
                    "task_id": task_id,
                    "code": request.code,
                    "language": request.language,
                },
            )

            # Wait for result
            try:
                while True:
                    message = await pubsub.get_message(
                        ignore_subscribe_messages=True, timeout=1.0
                    )
                    if message:
                        result = json.loads(message["data"])
                        await websocket.send_json(result)
                        break
                    await asyncio.sleep(0.1)
            except Exception as e:
                await websocket.send_json({"error": f"Execution error: {str(e)}"})
            finally:
                await pubsub.unsubscribe(f"task_results:{task_id}")

    except WebSocketDisconnect:
        pass
    finally:
        await redis_client.aclose()
