import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go  # Import here
import plotly.express as px
import dash_ag_grid as dag  # Import dash_ag_grid
import dash_bootstrap_components as dbc  # Import Bootstrap components

from data_processing import load_and_preprocess_data, create_visualizations


# Initialize the Dash app with Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP],
                meta_tags=[{'name': 'viewport',
                            'content': 'width=device-width, initial-scale=1.0'}])
server = app.server

# Load and preprocess data (make sure 'df' is accessible here)
pledges_file = 'https://storage.googleapis.com/plotly-app-challenge/one-for-the-world-pledges.json'
payments_file = 'https://storage.googleapis.com/plotly-app-challenge/one-for-the-world-payments.json'
df = load_and_preprocess_data(pledges_file, payments_file)

# Create visualizations
figures = create_visualizations(df)


# App layout using Bootstrap components
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("One For The World Pledges and Payments Dashboard", className="text-center mb-4"), width=12),
    ]),

    dbc.Row([
        dbc.Col([
            html.Label("Select Year:"),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': str(year), 'value': year} for year in sorted(df['year'].unique())],
                multi=True,  # Allow multiple selections
                value=sorted(df['year'].unique()),
                className="mb-3"  # Add margin bottom for spacing
            ),
        ], md=6, lg=4),  # Adjust column size for responsiveness
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='pledge-trend-graph', figure=figures['pledge_trend']), md=12, lg=6),
        dbc.Col(dcc.Graph(id='pledge_distribution-graph', figure=figures['pledge_distribution']), md=12, lg=6),
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='fulfillment-rate-graph', figure=figures['fulfillment_rate']), md=12, lg=6),
        dbc.Col(dcc.Graph(id='pledge_payment-scatter-graph', figure=figures['pledge_payment_scatter']), md=12, lg=6),
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='pledges-by-year-graph', figure=figures['by_year']), width=12),
    ]),

    dbc.Row([
        dbc.Col(dcc.Graph(id='combined-metrics-graph', figure=figures['subplots']), width=12),
    ]),

    dbc.Row([
        dbc.Col([
            html.H2("Pledge Summary Table", className="mt-4"),
            dag.AgGrid(  # Replace dash_table with dash_ag_grid
                id='pledge-summary-grid',
                columnDefs=[
                    {"headerName": "Year", "field": "year"},
                    {"headerName": "Number of Pledges", "field": "num_pledges"},
                    {"headerName": "Total Pledge Amount", "field": "total_contribution_amount"},
                    {"headerName": "Average Pledge Amount", "field": "average_contribution_amount"},
                    {"headerName": "Fulfillment Rate (%)", "field": "fulfillment_rate"}  # added
                ],
                rowData=[],
                columnSize="sizeToFit",  # Adjust column size
                className="ag-theme-alpine"  # Add theme
            ),
        ], width=12),
    ]),

    dbc.Row([
        dbc.Col([
            html.H2("Ask a Question About the Data (LLM Placeholder)", className="mt-4"),
            dcc.Input(id='llm-input', type='text', placeholder='Enter your question', className="mb-2"),
            dbc.Button('Submit', id='llm-button', n_clicks=0, className="mr-2"),  # Added Bootstrap button
            html.Div(id='llm-output')
        ], width=12),
    ]),
], fluid=True)  # Use fluid=True for full width

# --- Callbacks ---

# Year Filter Callback
@app.callback(
    [Output('pledge-trend-graph', 'figure'),
     Output('pledge_distribution-graph', 'figure'),
     Output('fulfillment-rate-graph', 'figure'),
     Output('pledge_payment-scatter-graph', 'figure'),
     Output('pledges-by-year-graph', 'figure'),
     Output('pledge-summary-grid', 'rowData')],  # Update the AgGrid's rowData
    [Input('year-dropdown', 'value')]
)
def update_graphs(selected_years):
    """Updates graphs based on selected years."""

    # Filter the dataframe based on the selected years
    filtered_df = df[df['year'].isin(selected_years)]

    # Recreate visualizations with the filtered data
    filtered_figures = create_visualizations(filtered_df)

    # Create pledge summary data for the table
       # Create pledge summary data for the table
    pledge_summary = filtered_df.groupby('year').agg(
        num_pledges=('pledge_id', 'count'),
        total_contribution_amount=('contribution_amount', 'sum'),
        average_contribution_amount=('contribution_amount', 'mean'),
        total_payment_amount=('amount', 'sum')  # **USE THE COLUMN**
    ).reset_index()

    # Handle potential division by zero
    pledge_summary['fulfillment_rate'] = 0
    pledge_summary.loc[pledge_summary['total_contribution_amount'] != 0, 'fulfillment_rate'] = \
        (pledge_summary['total_payment_amount'] / pledge_summary['total_contribution_amount']) * 100

    pledge_summary['fulfillment_rate'] = pledge_summary['fulfillment_rate'].round(2)  # round to 2 decimals
    table_data = pledge_summary.to_dict('records')  # convert to a list of dictionaries

    return filtered_figures['pledge_trend'], \
           filtered_figures['pledge_distribution'], \
           filtered_figures['fulfillment_rate'], \
           filtered_figures['pledge_payment_scatter'], \
           filtered_figures['by_year'], \
           table_data  # Return the table data


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