import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv
import logging
from datetime import datetime

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    filename='../logs/data_cleaning_transformation.log',
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

# Create SQLAlchemy engine
engine = create_engine(f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}')

def load_data():
    """Load data from PostgreSQL database"""
    query = "SELECT * FROM telegram_messages"
    df = pd.read_sql(query, engine)
    logging.info(f"Loaded {len(df)} records from the database")
    return df

def remove_duplicates(df):
    """Remove duplicate records based on message_id and channel"""
    before_count = len(df)
    df.drop_duplicates(subset=['message_id', 'channel'], keep='first', inplace=True)
    after_count = len(df)
    logging.info(f"Removed {before_count - after_count} duplicate records")
    return df

def handle_missing_values(df):
    """Handle missing values in the dataset"""
    # Fill missing content with empty string
    df['content'].fillna('', inplace=True)
    
    # Fill missing views with 0
    df['views'].fillna(0, inplace=True)
    
    # Drop rows with missing timestamps
    before_count = len(df)
    df.dropna(subset=['timestamp'], inplace=True)
    after_count = len(df)
    logging.info(f"Dropped {before_count - after_count} rows with missing timestamps")
    
    return df

def standardize_formats(df):
    """Standardize data formats"""
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True)
    
    # Ensure views is integer
    df['views'] = df['views'].astype(int)
    
    # Standardize channel names
    df['channel'] = df['channel'].str.lower().str.strip()
    
    return df

def data_validation(df):
    """Perform data validation"""
    # Check for future dates
    future_dates = df[df['timestamp'] > datetime.now(df['timestamp'].dt.tz)]
    if not future_dates.empty:
        logging.warning(f"Found {len(future_dates)} records with future dates")
        df = df[df['timestamp'] <= datetime.now(df['timestamp'].dt.tz)]
    
    # Check for negative views
    negative_views = df[df['views'] < 0]
    if not negative_views.empty:
        logging.warning(f"Found {len(negative_views)} records with negative views")
        df.loc[df['views'] < 0, 'views'] = 0
    
    return df

def clean_data(df):
    """Perform all data cleaning steps"""
    df = remove_duplicates(df)
    df = handle_missing_values(df)
    df = standardize_formats(df)
    df = data_validation(df)
    return df

def save_to_database(df, table_name):
    """Save cleaned data back to the database"""
    df.to_sql(table_name, engine, if_exists='replace', index=False)
    logging.info(f"Saved {len(df)} cleaned records to {table_name}")

def main():
    try:
        # Load data
        df = load_data()
        
        # Clean data
        cleaned_df = clean_data(df)
        
        # Save cleaned data
        save_to_database(cleaned_df, 'cleaned_telegram_messages')
        
        logging.info("Data cleaning and transformation completed successfully")
    except Exception as e:
        logging.error(f"Data cleaning and transformation failed: {e}")

if __name__ == '__main__':
    main()