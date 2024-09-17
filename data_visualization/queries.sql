-- summary
SELECT 
    SUM(total) AS total,
    SUM(available_rent_bikes) AS rent,
    SUM(available_return_bikes) AS return,
    ROUND(SUM(available_return_bikes) * 1.0 / SUM(total), 2) AS ratio
FROM cleaned_youbike
WHERE mday >= '2024-09-08' AND mday < '2024-09-15';

-- region
SELECT DISTINCT sarea FROM cleaned_youbike;

-- scatter
SELECT 
    sarea,
    b.population_density/1000 AS population_density,
    ROUND(SUM(available_return_bikes) * 1.0/SUM(total), 2) AS usage_ratio
FROM cleaned_youbike AS a
LEFT JOIN cleaned_density_by_district AS b
ON a.sarea = b.district
WHERE mday >= '2024-09-08' AND mday < '2024-09-15' AND sarea LIKE '%區'
GROUP BY sarea;

-- route
WITH stop_coordinates AS (
    SELECT stop_name, AVG(latitude) AS latitude, AVG(longitude) AS longitude
    FROM cleaned_visibility_rate
    GROUP BY stop_name
)

SELECT 
    tbb.on_stop, 
    on_stop_coord.latitude AS on_stop_lat, 
    on_stop_coord.longitude AS on_stop_lon,
    tbb.off_stop,
    off_stop_coord.latitude AS off_stop_lat,
    off_stop_coord.longitude AS off_stop_lon,
    tbb.sum_of_txn_times, 
    tbb.district_origin,
    tbb.district_destination
FROM cleaned_origin_destination tbb
LEFT JOIN stop_coordinates on_stop_coord
    ON tbb.on_stop = on_stop_coord.stop_name
LEFT JOIN stop_coordinates off_stop_coord
    ON tbb.off_stop = off_stop_coord.stop_name
ORDER BY tbb.sum_of_txn_times DESC
LIMIT 15;

-- cross
WITH tba AS (
    SELECT 
        CASE 
            WHEN district_origin = district_destination THEN 'same_district' 
            ELSE 'different_district' 
        END AS route_type,
        SUM(sum_of_txn_times) AS sum_of_txn_times
    FROM 
        cleaned_origin_destination
    GROUP BY 
        district_origin, 
        district_destination
),

route_totals AS (
    SELECT 
        route_type,
        SUM(sum_of_txn_times) AS sum_of_txn_times
    FROM 
        tba
    GROUP BY 
        route_type
)

SELECT 
    route_type,
    sum_of_txn_times,
    (sum_of_txn_times * 1.0 / (SELECT SUM(sum_of_txn_times) FROM route_totals)) AS percentage
FROM 
    route_totals;

-- visibility
WITH tba AS (
SELECT DISTINCT sna, sarea
FROM cleaned_youbike
)

SELECT sarea, stop_name, capacity, category
FROM cleaned_visibility_rate tbb
LEFT JOIN tba
ON tba.sna = tbb.stop_name;

-- sna
SELECT 
  sarea,
  sna, 
  ROUND(SUM(available_return_bikes) * 100 / SUM(total), 2) || '%' AS usage_ratio
FROM cleaned_youbike
WHERE mday >= '2024-09-08' AND mday < '2024-09-15'
GROUP BY sarea, sna
ORDER BY usage_ratio DESC

-- orgdes
SELECT district_origin, on_stop, district_destination, off_stop, 
        SUM(sum_of_txn_times) AS total_txn_times
FROM cleaned_origin_destination
GROUP BY district_origin, on_stop, district_destination, off_stop
ORDER BY total_txn_times DESC

-- overallUsage
SELECT 
    sarea, 
    AVG(latitude) AS latitude, 
    AVG(longitude) AS longitude, 
    ROUND(SUM(available_return_bikes) * 1.0 / SUM(total), 2) AS usage_ratio
FROM cleaned_youbike
WHERE mday >= '2024-09-08' AND mday < '2024-09-15'
GROUP BY sarea

-- specificUsage
SELECT 
    sarea, 
    AVG(latitude) AS latitude, 
    AVG(longitude) AS longitude, 
    ROUND(SUM(available_return_bikes) * 1.0 / SUM(total), 2) AS usage_ratio
FROM cleaned_youbike
WHERE mday = '{selected_date}'
GROUP BY sarea

-- overallDailyUsage
SELECT mday,
    ROUND(SUM(available_return_bikes) * 1.0 / SUM(total), 2) AS usage_ratio
FROM cleaned_youbike
WHERE mday >= '2024-09-08' AND mday < '2024-09-15'
GROUP BY mday
ORDER BY mday

-- specificRegionDailyUsage
SELECT mday,
    ROUND(SUM(available_return_bikes) * 1.0 / SUM(total), 2) AS usage_ratio
FROM cleaned_youbike
WHERE sarea = '{selected_region}' AND mday >= '2024-09-08' AND mday < '2024-09-15'
GROUP BY mday
ORDER BY mday

-- overallHourlyUsage
SELECT 
    strftime('%H:00', infoTime) AS infoHour,
    ROUND(SUM(available_return_bikes) * 1.0 / SUM(total), 2) AS usage_ratio
FROM cleaned_youbike
WHERE mday = '{selected_date}'
GROUP BY strftime('%H:00', infoTime)
ORDER BY infoHour

-- specificDateHourlyUsage
SELECT 
    strftime('%H:00', infoTime) AS infoHour,
    ROUND(SUM(available_return_bikes) * 1.0 / SUM(total), 2) AS usage_ratio
FROM cleaned_youbike
WHERE sarea = '{selected_region}' AND mday = '{selected_date}'
GROUP BY strftime('%H:00', infoTime)
ORDER BY infoHour