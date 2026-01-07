from cent import Client
from app.core.config import settings

client = Client(
    settings.CENTRIFUGO_API_URL,
    settings.CENTRIFUGO_API_KEY,
    timeout=10
)

async def broadcast_message(channel: str, event: str, data: dict):
    payload = {"event": event, "data": data}
    try:
        client.publish(channel, payload)
    except Exception as e:
        print(f"Centrifugo error: {e}")
