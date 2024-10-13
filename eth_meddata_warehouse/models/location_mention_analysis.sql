{{ config(materialized='table') }}

WITH ethiopian_cities AS (
    SELECT UNNEST(ARRAY['Addis Ababa', 'Dire Dawa', 'Mekele', 'Gondar', 'Bahir Dar', 'Dessie', 'Jimma', 'Jijiga', 'Shashamane', 'Bishoftu', 'Sodo', 'Arba Minch', 'Hosaena', 'Harar', 'Dilla', 'Nekemte', 'Debre Birhan', 'Asella', 'Debre Markos', 'Kombolcha']) AS city
),
city_mentions AS (
    SELECT
        tm.id,
        tm.channel,
        tm.timestamp,
        ec.city
    FROM {{ ref('transformed_telegram_messages') }} tm
    CROSS JOIN ethiopian_cities ec
    WHERE tm.content ILIKE '%' || ec.city || '%'
)
SELECT
    channel,
    city,
    COUNT(*) AS mention_count,
    COUNT(DISTINCT DATE(timestamp)) AS days_mentioned
FROM city_mentions
GROUP BY channel, city
ORDER BY channel, mention_count DESC