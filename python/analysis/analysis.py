import pandas as pd
import psycopg2
from sklearn.svm import SVR
from sklearn.preprocessing import MinMaxScaler

reservoir = ''
train_start_dt = '2010-01-01'
test_start_dt = '2023-01-01'

def get_data(res):
    global reservoir
    reservoir = res
    db_params = {
        "dbname": 'postgres',
        "port": '5432',
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

def add_14_days_data(df):
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

def process_data(X_train, y_train, X_test, y_test):
    x_scaler = MinMaxScaler()
    y_scaler = MinMaxScaler()

def main():
    df = get_data('mohave')
    df = add_14_days_data(df)
    X_train, y_train, X_test, y_test = generate_train_and_test_sets(df)
    print(test.head())
    # print(df.head())
    # print(train_start_dt)

main()