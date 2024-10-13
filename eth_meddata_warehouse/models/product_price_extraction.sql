{{ config(materialized='table') }}

WITH source_data AS (
    SELECT * 
    FROM {{ ref('transformed_telegram_messages') }}
),
phone_extracted AS (
    SELECT
        id,
        channel,
        timestamp,
        content AS "Message",
        -- Extract phone numbers with optional spaces
        array_to_string(ARRAY(
            SELECT regexp_replace(unnest(regexp_matches(content, '09\s*[0-9]{8}', 'g')), '\s+', '', 'g')
        ), ', ') AS phone_numbers,
        -- Clean the message of phone numbers
        regexp_replace(
            content, 
            '09\s*[0-9]{8}', 
            '', 
            'g'
        ) AS cleaned_message
    FROM source_data
),
product_price_extracted AS (
    SELECT
        id,
        channel,
        timestamp,
        TRIM(cleaned_message) AS cleaned_message,
        phone_numbers,
        -- Adjusted regex to capture product names and prices
        regexp_matches(cleaned_message, '^(.*?)\s*(?:price|Price|PRICE)\s*(\d+)\s*(birr|ETB)', 'g') AS matches,
        ROW_NUMBER() OVER (PARTITION BY id ORDER BY timestamp DESC) AS rn  -- Add row number to filter
    FROM phone_extracted
)
SELECT
    id,
    channel,
    timestamp,
    TRIM(matches[1]) AS product_name,  -- Extract product name
    CAST(TRIM(matches[2]) AS INTEGER) AS price_in_birr,  -- Extract price as an integer
    CASE
        WHEN phone_numbers IS NOT NULL AND phone_numbers != '' THEN phone_numbers
        ELSE NULL
    END AS contact_phone_numbers  -- Renamed for clarity
FROM product_price_extracted
WHERE matches IS NOT NULL  -- Filter out any rows where matches are not found
AND rn = 1  -- Select only the first occurrence of each id
AND TRIM(matches[1]) <> ''  -- Drop empty product names
AND TRIM(matches[1]) <> TRIM(matches[2])  -- Drop rows where product name and price are the same
ORDER BY id  -- Optional: order by id