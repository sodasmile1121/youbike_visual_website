import requests
import pandas as pd
import geopandas as gpd
from sqlalchemy import create_engine
from datetime import datetime
import time

def fetch_data():
    url = "https://tcgbusfs.blob.core.windows.net/dotapp/youbike/v2/youbike_immediate.json"
    try:
        response = requests.get(url)
        response.raise_for_status() 
        data = response.json()
        return pd.DataFrame(data)
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return pd.DataFrame()  

def read_from_csv(csv_path):
    try:
        df = pd.read_csv(csv_path)
        return df
    except FileNotFoundError as e:
        print(f"CSV file not found: {e}")
        return pd.DataFrame()
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return pd.DataFrame()
    
def read_geojson(file_path):
    try:
        gdf = gpd.read_file(file_path)
        return gdf
    except Exception as e:
        print(f"Error reading geojson file: {e}")
        return None

def save_to_db(df, ds_file):
    if not df.empty: 
        engine = create_engine(f'sqlite:///ubike.db')
        try:
            df.to_sql(ds_file, engine, if_exists='append', index=False)
        except Exception as e:
            print(f"Error saving data to database: {e}")

def main():
    # Fetch Real-Time Data
    '''
    while True:
        realtime = fetch_data()
        if not realtime.empty:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            realtime['timestamp'] = timestamp
            save_to_db(realtime, 'youbike')
            print(f"Data saved at {timestamp}")
        else:
            print("No data to save.")
        time.sleep(300)
    '''

    # Upload CSV Data
    '''
    density = read_from_csv('./data/district_density.csv')
    density.columns = ['date', 'district', 'area', 'actual_townships', 'registered_townships', 'actual_neighbors', 'registered_neighbors', 'households', 'total_population', 'male_population', 'female_population', 'sextual_ratio', 'household_size', 'population_density']
    save_to_db(density, 'density_by_district')
    '''

    # Upload GeoJson Data
    '''
    origin_destination = read_geojson('./data/origin_destination_statistics.geojson')
    print(len(origin_destination))
    if 'geometry' in origin_destination.columns:
        origin_destination = origin_destination.drop(['geometry'], axis=1)
    save_to_db(origin_destination, 'origin_destination')

    visibility_rate = read_geojson('./data/visibility_rate.geojson')
    print(len(visibility_rate))
    if 'geometry' in visibility_rate.columns:
        visibility_rate = visibility_rate.drop(['geometry'], axis=1)
    save_to_db(visibility_rate, 'visibility_rate')
    '''

if __name__ == '__main__':
    main()




