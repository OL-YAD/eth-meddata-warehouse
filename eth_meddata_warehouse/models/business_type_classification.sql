{{ config(materialized='table') }}

WITH business_types AS (
    SELECT 'hospital' AS type, ARRAY['hospital', 'clinic', 'medical center'] AS keywords
    UNION ALL SELECT 'pharmacy', ARRAY['pharmacy', 'drug store', 'medicine shop']
    UNION ALL SELECT 'doctor office', ARRAY['doctor', 'physician', 'specialist']
    UNION ALL SELECT 'laboratory', ARRAY['lab', 'laboratory', 'test', 'diagnostic']
),
classified_messages AS (
    SELECT
        tm.id,
        tm.channel,
        tm.content,
        bt.type
    FROM {{ ref('transformed_telegram_messages') }} tm
    CROSS JOIN business_types bt
    WHERE EXISTS (
        SELECT 1
        FROM unnest(bt.keywords) kw
        WHERE tm.content ILIKE '%' || kw || '%'
    )
)
SELECT
    channel,
    type,
    COUNT(*) AS message_count,
    COUNT(*) * 100.0 / SUM(COUNT(*)) OVER (PARTITION BY channel) AS percentage
FROM classified_messages
GROUP BY channel, type
ORDER BY channel, message_count DESC