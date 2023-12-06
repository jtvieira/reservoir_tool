
from sklearn.metrics import mean_absolute_percentage_error as MAPE
from sklearn.metrics import mean_absolute_error as MAE
import pandas as pd
import psycopg2
import plotly.graph_objects as go
import plotly.offline as pyo
from datetime import datetime, timedelta

db_params = {
    "dbname": 'postgres',
    "port": '5432',
}
# print('MAPE for test data: ', mape(y_test_pred, y_test_values)*100, '%')
# print('MAPE for training data: ', mape(y_train_pred, y_train_values)*100, '%')
# print('MAE for test data: ', mae(y_test_pred, y_test_values))
# print('MAE for training data: ', mae(y_train_pred, y_train_values))

def get_data(df, col):
    pred = df[col].values
    test = df['test'].values
    return test, pred

def generate_plot(df, col):
    test, pred = get_data(df, col)
    start_date = datetime(2023, 1, 1)  # January 1, 2023
    end_date = datetime(2023, 10, 31)   # December 31, 2023
    date_list = [start_date + timedelta(days=x) for x in range((end_date - start_date).days + 1)]

    fig = go.Figure()

    # Add the actual data plot
    fig.add_trace(go.Scatter(x=date_list, y=test,
                            mode='lines',
                            name='Actual',
                            line=dict(color='red', width=2),
                            opacity=0.6))

    # Add the predicted data plot
    fig.add_trace(go.Scatter(x=date_list, y=pred,
                            mode='lines',
                            name='Predicted',
                            line=dict(color='blue', width=0.8)))

    # Update layout
    fig.update_layout(
        title='Actual vs Predicted',
        xaxis_title='Timestamp',
        yaxis_title='Values',
        legend_title='Legend',
        width=1000,  # Width in pixels
        height=500   # Height in pixels
    )

    mape = MAPE(pred, test)*100
    mae = MAE(pred, test)
    annotations = [
    dict(xref='paper', x=0, y=20,
         xanchor='left', yanchor='bottom',
         text=f'MAPE Test: {mape}%',
         font=dict(family='Arial', size=12),
         showarrow=False),
    dict(xref='paper', x=0.05, y=0.1,   # Adjust position as needed
         xanchor='left', yanchor='top',
         text=f'MAE Test: {mae}',
         font=dict(family='Arial', size=12),
         showarrow=False),
    ]

    fig.update_layout(annotations=annotations)  
    # Show the figure
    # pyo.iplot(fig)
    # fig.show()
    return pyo.plot(fig, output_type='div')

def get_df(res):
    table = f'{res}_results'
    conn = psycopg2.connect(**db_params)
    query = F'''SELECT * FROM {table};'''
    df = pd.read_sql(query, conn)
    conn.close()
    # print(df.head())
    # generate_plot(df, 'gaussian')
    return df

def return_plots(res):
    df = get_df(res)
    plots = []

    algs = ['svr', 'kneighbors', 'neural_net', 'decision_tree', 'random_forest', 'gaussian']
    for alg in algs:
        plot = generate_plot(df, alg)
        plots.append(plot)
    return plots