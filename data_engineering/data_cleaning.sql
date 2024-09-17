CREATE TABLE cleaned_youbike AS
	SELECT 
		sno,
		replace(sna, 'YouBike2.0_', '') AS sna,
		sarea,
		DATE(mday) AS mday,
		ar,
		sareaen,
		snaen,
		aren,
		CAST(act AS NUMERIC) AS act,
		DATETIME(srcUpdateTime) AS srcUpdateTime,
		DATETIME(updateTime) AS updateTime,
		DATETIME(infoTime) AS infoTime,
		DATE(infoDate) AS infoDate,
		CAST(total AS NUMERIC) AS total,
		CAST(available_rent_bikes AS NUMERIC) AS available_rent_bikes,
		CAST(latitude AS NUMERIC) AS latitude,
		CAST(longitude AS NUMERIC) AS longitude,
		CAST(available_return_bikes AS NUMERIC) AS available_return_bikes,
		DATETIME(timestamp) AS timestamp
	FROM youbike;

CREATE TABLE cleaned_density_by_district AS
	SELECT 
		DATE('2024-07-31') AS date,
		district,
		CAST(area AS NUMERIC) AS area,
		CAST(actual_townships AS NUMERIC) AS actual_townships,
		CAST(registered_townships AS NUMERIC) AS registered_townships,
		CAST(actual_neighbors AS NUMERIC) AS actual_neighbors,
		CAST(registered_neighbors AS NUMERIC) AS registered_neighbors,
		CAST(households AS NUMERIC) AS households,
		CAST(total_population AS NUMERIC) AS total_population,
		CAST(male_population AS NUMERIC) AS male_population,
		CAST(female_population AS NUMERIC) AS female_population,
		CAST(sextual_ratio AS NUMERIC) AS sextual_ratio,
		CAST(household_size AS NUMERIC) AS household_size,
		CAST(population_density AS NUMERIC) AS population_density
	FROM density_by_district
	WHERE date = '113年 7月底' AND district != '總計'

CREATE TABLE cleaned_visibility_rate AS 
	SELECT 
		stop_id,
		stop_name,
		CAST(capacity AS NUMERIC) AS capacity,
		CAST(latitude AS NUMERIC) AS latitude,
		CAST(longitude AS NUMERIC) AS longitude,
		category
	FROM visibility_rate

CREATE TABLE cleaned_origin_destination AS 
	SELECT 
		on_stop_id,
		off_stop_id,
		on_stop,
		off_stop,
		CAST(sum_of_txn_times AS NUMERIC) AS sum_of_txn_times,
		district_origin,
		district_destination,
		CAST(width AS NUMERIC) AS width
	FROM origin_destination