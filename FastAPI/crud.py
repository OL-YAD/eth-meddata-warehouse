from sqlalchemy.orm import Session
import models, schemas

def get_telegram_messages(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.TelegramMessage).offset(skip).limit(limit).all()

def get_telegram_message(db: Session, message_id: int):
    return db.query(models.TelegramMessage).filter(models.TelegramMessage.id == message_id).first()

def get_object_detections(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.ObjectDetection).offset(skip).limit(limit).all()

def get_object_detection(db: Session, detection_id: int):
    return db.query(models.ObjectDetection).filter(models.ObjectDetection.id == detection_id).first()

def create_telegram_message(db: Session, message: schemas.TelegramMessageCreate):
    db_message = models.TelegramMessage(**message.dict())
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message

def create_object_detection(db: Session, detection: schemas.ObjectDetectionCreate):
    db_detection = models.ObjectDetection(**detection.dict())
    db.add(db_detection)
    db.commit()
    db.refresh(db_detection)
    return db_detection


def update_telegram_message(db: Session, message_id: int, message: schemas.TelegramMessageUpdate):
    db_message = db.query(models.TelegramMessage).filter(models.TelegramMessage.id == message_id).first()
    if db_message:
        update_data = message.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_message, key, value)
        db.commit()
        db.refresh(db_message)
    return db_message

def update_object_detection(db: Session, detection_id: int, detection: schemas.ObjectDetectionUpdate):
    db_detection = db.query(models.ObjectDetection).filter(models.ObjectDetection.id == detection_id).first()
    if db_detection:
        update_data = detection.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_detection, key, value)
        db.commit()
        db.refresh(db_detection)
    return db_detection

def delete_telegram_message(db: Session, message_id: int):
    db_message = db.query(models.TelegramMessage).filter(models.TelegramMessage.id == message_id).first()
    if db_message:
        db.delete(db_message)
        db.commit()
    return db_message

def delete_object_detection(db: Session, detection_id: int):
    db_detection = db.query(models.ObjectDetection).filter(models.ObjectDetection.id == detection_id).first()
    if db_detection:
        db.delete(db_detection)
        db.commit()
    return db_detection