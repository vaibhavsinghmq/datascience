create or Replace table mq-bigdata-technologies.assignment_3.p13_part12
as
SELECT
count(fullvisitorId) as number_of_visitors,
v2ProductName,
sum(pageviews) as pageviews,
SUM(productQuantity) as sum_Quantity,
COUNT(productQuantity)as count_Quantity,
SUM(productQuantity)/COUNT(productQuantity) as  average_amount_of_product_per_order,
FROM `data-to-insights.ecommerce.all_sessions_raw`
group by v2ProductName
order by SUM(productQuantity)/COUNT(productQuantity) desc
limit 10