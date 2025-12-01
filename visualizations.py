# visualizations.py
import plotly.express as px

def fig_time_series(df):
    daily = df.groupby("date", as_index=False)["amount"].sum()
    fig = px.line(daily, x="date", y="amount", title="Daily Sales")
    fig.update_layout(hovermode="x")
    return fig

def fig_by_category(df):
    cat = df.groupby("category", as_index=False)["amount"].sum().sort_values("amount", ascending=False)
    return px.bar(cat, x="category", y="amount", title="Sales by Category", hover_data=["amount"])

def fig_region_pie(df):
    reg = df.groupby("region", as_index=False)["amount"].sum()
    return px.pie(reg, names="region", values="amount", title="Sales by Region")
