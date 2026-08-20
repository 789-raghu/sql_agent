-- Analytical database views for complex energy reporting

CREATE OR REPLACE VIEW consumer_daily_summary AS
SELECT 
    c.consumer_id,
    c.name AS consumer_name,
    c.category,
    cl.name AS cluster_name,
    l.city,
    ds.date,
    ds.total_consumption,
    ds.avg_consumption,
    ds.max_consumption,
    ds.min_consumption
FROM daily_summary ds
JOIN consumers c ON ds.consumer_id = c.consumer_id
LEFT JOIN clusters cl ON c.cluster_id = cl.cluster_id
LEFT JOIN locations l ON c.location_id = l.location_id;

CREATE OR REPLACE VIEW consumer_monthly_summary AS
SELECT 
    c.consumer_id,
    c.name AS consumer_name,
    c.category,
    TO_CHAR(ds.date, 'YYYY-MM') AS year_month,
    SUM(ds.total_consumption) AS monthly_total_consumption,
    AVG(ds.avg_consumption) AS monthly_avg_consumption,
    MAX(ds.max_consumption) AS monthly_peak_consumption
FROM daily_summary ds
JOIN consumers c ON ds.consumer_id = c.consumer_id
GROUP BY c.consumer_id, c.name, c.category, TO_CHAR(ds.date, 'YYYY-MM');

CREATE OR REPLACE VIEW consumer_predictions AS
SELECT 
    co.consumer_id,
    c.name AS consumer_name,
    co.timestamp,
    co.consumption AS actual_consumption,
    p.predicted_consumption,
    (co.consumption - p.predicted_consumption) AS difference,
    CASE 
        WHEN p.predicted_consumption > 0 THEN 
            ROUND(((co.consumption - p.predicted_consumption) / p.predicted_consumption * 100.0), 2)
        ELSE 0.0 
    END AS percentage_exceeded
FROM consumption co
JOIN predictions p ON co.consumer_id = p.consumer_id AND co.timestamp = p.timestamp
JOIN consumers c ON co.consumer_id = c.consumer_id;

CREATE OR REPLACE VIEW consumer_cluster_summary AS
SELECT 
    cl.cluster_id,
    cl.name AS cluster_name,
    cl.region,
    COUNT(DISTINCT c.consumer_id) AS total_consumers,
    COALESCE(AVG(ds.avg_consumption), 0) AS cluster_avg_consumption,
    COALESCE(SUM(ds.total_consumption), 0) AS cluster_total_consumption
FROM clusters cl
LEFT JOIN consumers c ON cl.cluster_id = c.cluster_id
LEFT JOIN daily_summary ds ON c.consumer_id = ds.consumer_id
GROUP BY cl.cluster_id, cl.name, cl.region;
