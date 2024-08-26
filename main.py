"""
Main Application for Solana Transactions Dashboard

Author: Davide Vidotto
Date: August 2024
Version: 1.0

Description:
This application is a real-time dashboard for monitoring and visualizing Solana blockchain transactions. Utilizing Dash by Plotly, it provides interactive graphs and status updates on the latest blockchain activity.

Key Features:
- Displays real-time charts for transaction statuses and types.
- Retrieves and updates Solana blockchain data periodically.
- Visualizations are updated automatically every few seconds.

Components:
- `update_chain_data()`: Function running in a separate thread to periodically update the transaction data from the Solana blockchain and store it in a CSV file.
- Dash components:
  - `html.H1`: Main title of the dashboard.
  - `dcc.Graph`: Displays charts for transaction statuses and types.
  - `dcc.Interval`: Periodically triggers updates to the graphs and text section.
- Callbacks:
  - `update_text_section()`: Updates the text section with the latest block information.
  - `update_status_graph()`: Updates the status chart with transaction status data.
  - `update_type_graph()`: Updates the type chart with transaction success types data.

Dependencies:
- Dash for creating the web application interface.
- Plotly for generating interactive graphs.
- pandas for data manipulation.
- threading for concurrent data updates.

"""

import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from PlotUtils import PlotUtils
from SolanaChainExplorer import SolanaChainExplorer
import plotly.graph_objects as go
from pathlib import Path
import threading
import time

MAX_OBSERVATIONS_TO_PLOT = 25

lock = threading.Lock()
df = None
file_path = Path('./data/chain.csv')
solana_chain = SolanaChainExplorer()
solana_chain.import_settings_from_json('./explorer_settings.json')

def update_chain_data():
    global df 
    while True: 
        with lock:
            if solana_chain.get_df() is None: 
                if file_path.exists():
                    solana_chain.load_chain_from_csv(str(file_path))
                else:
                    starting_slot_number = int(solana_chain.get_latest_slot_number() - \
                        (solana_chain.n_batches_to_explore * solana_chain.jump))
                    solana_chain.explore_chain(starting_slot_number, True, True, True)
                    solana_chain.store_chain_to_csv(str(file_path))
            else: 
                solana_chain.update_chain(True, str(file_path))
            df = solana_chain.get_df()
        time.sleep(20)

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Solana Transactions Tracker", style={'marginBottom': '80px', 'textAlign': 'center', 'size': '40px'}),
        html.Div(id='block-info-section'),
    dcc.Graph(id='status-chart', style={'marginBottom': '100px'}),
    dcc.Graph(id='success-type-chart', style={'marginBottom': '50px'}),
    
    dcc.Interval(
        id='interval-component',
        interval=5*1000,
        n_intervals=0
    )
])

@app.callback(
    Output('block-info-section', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_text_section(n):
    global df 

    text_style = {'textAlign': 'center', 'marginTop': '20px'}
    div_style = {'padding': '20px', 'border': '1px solid #ddd', 'borderRadius': '5px', 'marginBottom': '50px'}
    
    if df is None: 
        return html.Div([
            html.H3("Fetching data from Solana RPC endpoint...", style=text_style),
            html.H3("", style=text_style),
            html.H3("", style=text_style), 
        ], style = div_style)
    else: 
        return html.Div([
            html.H3(f"Last examined block: {int(df['Max_Slot_Number'].max())}", style=text_style), 
            html.H3(f"Last validated block: {solana_chain.get_latest_slot_number()}", style=text_style), 
            html.H3(f"Next block to analyze: {int(df['Max_Slot_Number'].max()) + solana_chain.jump}", style=text_style)
        ], style = div_style)

@app.callback(
    Output('status-chart', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_status_graph(n):
    global df 
    with lock: 
        if df is not None and not df.empty:
            return PlotUtils.bar_chart_dash(df[-MAX_OBSERVATIONS_TO_PLOT:], 'status', True, "Transactions' Status")
        else: 
            return PlotUtils.empty_figure()

@app.callback(
    Output('success-type-chart', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_type_graph(n):
    global df 
    with lock:
        if df is not None and not df.empty:
            return PlotUtils.bar_chart_dash(df[-MAX_OBSERVATIONS_TO_PLOT:], 'success_type', True, "Transactions' Type", True)
        else: 
            return PlotUtils.empty_figure()

if __name__ == '__main__':
    thread = threading.Thread(target=update_chain_data, daemon=True)
    thread.start()
    app.run_server(debug=True, use_reloader=False)
