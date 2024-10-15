from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class TelegramMessageBase(BaseModel):
    message_id: int
    channel: str
    timestamp: datetime
    content: str
    views: int

class TelegramMessage(TelegramMessageBase):
    id: int

    class Config:
        orm_mode = True

class ObjectDetectionBase(BaseModel):
    image_path: str
    class_name: str
    confidence: float
    bbox: List[float]

class ObjectDetection(ObjectDetectionBase):
    id: int

    class Config:
        orm_mode = True

class TelegramMessageCreate(TelegramMessageBase):
    pass

class ObjectDetectionCreate(ObjectDetectionBase):
    pass

class TelegramMessageUpdate(BaseModel):
    message_id: Optional[int] = None
    channel: Optional[str] = None
    timestamp: Optional[datetime] = None
    content: Optional[str] = None
    views: Optional[int] = None

class ObjectDetectionUpdate(BaseModel):
    image_path: Optional[str] = None
    class_name: Optional[str] = None
    confidence: Optional[float] = None
    bbox: Optional[List[float]] = None
    