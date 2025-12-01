# app.py
import pandas as pd
from sqlalchemy import create_engine
from dash import Dash, dcc, html, Input, Output
from visualizations import fig_time_series, fig_by_category, fig_region_pie

# --- Load data ---
sales = pd.read_csv("data/sales.csv", parse_dates=["date"])
engine = create_engine("sqlite:///data/customers.db")
customers = pd.read_sql("customers", engine, parse_dates=["signup_date"])

df = sales.merge(customers, on="customer_id", how="left")

# --- Fix duplicate region columns (region_x, region_y) ---
if "region_x" in df.columns:
    df.rename(columns={"region_x": "region"}, inplace=True)
    df.drop(columns=["region_y"], inplace=True, errors="ignore")

df["month"] = df["date"].dt.to_period("M").astype(str)
df["amount"] = df["amount"].astype(float)

# --- Dash app setup ---
app = Dash(__name__, title="Sales Dashboard")
server = app.server

categories = [{"label": c, "value": c} for c in sorted(df["category"].unique())]
regions = [{"label": r, "value": r} for r in sorted(df["region"].unique())]
min_date, max_date = df["date"].min(), df["date"].max()

# --- Layout ---
app.layout = html.Div(
    style={
        "fontFamily": "Segoe UI, sans-serif",
        "padding": "20px",
        "maxWidth": "1200px",
        "margin": "auto",
        "backgroundColor": "#f8f9fa"
    },
    children=[
        html.H1("📊 Interactive Sales Dashboard", 
                style={"textAlign": "center", "color": "#2c3e50"}),

        html.Div([
            html.Div([
                html.Label("📅 Date Range", style={"fontWeight": "bold"}),
                dcc.DatePickerRange(
                    id="date-range",
                    start_date=min_date,
                    end_date=max_date,
                    display_format="YYYY-MM-DD"
                ),
            ], style={"display": "inline-block", "marginRight": "20px"}),

            html.Div([
                html.Label("🏷️ Category", style={"fontWeight": "bold"}),
                dcc.Dropdown(
                    id="category-dropdown", 
                    options=categories, 
                    multi=True, 
                    placeholder="All categories"
                ),
            ], style={"display": "inline-block", "width": "250px", "marginRight": "20px"}),

            html.Div([
                html.Label("🌍 Region", style={"fontWeight": "bold"}),
                dcc.Dropdown(
                    id="region-dropdown", 
                    options=regions, 
                    multi=True, 
                    placeholder="All regions"
                ),
            ], style={"display": "inline-block", "width": "250px"}),

            html.Div([
                html.Label("⬇️ Download Data", style={"fontWeight": "bold"}),
                html.Button("Download CSV", id="btn-download", n_clicks=0, 
                            style={"marginTop": "5px", "backgroundColor": "#2ecc71", 
                                   "color": "white", "border": "none", 
                                   "padding": "8px 15px", "borderRadius": "6px"}),
                dcc.Download(id="download-dataframe-csv"),
            ], style={"display": "inline-block", "marginLeft": "20px"})
        ], style={
            "marginBottom": "30px", 
            "padding": "15px", 
            "backgroundColor": "white", 
            "borderRadius": "10px", 
            "boxShadow": "0px 2px 8px rgba(0,0,0,0.1)"
        }),

        html.Div([
            dcc.Graph(id="time-series"),
        ], style={
            "backgroundColor": "white", 
            "padding": "15px", 
            "borderRadius": "10px", 
            "boxShadow": "0px 2px 8px rgba(0,0,0,0.1)",
            "marginBottom": "20px"
        }),

        html.Div([
            html.Div(dcc.Graph(id="category-bar"), 
                     style={"width": "49%", "display": "inline-block", "verticalAlign": "top"}),
            html.Div(dcc.Graph(id="region-pie"), 
                     style={"width": "49%", "display": "inline-block", "verticalAlign": "top"}),
        ])
    ]
)

# --- Callbacks ---
@app.callback(
    Output("time-series", "figure"),
    Output("category-bar", "figure"),
    Output("region-pie", "figure"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
    Input("category-dropdown", "value"),

    Input("region-dropdown", "value"),

)
def update_charts(start_date, end_date, sel_categories, sel_regions):
    dff = df.copy()

    if start_date:
        dff = dff[dff["date"] >= pd.to_datetime(start_date)]
    if end_date:
        dff = dff[dff["date"] <= pd.to_datetime(end_date)]
    if sel_categories:
        dff = dff[dff["category"].isin(sel_categories)]
    if sel_regions:
        dff = dff[dff["region"].isin(sel_regions)]

    return (
        fig_time_series(dff),
        fig_by_category(dff),
        fig_region_pie(dff),
    )

# --- CSV Download Callback ---
@app.callback(
    Output("download-dataframe-csv", "data"),
    Input("btn-download", "n_clicks"),
    prevent_initial_call=True,
)
def download_csv(n_clicks):
    return dcc.send_data_frame(df.to_csv, "sales_data.csv", index=False)

# --- Run app ---
if __name__ == "__main__":
    app.run(debug=True, port=8050)
