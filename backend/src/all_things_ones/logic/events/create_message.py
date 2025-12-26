import json

from .model import EventData, EventType


def create_sse_message(event_type: EventType, data: EventData) -> str:
    return f"event: {event_type.value}\ndata: {json.dumps(data)}\n\n"


def create_status_message(data: str) -> str:
    return create_sse_message(EventType.STATUS, {"message": data})


def create_image_message(data: str, index: int) -> str:
    return create_sse_message(EventType.IMAGE, {"image": data, "index": index})


def create_complete_message(data: str) -> str:
    return create_sse_message(EventType.COMPLETE, {"message": data})


def create_error_message(data: str) -> str:
    return create_sse_message(EventType.ERROR, {"message": data})
