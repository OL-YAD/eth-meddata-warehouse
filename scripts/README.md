# Ethiopian Medical Data Warehouse

## Overview
This project builds a comprehensive data warehouse for Ethiopian medical business data scraped from Telegram channels. It includes data scraping, cleaning, transformation, object detection using YOLO, and a FastAPI interface for data access.

## Features
- Telegram channel scraping for medical business data
- Data cleaning and transformation using DBT (Data Build Tool)
- Object detection in images using YOLO
- Data warehouse implementation
- FastAPI interface for data access

## Technologies Used
- Python
- Telethon (for Telegram scraping)
- DBT (Data Build Tool)
- YOLO (You Only Look Once) for object detection
- FastAPI
- SQLAlchemy
- PostgreSQL


## Folder Structure

- `notebooks/` : Jupyter notebooks for all the analysis.
- `scripts/`   : Python scripts files.


## scripts Folder/ 

```
    `telegram_scraper.py`              : a script file for scraping data from telegram 
    `data_cleaning_transformation.py`  : a script file that contains data cleaning and transformation pipeline  
    `yolo_object_detection.py`         : a script file for object detection
    
```

## Setup Instructions
1. Clone the repository.
2. Set up the virtual environment.
3. Install dependencies using `pip install -r requirements.txt`
