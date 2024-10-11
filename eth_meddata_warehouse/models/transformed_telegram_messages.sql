{{ config(materialized='table') }}

WITH source_data AS (
    SELECT * FROM {{ source('telegram', 'cleaned_telegram_messages') }}
)

SELECT
    id,
    channel,
    message_id,
    content,
    timestamp,
    views,
    message_link,
    image_path,
    -- Add derived columns
    DATE(timestamp) AS message_date,
    EXTRACT(HOUR FROM timestamp) AS message_hour,
    LENGTH(content) AS content_length,
    CASE
        WHEN views > 1000 THEN 'High'
        WHEN views > 100 THEN 'Medium'
        ELSE 'Low'
    END AS popularity
FROM source_data