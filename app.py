from dash import Dash, dcc, callback, Output, Input, no_update
import dash_ag_grid as dag
import plotly.express as px
import pandas as pd

# df_pledges = pd.read_json("https://storage.googleapis.com/plotly-app-challenge/one-for-the-world-pledges.json")
df_payments = pd.read_json("https://storage.googleapis.com/plotly-app-challenge/one-for-the-world-payments.json")


fig = px.histogram(df_payments, x='payment_platform')

grid = dag.AgGrid(
    id='payments-table',
    rowData=df_payments.to_dict("records"),
    columnDefs=[{"field": i, 'filter': True, 'sortable': True} for i in df_payments.columns],
    dashGridOptions={"pagination": True}
)

app = Dash()

server = app.server

app.layout = [
    dcc.Markdown("# One For The World - Getting Started"),
    grid,
    dcc.Graph(id='platform-fig', figure=fig)
]


if __name__ == "__main__":
    app.run_server(debug=True)
