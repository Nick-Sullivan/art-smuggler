from enum import Enum
from typing import TypedDict, Union


class EventType(Enum):
    STATUS = "status"
    IMAGE = "image"
    COMPLETE = "complete"
    ERROR = "error"


class MessageEventData(TypedDict):
    message: str
    timestamp: str


class ImageEventData(TypedDict):
    image: str
    index: int
    timestamp: str


EventData = Union[MessageEventData, ImageEventData]
