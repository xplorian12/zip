import pandas as pd
import dash
from dash import dcc, html, Input, Output
import dash_bootstrap_components as dbc
from flask import Flask


server = Flask(__name__)
# Load your data
df = pd.read_csv("research.csv")

# Drop rows with missing values in 'Zip' or 'Area' columns
df = df.dropna(subset=['Zip', 'Area'])

# Convert ZIP codes to string and strip decimal
df['Zip'] = df['Zip'].astype(str).str.rstrip('.0')

# Create dropdown options like "90001 - Florence"
df["dropdown_label"] = df["Zip"] + " - " + df["Area"]
dropdown_options = [
    {"label": row["dropdown_label"], "value": row["Zip"]}
    for _, row in df.iterrows()
]

# Initialize Dash app with Bootstrap for clean design
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.LUX])

app.layout = dbc.Container([
    html.H2("LA Zip Code Data Dashboard (2025)", className="mt-4 mb-4 text-center"),

    dcc.Dropdown(
        id="zip-dropdown",
        options=dropdown_options,
        placeholder="Select a ZIP code",
        style={"margin-bottom": "30px"}
    ),

    html.Div(id="zip-data-display")
], fluid=True)


@app.callback(
    Output("zip-data-display", "children"),
    Input("zip-dropdown", "value")
)
def display_zip_data(zip_code):
    if not zip_code:
        return html.Div("Please select a ZIP code above.", className="text-muted")

    row = df[df["Zip"] == zip_code].squeeze()

    def card(title, value, color="light"):
        return dbc.Card(
            dbc.CardBody([
                html.H6(title, className="card-title"),
                html.H4(value, className="card-text")
            ]),
            className="m-2",
            color=color,
            inverse=False
        )

    # Format data
    def currency(val): return f"${val:,.0f}" if pd.notna(val) else "N/A"
    def percent(val): return f"{val:.1f}%" if pd.notna(val) else "N/A"
    def number(val): return f"{int(val):,}" if pd.notna(val) else "N/A"

    return dbc.Row([
        dbc.Col([
            html.H5(f"ZIP: {row['Zip']} - {row['Area']}", className="mb-3"),

            dbc.Row([
                dbc.Col(card("Median Lease Price", currency(row["median_LP"])), md=4),
                dbc.Col(card("Median Sale Price", currency(row["median_SP"])), md=4),
                dbc.Col(card("Median DOM", number(row["median_dom"])), md=4),
            ]),

            dbc.Row([
                dbc.Col(card("Median $/Sqft", currency(row["median_dollar_sqft"])), md=4),
                dbc.Col(card("Sale-to-Lease Ratio", f"{row['ratio']:.2f}" if pd.notna(row["ratio"]) else "N/A"), md=4),
                dbc.Col(card("Sale Price Change", currency(row["sale_price_change"])), md=4),
            ]),

            dbc.Row([
                dbc.Col(card("Sale % Change", percent(row["sale_perc_change"])), md=4),
                dbc.Col(card("Lease Price Change", currency(row["lease_price_change"])), md=4),
                dbc.Col(card("Income Diff", currency(row["income_diff"])), md=4),
            ]),

            dbc.Row([
                dbc.Col(card("Income % Change", percent(row["income_pct_change"])), md=4),
                dbc.Col(card("Demolitions Issued", number(row["Bldg-Demolition_Issued"])), md=4),
                dbc.Col(card("Demolitions Finaled", number(row["Bldg-Demolition_Permit Finaled"])), md=4),
            ]),

            dbc.Row([
                dbc.Col(card("New Builds Issued", number(row["Bldg-New_Issued"])), md=6),
                dbc.Col(card("New Builds Finaled", number(row["Bldg-New_Permit Finaled"])), md=6),
            ]),
        ])
    ])

if __name__ == '__main__':
    # Get the port from the environment variable
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
