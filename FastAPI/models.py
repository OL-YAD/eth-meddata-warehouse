from sqlalchemy import Column, Integer, String, DateTime, Float, JSON
from database import Base

class TelegramMessage(Base):
    __tablename__ = "cleaned_telegram_messages"

    id = Column(Integer, primary_key=True, index=True)
    message_id = Column(String)
    channel = Column(String)
    timestamp = Column(DateTime)
    content = Column(String)
    views = Column(Integer)

class ObjectDetection(Base):
    __tablename__ = "object_detections"

    id = Column(Integer, primary_key=True, index=True)
    image_path = Column(String)
    class_name = Column(String)
    confidence = Column(Float)
    bbox = Column(JSON)