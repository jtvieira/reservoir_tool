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

def create_df(res):
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
    query = f'''SELECT date, avg_temp, precip, storage, elevation FROM {res};'''
    cursor.execute(query)
    data = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    
    df = pd.DataFrame(data, columns=['Date', 'Avg Temp', 'Precip', 'Storage', 'Elevation'])
    return df

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
    df = create_df(res)
    return get_plot(df)