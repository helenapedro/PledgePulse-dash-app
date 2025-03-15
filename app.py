# app.py
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go  # Import here
import plotly.express as px

from data_processing import load_and_preprocess_data, create_visualizations


app = dash.Dash(__name__)
server = app.server

# Load and preprocess data (make sure 'df' is accessible here)
pledges_file = 'https://storage.googleapis.com/plotly-app-challenge/one-for-the-world-pledges.json'
payments_file = 'https://storage.googleapis.com/plotly-app-challenge/one-for-the-world-payments.json'
df = load_and_preprocess_data(pledges_file, payments_file)

# Create visualizations
figures = create_visualizations(df)

app.layout = html.Div([
    html.H1("One For The World Pledges and Payments Dashboard"),

    # Filters (Example: Year Filter)
    html.Div([
        html.Label("Select Year:"),
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': str(year), 'value': year} for year in sorted(df['year'].unique())],
            multi=True,  # Allow multiple selections
            value=sorted(df['year'].unique()) # Default selection: all years
        ),
    ], style={'width': '48%', 'display': 'inline-block'}), # Style to put dropdown inline

    # First Row of Graphs
    html.Div([
        dcc.Graph(id='pledge-trend-graph', figure=figures['pledge_trend']),
    ], style={'width': '48%', 'display': 'inline-block'}),
    html.Div([
        dcc.Graph(id='pledge-distribution-graph', figure=figures['pledge_distribution']),
    ], style={'width': '48%', 'display': 'inline-block'}),

    # Second Row of Graphs
    html.Div([
        dcc.Graph(id='fulfillment-rate-graph', figure=figures['fulfillment_rate']),
    ], style={'width': '48%', 'display': 'inline-block'}),
    html.Div([
        dcc.Graph(id='pledge-payment-scatter-graph', figure=figures['pledge_payment_scatter']),
    ], style={'width': '48%', 'display': 'inline-block'}),

    # By Year Plot
    html.Div([
        dcc.Graph(id='pledges-by-year-graph', figure=figures['by_year']),
    ], style={'width': '48%', 'display': 'inline-block'}),

    # Combined Metrics Plot
    html.Div([
        dcc.Graph(id='combined-metrics-graph', figure=figures['subplots']),
    ], style={'width': '96%', 'display': 'inline-block'}),

    # Table (Example - Pledge Summary)
    html.Div([
        html.H2("Pledge Summary Table"),
        dash.dash_table.DataTable(
            id='pledge-summary-table',
            columns=[{"name": i, "id": i} for i in ['year', 'total_pledge_amount', 'average_pledge_amount']],
            data=[],
            style_cell={'textAlign': 'left'},
            style_header={
                'backgroundColor': 'rgb(230, 230, 230)',
                'fontWeight': 'bold'
            }
        )
    ]),

    # LLM Interface (Placeholder)
    html.Div([
        html.H2("Ask a Question About the Data (LLM Placeholder)"),
        dcc.Input(id='llm-input', type='text', placeholder='Enter your question'),
        html.Button('Submit', id='llm-button', n_clicks=0),
        html.Div(id='llm-output')
    ])
])


# --- Callbacks ---

# Year Filter Callback
@app.callback(
    [Output('pledge-trend-graph', 'figure'),
     Output('pledge-distribution-graph', 'figure'),
     Output('fulfillment-rate-graph', 'figure'),
     Output('pledge-payment-scatter-graph', 'figure'),
     Output('pledges-by-year-graph', 'figure'),
     Output('pledge-summary-table', 'data')], # Update all graphs and the table
    [Input('year-dropdown', 'value')]
)
def update_graphs(selected_years):
    """Updates graphs based on selected years."""

    # Filter the dataframe based on the selected years
    filtered_df = df[df['year'].isin(selected_years)]

    # Recreate visualizations with the filtered data
    filtered_figures = create_visualizations(filtered_df)

    # Create pledge summary data for the table
    pledge_summary = filtered_df.groupby('year')['contribution_amount'].agg(['sum', 'mean']).reset_index() #Changed here
    pledge_summary.columns = ['year', 'total_pledge_amount', 'average_pledge_amount']
    table_data = pledge_summary.to_dict('records')


    return filtered_figures['pledge_trend'], \
           filtered_figures['pledge_distribution'], \
           filtered_figures['fulfillment_rate'], \
           filtered_figures['pledge_payment_scatter'], \
           filtered_figures['by_year'], \
           table_data


# LLM Callback (Placeholder - To be implemented with an actual LLM)
@app.callback(
    Output('llm-output', 'children'),
    [Input('llm-button', 'n_clicks')],
    [dash.dependencies.State('llm-input', 'value')]
)
def process_llm_input(n_clicks, user_input):
    """Placeholder for LLM interaction."""
    if n_clicks > 0:
        # Replace with actual LLM integration
        return f"You asked: {user_input}.  (LLM integration pending)"
    return ""

if __name__ == '__main__':
    app.run_server(debug=True)