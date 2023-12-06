import requests
import json
import pandas as pd
import psycopg2
import plotly_express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.offline as pyo
from dotenv import load_dotenv
import os


def create_df(lon, lat, site_no, edate):
    clim_df = get_clim_df(lon, lat, edate)
    storage_df = get_storage_and_elevation_df_from_siteno(site_no)
    return merge_data(storage_df, clim_df)

def get_clim_df(lon, lat, edate):

    data = get_climate_data_at_lon_lat(lon, lat, edate)
    res = data['data']    
    return pd.DataFrame(res, columns=['Date', 'Avg Temp', 'Precip'])

def get_climate_data_at_lon_lat(lon, lat, edate):

    params = {"loc":"{}, {}\t".format(lon,lat),"grid":"21","elems":[{"name":"avgt","interval":"dly","duration":"dly"},{"name":"pcpn","interval":"dly","duration":"dly"}],"sdate":"20100101","edate":f"{edate}"}
    url = 'https://data.rcc-acis.org/GridData'
    data = requests.post(url, data=json.dumps(params), headers={'content-type': 'application/json'}, timeout=60)
    return data.json()


def merge_data(storage_df, clim_df):
    clim_df['Date'] = pd.to_datetime(clim_df['Date'])
    storage_df['Date'] = pd.to_datetime(storage_df['Date'])
    return pd.merge(clim_df, storage_df, on='Date', how='inner')

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


def get_havasu_real_time():
    df = create_df(-114.1571702, 34.31612564, '09427500', '20231201')
    return get_plot(df)

def get_mohave_real_time():
    df = create_df(-114.5694098, 35.19722105, '09422500', '20231201')
    return get_plot(df)

def get_plot(df):

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(
        go.Scatter(x=df['Date'], y=df['Storage'], name='Storage'),
        secondary_y=False,
    )

    fig.add_trace(
        go.Scatter(x=df['Date'], y=df['Avg Temp'], name='Temperature'),
        secondary_y=True,
    )

    fig.update_layout(
        title_text="Storage and Temperature Over Time"
    )

    fig.update_xaxes(title_text="Date")

    fig.update_yaxes(title_text="Storage", secondary_y=False)
    fig.update_yaxes(title_text="Temperature", secondary_y=True)
    
    return pyo.plot(fig, output_type='div')

def return_plot(res):
    if res == 'mohave':
        return get_mohave_real_time()
    if res == 'havasu':
        return get_havasu_real_time()
    