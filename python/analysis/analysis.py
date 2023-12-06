import pandas as pd
import psycopg2
from sklearn.svm import SVR
from sklearn.preprocessing import MinMaxScaler
import numpy as np
import trainModels
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

train_start_dt = '2010-01-01'
test_start_dt = '2023-01-01'



def write_results_to_db(df, reservoir):
    load_dotenv()
    db_params = {
        'user': os.getenv('USER'),
        "host": os.getenv('HOST'),
        "dbname": os.getenv('DB_NAME'),
        "port": os.getenv('PORT'),
        'password': os.getenv('PASSWORD')
    }
    connection_parts = ["postgresql://"]

    if db_params["user"]:
        connection_parts.append(db_params["user"])
        if db_params["password"]:
            connection_parts.append(f":{db_params['password']}")
        connection_parts.append("@")

    host_part = db_params["host"] if db_params["host"] else "localhost"
    connection_parts.append(f"{host_part}:{db_params['port']}")

    connection_parts.append(f"/{db_params['dbname']}")

    connection_string = "".join(connection_parts)

    # Create the engine
    engine = create_engine(connection_string)

    df.to_sql(f'{reservoir}_results', engine, index=False, if_exists='replace')


def get_data(res):
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
    query = f"SELECT * FROM {res};"

    cursor.execute(query)
    data = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    df = pd.DataFrame(data, columns=['id','Date', 'Avg_Temp', 'Precip', 'Storage', 'Elevation'])
    df = df.drop('id', axis=1)
    df['Date'] = pd.to_datetime(df['Date'])
    df.index = df['Date']
    df = df.reindex(pd.date_range(min(df['Date']),
                                            max(df['Date']),
                                            freq='D'))
    df = df.drop('Date', axis=1)
    return df

def add_14_days_data(df, reservoir):
    if reservoir == 'havasu':
        df = df.dropna(axis=1) # in the case of havasu, the elevation column is all NaN so we drop that column

    for i in range(1, 15):
        df[f'd - {i}'] = df['Storage'].shift(i)
    if reservoir == 'mohave':
        numeric_columns = ['Avg_Temp', 'Precip', 'Storage', 'Elevation'] + [f'd - {i}' for i in range(1, 15)]
    if reservoir == 'havasu':
        numeric_columns = ['Avg_Temp', 'Precip', 'Storage'] + [f'd - {i}' for i in range(1, 15)]

    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')
    df = df.dropna() #drop the rows with NaN
    return df

def generate_train_and_test_sets(df):
    train = df.copy()[(df.index >= train_start_dt) & (df.index < test_start_dt)]
    test = df.copy()[df.index >= test_start_dt]
    return split_to_x_and_y(train, test)

def split_to_x_and_y(train, test):
    X_train = train.drop('Storage', axis=1)
    X_test = test.drop('Storage', axis=1)

    y_train = train['Storage']
    y_test = test['Storage']
    return X_train, y_train, X_test, y_test

def process_data(X_train, y_train, X_test, y_test, reservoir):
    x_scaler = MinMaxScaler()
    y_scaler = MinMaxScaler()

    X_test_values = X_test.values
    X_test_values = x_scaler.fit_transform(X_test_values)

    X_train_values = X_train.values
    X_train_values = x_scaler.fit_transform(X_train_values)

    y_train_values = y_train.values.reshape(-1, 1)
    y_train_values = y_scaler.fit_transform(y_train_values)

    y_test_values = y_test.values.reshape(-1, 1)
    # y_test_values = y_scaler.fit_transform(y_test_values)

    results = trainModels.train(X_train_values, y_train_values, X_test_values)
    for k, _ in results.items():
        results[k] = y_scaler.inverse_transform(results[k])
    results['test'] = y_test_values
    df = pd.DataFrame({k: v.flatten() for k, v in results.items()})
    write_results_to_db(df, reservoir)

def main(reservoir):
    df = get_data(reservoir)
    df = add_14_days_data(df, reservoir)
    X_train, y_train, X_test, y_test = generate_train_and_test_sets(df)
    process_data(X_train, y_train, X_test, y_test, reservoir)
    # print(test.head())
    # print(df.head())
    # print(train_start_dt)

if __name__ == '__main__':
    reservoirs = ['havasu', 'mohave']
    for res in reservoirs:
        print(f'analyzing data for {res}')
        main(res)