import psycopg2
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
import os

db_params = {
    # "dbname": os.getenv('DB_NAME'),
    # "host": os.getenv('HOST'),
    # "port": os.getenv('PORT'),
    "dbname": 'postgres',
    # "host": 'postgres',
    "port": '5432',
}


def get_dfs(state):
    url_meta = f"https://waterservices.usgs.gov/nwis/site/?format=rdb&stateCd={state}&parameterCd=00054&siteStatus=active"
    url_data = f"https://waterservices.usgs.gov/nwis/dv/?format=rdb&stateCd={state}&startDT=2010-01-01&endDT={datetime.now().date()}&parameterCd=00054&siteStatus=active"
    url_data_el = f"https://waterservices.usgs.gov/nwis/dv/?format=rdb&stateCd={state}&startDT=2010-01-01&endDT={datetime.now().date()}&parameterCd=62614&siteStatus=active"
    df_meta = pd.read_csv(url_meta, on_bad_lines='skip', comment="#", delimiter="\t", header=0)
    df_data = pd.read_csv(url_data, on_bad_lines='skip', comment="#", delimiter="\t", header=0)
    df_meta = df_meta.drop(0)
    df_data = df_data.drop(0)

    df_data_el = pd.read_csv(url_data_el, on_bad_lines='skip', comment="#", delimiter="\t", header=0)
    df_data_el = df_data_el.drop(0)

    el = [col for col in df_data_el.columns if '62614' in col]
    df_data_el = df_data_el.rename(columns={el[0]: 'elevation'})
    df_data_el = df_data_el[['site_no', 'datetime', 'elevation']]

    st = [col for col in df_data.columns if '00054' in col]
    if st:
        df_data = df_data.rename(columns={st[0]: 'storage'})

    df_data = df_data.drop(st[1], axis=1)

    df_data_el = df_data_el[~(df_data_el['elevation'].str.contains('62614') | (df_data_el['elevation'] == '14n'))]
    df_data = df_data[~(df_data['storage'].str.contains('00054') | (df_data['storage'] == '14n'))]
    merged_data_df = pd.merge(df_data, df_data_el, on=['site_no', 'datetime'], how='left')
    
    
    return df_meta, merged_data_df

def drop_table(table_name):
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()
    drop_query = f"DROP TABLE IF EXISTS {table_name};"

    cursor.execute(drop_query)
    conn.commit()
    cursor.close()
    conn.close()

def insert_meta(df):
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    table_name = "res_meta"

    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        id SERIAL PRIMARY KEY,
        agency_cd VARCHAR(10),
        site_no VARCHAR(15) UNIQUE,
        station_nm VARCHAR(255),
        site_tp_cd VARCHAR(10),
        dec_lat_va DOUBLE PRECISION,
        dec_long_va DOUBLE PRECISION,
        coord_acy_cd VARCHAR(5),
        dec_coord_datum_cd VARCHAR(10),
        alt_va DOUBLE PRECISION,
        alt_acy_va DOUBLE PRECISION,
        alt_datum_cd VARCHAR(10),
        huc_cd VARCHAR(16)
    );
    """

    # Execute the CREATE TABLE statement
    cursor.execute(create_table_query)

    insert_query = f"""
                    INSERT INTO {table_name} (agency_cd, site_no, station_nm, site_tp_cd, dec_lat_va, dec_long_va, coord_acy_cd, dec_coord_datum_cd, alt_va, alt_acy_va, alt_datum_cd, huc_cd)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
                    """

    for row in df.itertuples(index=False, name=None):
        cursor.execute(insert_query, row)
    # Commit the transaction
    conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()


def insert_data(df):
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    table_name = "res_data"
    create_table_query = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        id SERIAL PRIMARY KEY,
        agency_cd VARCHAR(50),
        site_no VARCHAR(15) REFERENCES res_meta(site_no),
        datetime DATE,
        storage DOUBLE PRECISION,
        elevation DECIMAL(10, 2)
    );
    """
    cursor.execute(create_table_query)

    insert_query = f"""
    INSERT INTO {table_name} (agency_cd, site_no, datetime, storage, elevation)
    VALUES (%s, %s, %s, %s, %s);
    """

    date_format = "%Y-%m-%d"
    for row in df.itertuples(index=False, name=None):
        # Skip the row if the 'datetime' value is not a valid date string
        try:
            # Try to convert the 'datetime' value to a date object
            datetime.strptime(row[2], date_format)
        except ValueError:
            continue  # Skip to the next row if the conversion fails
        
        # Check if value_00054 is a number
        try:
            float(row[3])
        except ValueError:
            continue  # Skip to the next row if the conversion fails
        
        # Execute the insert query
        cursor.execute(insert_query, row)
    
    conn.commit()

    cursor.close()
    conn.close()

def main():
    states = ["az", "ca", "nm"]
    drop_table("res_data")
    drop_table("res_meta")
    for state in states:
        df_meta, df_data = get_dfs(state)
        insert_meta(df_meta)
        insert_data(df_data)


if __name__ == "__main__":
    main()
