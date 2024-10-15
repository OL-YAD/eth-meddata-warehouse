from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

import crud, models, schemas
from database import engine, get_db

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the Ethiopian Medical Business DataWarehouse API"}

@app.get("/telegram_messages/", response_model=List[schemas.TelegramMessage])
def read_telegram_messages(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    messages = crud.get_telegram_messages(db, skip=skip, limit=limit)
    return messages

@app.get("/telegram_messages/{message_id}", response_model=schemas.TelegramMessage)
def read_telegram_message(message_id: int, db: Session = Depends(get_db)):
    db_message = crud.get_telegram_message(db, message_id=message_id)
    if db_message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return db_message

@app.get("/object_detections/", response_model=List[schemas.ObjectDetection])
def read_object_detections(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    detections = crud.get_object_detections(db, skip=skip, limit=limit)
    return detections

@app.get("/object_detections/{detection_id}", response_model=schemas.ObjectDetection)
def read_object_detection(detection_id: int, db: Session = Depends(get_db)):
    db_detection = crud.get_object_detection(db, detection_id=detection_id)
    if db_detection is None:
        raise HTTPException(status_code=404, detail="Detection not found")
    return db_detection

@app.post("/telegram_messages/", response_model=schemas.TelegramMessage)
def create_telegram_message(message: schemas.TelegramMessageCreate, db: Session = Depends(get_db)):
    return crud.create_telegram_message(db=db, message=message)

@app.post("/object_detections/", response_model=schemas.ObjectDetection)
def create_object_detection(detection: schemas.ObjectDetectionCreate, db: Session = Depends(get_db)):
    return crud.create_object_detection(db=db, detection=detection)

# New update endpoints
@app.put("/telegram_messages/{message_id}", response_model=schemas.TelegramMessage)
def update_telegram_message(message_id: int, message: schemas.TelegramMessageUpdate, db: Session = Depends(get_db)):
    db_message = crud.update_telegram_message(db, message_id=message_id, message=message)
    if db_message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return db_message

@app.put("/object_detections/{detection_id}", response_model=schemas.ObjectDetection)
def update_object_detection(detection_id: int, detection: schemas.ObjectDetectionUpdate, db: Session = Depends(get_db)):
    db_detection = crud.update_object_detection(db, detection_id=detection_id, detection=detection)
    if db_detection is None:
        raise HTTPException(status_code=404, detail="Detection not found")
    return db_detection

# New delete endpoints
@app.delete("/telegram_messages/{message_id}", response_model=schemas.TelegramMessage)
def delete_telegram_message(message_id: int, db: Session = Depends(get_db)):
    db_message = crud.delete_telegram_message(db, message_id=message_id)
    if db_message is None:
        raise HTTPException(status_code=404, detail="Message not found")
    return db_message

@app.delete("/object_detections/{detection_id}", response_model=schemas.ObjectDetection)
def delete_object_detection(detection_id: int, db: Session = Depends(get_db)):
    db_detection = crud.delete_object_detection(db, detection_id=detection_id)
    if db_detection is None:
        raise HTTPException(status_code=404, detail="Detection not found")
    return db_detection

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)