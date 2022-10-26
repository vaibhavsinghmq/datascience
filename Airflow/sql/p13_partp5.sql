create or Replace table mq-bigdata-technologies.assignment_3.p13_part5
as
SELECT 
channelGrouping,
count(fullvisitorid) as total_visitors,
COUNT(DISTINCT fullvisitorid) AS unique_visitors
FROM `data-to-insights.ecommerce.all_sessions_raw`
group by channelGrouping