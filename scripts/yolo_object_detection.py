import os
import logging
import json
import torch
from PIL import Image
import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    filename='../logs/object_detection.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# PostgreSQL database credentials
db_host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_port = os.getenv('DB_PORT')

def load_yolo_model():
    """Load the pre-trained YOLO model"""
    model = torch.hub.load('ultralytics/yolov5', 'yolov5s', pretrained=True)
    model.eval()
    return model

def process_image(model, image_path):
    """Process a single image using the YOLO model"""
    image = Image.open(image_path)
    results = model(image)
    return results

def extract_detection_data(results, image_path):
    """Extract relevant data from the detection results"""
    detections = []
    for pred in results.pred[0]:
        x1, y1, x2, y2, conf, cls = pred
        detections.append({
            'image_path': image_path,
            'class_name': results.names[int(cls)],
            'confidence': float(conf),
            'bbox': [float(x1), float(y1), float(x2), float(y2)]
        })
    return detections

def save_detection_results(detections):
    """Save detection results to the database"""
    try:
        conn = psycopg2.connect(
            host=db_host,
            database=db_name,
            user=db_user,
            password=db_password
        )
        cursor = conn.cursor()

        # Create the table if it doesn't exist
        create_table_query = sql.SQL("""
            CREATE TABLE IF NOT EXISTS object_detections (
                id SERIAL PRIMARY KEY,
                image_path TEXT,
                class_name TEXT,
                confidence FLOAT,
                bbox JSON
            )
        """)
        cursor.execute(create_table_query)

        # Insert detection results
        insert_query = sql.SQL("""
            INSERT INTO object_detections (image_path, class_name, confidence, bbox)
            VALUES (%s, %s, %s, %s)
        """)
        for detection in detections:
            cursor.execute(insert_query, (
                detection['image_path'],
                detection['class_name'],
                detection['confidence'],
                json.dumps(detection['bbox'])
            ))

        conn.commit()
        cursor.close()
        conn.close()
        logging.info(f'Saved {len(detections)} detection results to database')
    except psycopg2.DatabaseError as e:
        logging.error(f'Database error: {e}')
    except Exception as e:
        logging.error(f'Error saving detection results to database: {e}')

def process_all_images(image_directory):
    """Process all images in the directory using YOLO"""
    model = load_yolo_model()
    all_detections = []

    for root, _, files in os.walk(image_directory):
        for file in files:
            if file.lower().endswith(('.png', '.jpg', '.jpeg')):
                image_path = os.path.join(root, file)
                try:
                    results = process_image(model, image_path)
                    detections = extract_detection_data(results, image_path)
                    all_detections.extend(detections)
                    logging.info(f'Processed image: {image_path}')
                except Exception as e:
                    logging.error(f'Error processing image {image_path}: {e}')

    save_detection_results(all_detections)
    return all_detections