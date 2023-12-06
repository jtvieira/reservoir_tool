import requests
import json
import pandas as pd
import psycopg2
from dotenv import load_dotenv
import os


# mohave lat = 35.19722105
# mohave lon = -114.5694098

# havasu lon = -114.1571702
# havasu lat = 34.31612564


# This makes a call to an external api that gets the historical data
def get_climate_data_at_lon_lat(lon, lat, edate):

    params = {"loc":"{}, {}\t".format(lon,lat),"grid":"21","elems":[{"name":"avgt","interval":"dly","duration":"dly"},{"name":"pcpn","interval":"dly","duration":"dly"}],"sdate":"20100101","edate":f"{edate}"}
    url = 'https://data.rcc-acis.org/GridData'
    data = requests.post(url, data=json.dumps(params), headers={'content-type': 'application/json'}, timeout=60)
    return data.json()


def get_clim_df(lon, lat, edate):

    data = get_climate_data_at_lon_lat(lon, lat, edate)
    res = data['data']    
    return pd.DataFrame(res, columns=['Date', 'Avg Temp', 'Precip'])

def get_storage_and_elevation_df_from_siteno(site_no):
    load_dotenv()
    db_params = {
        'user': os.getenv('USER'),
        "host": os.getenv('HOST'),
        "dbname": os.getenv('DB_NAME'),
        "port": os.getenv('PORT'),
        'password': os.getenv('PASSWORD')
    }
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    query = f"SELECT datetime, storage, elevation FROM res_data WHERE site_no LIKE '{site_no}';"

    cursor.execute(query)
    data = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return pd.DataFrame(data, columns=['Date', 'Storage', 'Elevation'])

def merge_data(storage_df, clim_df):
    clim_df['Date'] = pd.to_datetime(clim_df['Date'])
    storage_df['Date'] = pd.to_datetime(storage_df['Date'])
    return pd.merge(clim_df, storage_df, on='Date', how='inner')

def write_to_db(name, df):
    load_dotenv()
    db_params = {
        'user': os.getenv('USER'),
        "host": os.getenv('HOST'),
        "dbname": os.getenv('DB_NAME'),
        "port": os.getenv('PORT'),
        'password': os.getenv('PASSWORD')
    }
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    create_table_query = f'''
        CREATE TABLE IF NOT EXISTS {name} (
            id SERIAL,
            Date DATE,
            Avg_Temp DECIMAL(5, 2),
            Precip DECIMAL(5, 2),
            Storage DECIMAL(10, 2),
            Elevation DECIMAL(10, 2) NULL
        );
    '''
    cursor.execute(create_table_query)

    insert_query = f'''
        INSERT INTO {name} (Date, Avg_Temp, Precip, Storage, Elevation)
        VALUES (%s, %s, %s, %s, %s)
    '''
    for row in df.itertuples(index=False, name=None):
        cursor.execute(insert_query, row)
    # Commit the transaction
    conn.commit()

    cursor.close()
    conn.close()

def create_df(lon, lat, site_no, edate):
    clim_df = get_clim_df(lon, lat, edate)
    storage_df = get_storage_and_elevation_df_from_siteno(site_no)
    return merge_data(storage_df, clim_df)

def drop_table(table_name):
    load_dotenv()
    db_params = {
        'user': os.getenv('USER'),
        "host": os.getenv('HOST'),
        "dbname": os.getenv('DB_NAME'),
        "port": os.getenv('PORT'),
        'password': os.getenv('PASSWORD')
    }
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    drop_query = f"DROP TABLE IF EXISTS {table_name};"

    cursor.execute(drop_query)
    conn.commit()
    cursor.close()
    conn.close()

def main():
    #index 0 for everything is lake mohave
    #index 1 for everything is lake havasu
    site_meta_data = {
        'names'         : ['mohave', 'havasu'],
        "longitudes"    : [-114.5694098, -114.1571702],
        "latitudes"     : [35.19722105, 34.31612564],
        'site_no'       : ['09422500', '09427500']  
    }
    edate = '20231031'
    for i in range(0,2):
        df = create_df(site_meta_data['longitudes'][i], site_meta_data['latitudes'][i], site_meta_data['site_no'][i], edate)
        print(df.head())
        drop_table(site_meta_data['names'][i]) #Don't want duplicate data every time we ingest. We will just drop the table every time we gather the data
        write_to_db(site_meta_data['names'][i], df)

if __name__ == '__main__':
    main()