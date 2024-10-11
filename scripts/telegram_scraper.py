import os
import logging
import asyncio
import csv
import json
import pandas as pd
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql
from telethon import TelegramClient, events
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError
from telethon.tl.types import MessageMediaPhoto
from prometheus_client import start_http_server, Counter


load_dotenv()


logging.basicConfig(
    filename='../logs/telegram_scraper.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Telegram API credentials
api_id = os.getenv('TELEGRAM_API_ID')
api_hash = os.getenv('TELEGRAM_API_HASH')
phone_number = os.getenv('TELEGRAM_PHONE_NUMBER')

# PostgreSQL database credentials
db_host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_port = os.getenv('DB_PORT')

# Directory to save CSV files and raw data
csv_directory = os.getenv('CSV_DIRECTORY', '../data/raw/csv')
raw_data_directory = os.getenv('RAW_DATA_DIRECTORY', '../data/raw_json')

# Prometheus metrics
messages_processed_counter = Counter('messages_processed', 'Number of messages processed')

async def start_telegram_client():
    """Start the Telegram client and handle authentication."""
    client = TelegramClient(phone_number, api_id, api_hash)
    await client.connect()
    if not await client.is_user_authorized():
        await client.send_code_request(phone_number)
        try:
            await client.sign_in(phone_number, input('Enter the code: '))
        except SessionPasswordNeededError:
            await client.sign_in(password=input('Enter your password: '))
        except PhoneCodeInvalidError:
            logging.error('Invalid code. Please try again.')
            return None
    return client

async def download_image(client, message, channel_title):
    """Download image from message."""
    if message.media and isinstance(message.media, MessageMediaPhoto):
        image_path = f"{raw_data_directory}/images/{channel_title}_{message.id}.jpg"
        os.makedirs(os.path.dirname(image_path), exist_ok=True)
        await client.download_media(message.media, file=image_path)
        return image_path
    return None

async def extract_telegram_data(client):
    """Extract data from Telegram channels."""
    channel_urls = [
        'https://t.me/DoctorsET',
        'https://t.me/CheMed123',
        'https://t.me/lobelia4cosmetics',
        'https://t.me/yetenaweg',
        'https://t.me/EAHCI'
    ]
    for channel_url in channel_urls:
        try:
            channel = await client.get_entity(channel_url)
            messages = await client.get_messages(channel, limit=None)
            data = []
            for message in messages:
                image_path = await download_image(client, message, channel.title)
                data.append({
                    'channel': channel.title,
                    'message_id': message.id,
                    'content': message.message,
                    'timestamp': message.date,
                    'views': message.views,
                    'message_link': f'https://t.me/{channel.username}/{message.id}' if channel.username else None,
                    'image_path': image_path
                })
            df = pd.DataFrame(data)
            save_to_csv(df, channel.title)
            save_to_database(df, 'telegram_messages')
            save_raw_data(channel.title, data)
            messages_processed_counter.inc(len(messages))
        except Exception as e:
            logging.error(f'Error extracting data from {channel_url}: {e}')

def save_to_csv(df, channel_title):
    """Save DataFrame to a CSV file."""
    if not os.path.exists(csv_directory):
        os.makedirs(csv_directory)
    csv_file_path = os.path.join(csv_directory, f'{channel_title}.csv')
    try:
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow(df.columns)
            # Write data rows
            for index, row in df.iterrows():
                writer.writerow(row)
        logging.info(f'Saved data to CSV file: {csv_file_path}')
    except Exception as e:
        logging.error(f'Error saving data to CSV file: {e}')

def save_to_database(df, table_name):
    """Save DataFrame to PostgreSQL database."""
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
            CREATE TABLE IF NOT EXISTS {} (
                id SERIAL PRIMARY KEY,
                channel TEXT,
                message_id INT,
                content TEXT,
                timestamp TIMESTAMP WITH TIME ZONE,
                views FLOAT,
                message_link TEXT,
                image_path TEXT
            )
        """).format(sql.Identifier(table_name))
        cursor.execute(create_table_query)

        for index, row in df.iterrows():
            select_query = sql.SQL("""
                SELECT 1 FROM {} WHERE message_id = %s
            """).format(sql.Identifier(table_name))
            cursor.execute(select_query, (row['message_id'],))
            if cursor.fetchone():
                update_query = sql.SQL("""
                    UPDATE {} SET
                        channel = %s,
                        content = %s,
                        timestamp = %s,
                        views = %s,
                        message_link = %s,
                        image_path = %s
                    WHERE message_id = %s
                """).format(sql.Identifier(table_name))
                cursor.execute(update_query, (row['channel'], row['content'], row['timestamp'], row['views'], row['message_link'], row['image_path'], row['message_id']))
            else:
                insert_query = sql.SQL("""
                    INSERT INTO {} (channel, message_id, content, timestamp, views, message_link, image_path)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """).format(sql.Identifier(table_name))
                cursor.execute(insert_query, (row['channel'], row['message_id'], row['content'], row['timestamp'], row['views'], row['message_link'], row['image_path']))

        conn.commit()
        cursor.close()
        conn.close()
        logging.info(f'Saved {len(df)} records to {table_name}')
    except psycopg2.DatabaseError as e:
        logging.error(f'Database error: {e}')
    except Exception as e:
        logging.error(f'Error saving data to database: {e}')

def save_raw_data(channel_title, data):
    """Save raw data to JSON file."""
    if not os.path.exists(raw_data_directory):
        os.makedirs(raw_data_directory)
    
    json_file_path = os.path.join(raw_data_directory, f'{channel_title}_raw.json')
    try:
        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)
        logging.info(f'Saved raw data to JSON file: {json_file_path}')
    except Exception as e:
        logging.error(f'Error saving raw data to JSON file: {e}')

async def main():
    """Main function to orchestrate the data pipeline."""
    try:
        # Start Prometheus HTTP server
        start_http_server(8000)
        
        client = await start_telegram_client()
        if client:
            await extract_telegram_data(client)
            await client.disconnect()

        logging.info("Telegram data extraction and loading process completed successfully.")
    except Exception as e:
        logging.error(f"Telegram data extraction and loading process failed: {e}")

if __name__ == '__main__':
    asyncio.run(main())