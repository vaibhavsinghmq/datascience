create or Replace table mq-bigdata-technologies.assignment_3.p13_part4
as
SELECT count(*) AS product_views, 
count(DISTINCT fullvisitorid) AS unique_visitors 
FROM `data-to-insights.ecommerce.all_sessions`