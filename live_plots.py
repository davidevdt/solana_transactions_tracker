import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
from plot_utils import PlotUtils
from SolanaChainExplorer import SolanaChainExplorer
import plotly.graph_objects as go
from pathlib import Path
import threading
import time

app = dash.Dash(__name__)

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
                    starting_slot_number = int(solana_chain.get_latest_slot_number() - 11E4)
                    solana_chain.explore_chain(starting_slot_number, True, True, True)
                    solana_chain.store_chain_to_csv(str(file_path))
            else: 
                solana_chain.update_chain(True, str(file_path))
            df = solana_chain.get_df()
        time.sleep(20)

def print_block_information(): 

    text_style = {'textAlign': 'center', 'marginTop': '20px'}
    div_style = {'padding': '20px', 'border': '1px solid #ddd', 'borderRadius': '5px'}
    
    with lock: 
        if df is None: 
            return html.Div([
                html.H3("Data is loading...", style=text_style),
                html.H3("", style=text_style),
                html.H3("", style=text_style), 
            ], style = div_style)
        else: 
            return html.Div([
                html.H3(f"Last examined block: {int(df['Max_Slot_Number'].max())}", style=text_style), 
                html.H3(f"Last validated block: {solana_chain.get_latest_slot_number()}", style=text_style), 
                html.H3(f"Next block to analyze: {int(df['Max_Slot_Number'].max()) + solana_chain.jump}", style=text_style)
            ], style = div_style)

app.layout = html.Div([
    html.H1("Solana Transactions Tracker", style={'marginBottom': '80px', 'textAlign': 'center', 'size': '40px'}),
    dcc.Graph(id='StatusGraph', style={'marginBottom': '100px'}),
    dcc.Graph(id='SuccessTypeGraph', style={'marginBottom': '50px'}),
    html.Div(id='text-section'),
    dcc.Interval(
        id='interval-component',
        interval=5*1000,
        n_intervals=0
    )
])


@app.callback(
    Output('StatusGraph', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_status_graph(n):
    if df is not None and not df.empty:
        return PlotUtils.bar_chart_dash(df, 'status', True, "Transactions' Status")

@app.callback(
    Output('SuccessTypeGraph', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_type_graph(n):
    if df is not None and not df.empty:
        return PlotUtils.bar_chart_dash(df, 'success_type', True, "Transactions' Type", True)

@app.callback(
    Output('text-section', 'children'),
    Input('interval-component', 'n_intervals')
)
def update_text_section(n):
    return print_block_information()


# Run the Dash app
if __name__ == '__main__':
    thread = threading.Thread(target=update_chain_data, daemon=True)
    thread.start()
    app.run_server(debug=True, use_reloader=False)

    
