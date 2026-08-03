import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import Dash, Input, Output, dcc, html, dash_table
from src.database import read_observations
from src.pipeline import make_demo_data
from src.analysis import enrich, correlation_matrix

BLUE = "#1677C8"
NAVY = "#103B66"
PALETTE = ["#1677C8", "#12A594", "#7468D8", "#F39C4A", "#DE6B8A"]

def get_data():
    frame = read_observations()
    if frame.empty:
        make_demo_data()
        frame = read_observations()
    return enrich(frame)

def empty_chart(message):
    fig = go.Figure()
    fig.add_annotation(text=message, x=.5, y=.5, showarrow=False, font={"size": 15, "color": NAVY})
    fig.update_layout(template="plotly_white", height=360, xaxis={"visible": False}, yaxis={"visible": False})
    return fig

app = Dash(__name__, title="Economic Pulse Analytics")
app.layout = html.Main(className="page", children=[
    html.Section(className="hero", children=[
        html.Div([html.Div("ECONOMIC INTELLIGENCE", className="eyebrow"), html.H1("Economic Pulse Analytics"),
                  html.P("Explore inflation, employment, growth, interest rates, wages, and consumer spending through clear, data-driven visuals.")]),
        html.Div([html.Span("● ", className="live-dot"), "Interactive dashboard"], className="badge"),
    ]),
    html.Section(className="panel filters", children=[
        html.Div([html.Label("Country"), dcc.Dropdown(id="country", clearable=False)]),
        html.Div([html.Label("Indicators"), dcc.Dropdown(id="indicator", multi=True)]),
        html.Div([html.Label("Analysis period"), dcc.DatePickerRange(id="dates", display_format="MMM YYYY")]),
    ]),
    html.Div(id="summary", className="summary"),
    html.Div(id="kpis", className="kpis"),
    html.Section(className="panel chart", children=[
        html.H2("Trend comparison"),
        html.P("X-axis: date. Y-axis: indexed change, where every selected indicator starts at 100. This lets you compare movement across indicators even when their original units differ."),
        dcc.Graph(id="trend", config={"displaylogo": False}),
    ]),
    html.Section(className="chart-grid", children=[
        html.Div(className="panel chart", children=[html.H2("Indicator relationship"),
            html.P("X-axis: first selected indicator’s value. Y-axis: second selected indicator’s value. Each dot represents one date."),
            dcc.Graph(id="scatter", config={"displaylogo": False})]),
        html.Div(className="panel chart", children=[html.H2("Correlation map"),
            html.P("Both axes: indicators. Values from −1 to +1 show whether two indicators move in opposite or similar directions."),
            dcc.Graph(id="heatmap", config={"displaylogo": False})]),
    ]),
    html.Section(className="panel table-panel", children=[
        html.Div(className="table-head", children=[html.Div([html.H2("Searchable observations"), html.P("Inspect the individual observations powering the dashboard.")]), html.Button("Download filtered data", id="download-button", className="download")]),
        dash_table.DataTable(id="table", page_size=10, filter_action="native", sort_action="native", style_table={"overflowX":"auto"},
            style_header={"backgroundColor":"#E7F3FF", "color":NAVY, "fontWeight":"700", "border":"0"},
            style_cell={"fontFamily":"Arial, sans-serif", "padding":"11px", "border":"0", "borderBottom":"1px solid #E6EEF5", "textAlign":"left"},
            style_data_conditional=[{"if":{"row_index":"odd"}, "backgroundColor":"#F8FBFE"}]),
        dcc.Download(id="download"),
    ]),
    html.Footer("Economic Pulse Analytics · Public economic data for education and research"),
])

@app.callback(Output("country", "options"), Output("country", "value"), Output("indicator", "options"), Output("indicator", "value"),
              Output("dates", "start_date"), Output("dates", "end_date"), Input("country", "id"))
def defaults(_):
    frame = get_data()
    countries = sorted(frame.country_code.dropna().unique())
    names = sorted(frame.indicator_name.dropna().unique())
    preferred = [x for x in ["Inflation, consumer prices", "GDP Growth", "Unemployment", "Household consumption"] if x in names]
    return ([{"label":x,"value":x} for x in countries], "USA" if "USA" in countries else countries[0],
            [{"label":x,"value":x} for x in names], preferred or names[:3], frame.observation_date.min().date(), frame.observation_date.max().date())

@app.callback(Output("summary", "children"), Output("kpis", "children"), Output("trend", "figure"), Output("scatter", "figure"), Output("heatmap", "figure"),
              Output("table", "data"), Output("table", "columns"), Input("country", "value"), Input("indicator", "value"), Input("dates", "start_date"), Input("dates", "end_date"))
def update(country, selected, start, end):
    if not country or not selected or not start or not end:
        blank = empty_chart("Choose filters to begin your analysis.")
        return "Choose filters to begin your analysis.", [], blank, blank, blank, [], []
    frame = get_data()
    filtered = frame[(frame.country_code == country) & frame.indicator_name.isin(selected)].copy()
    filtered = filtered[(filtered.observation_date >= pd.Timestamp(start)) & (filtered.observation_date <= pd.Timestamp(end))]
    if filtered.empty:
        blank = empty_chart("No observations match these filters. Try a wider date range.")
        return "No matching observations.", [], blank, blank, blank, [], []

    latest = filtered.sort_values("observation_date").groupby("indicator_name", as_index=False).tail(1)
    cards = [html.Div(className="card", children=[html.Small(row.indicator_name), html.H3(f"{row.value:,.2f}"), html.Span(f"Latest: {row.observation_date:%b %Y} · {row.unit}")]) for row in latest.itertuples()]
    summary = f"Showing {len(filtered):,} observations for {country} from {filtered.observation_date.min():%b %Y} to {filtered.observation_date.max():%b %Y}."

    indexed = filtered.sort_values("observation_date").copy()
    indexed["index"] = indexed.groupby("indicator_name").value.transform(lambda x: x / x.iloc[0] * 100 if x.iloc[0] else x)
    trend = px.line(indexed, x="observation_date", y="index", color="indicator_name", color_discrete_sequence=PALETTE,
        labels={"observation_date":"Date", "index":"Index (start of period = 100)", "indicator_name":"Indicator"})
    trend.update_traces(line={"width":3}, hovertemplate="%{fullData.name}<br>Date: %{x|%b %Y}<br>Index: %{y:.1f}<extra></extra>")
    trend.update_layout(template="plotly_white", height=430, hovermode="x unified", legend_title_text="", margin={"l":20,"r":20,"t":15,"b":20})
    trend.update_xaxes(showgrid=False); trend.update_yaxes(gridcolor="#E5EEF6", zeroline=False)

    wide = filtered.pivot_table(index="observation_date", columns="indicator_name", values="value", aggfunc="mean").dropna().reset_index()
    cols = [x for x in wide.columns if x != "observation_date"]
    if len(cols) >= 2 and not wide.empty:
        scatter = px.scatter(wide, x=cols[0], y=cols[1], color_discrete_sequence=[BLUE], labels={cols[0]:cols[0], cols[1]:cols[1]})
        scatter.update_traces(marker={"size":8, "opacity":.75, "line":{"width":1,"color":"white"}})
        scatter.update_layout(template="plotly_white", height=360, margin={"l":20,"r":20,"t":15,"b":20})
        scatter.update_xaxes(gridcolor="#E5EEF6"); scatter.update_yaxes(gridcolor="#E5EEF6")
    else:
        scatter = empty_chart("Select two indicators with overlapping dates to compare them.")

    corr = correlation_matrix(filtered, country).dropna(axis=0, how="all").dropna(axis=1, how="all")
    if corr.shape[0] >= 2:
        heatmap = px.imshow(corr, text_auto=".2f", color_continuous_scale=["#D9EDFF", "#FFFFFF", "#1677C8"], zmin=-1, zmax=1,
            labels={"x":"Indicator", "y":"Indicator", "color":"Correlation"})
        heatmap.update_layout(template="plotly_white", height=360, margin={"l":20,"r":20,"t":15,"b":20})
    else:
        heatmap = empty_chart("Select at least two indicators with common dates.")

    display = filtered[["observation_date", "indicator_name", "category", "value", "unit", "source"]].sort_values("observation_date", ascending=False).copy()
    display["observation_date"] = display.observation_date.dt.strftime("%Y-%m-%d")
    return summary, cards, trend, scatter, heatmap, display.to_dict("records"), [{"name":x.replace("_"," ").title(),"id":x} for x in display.columns]

@app.callback(Output("download", "data"), Input("download-button", "n_clicks"), Input("country", "value"), Input("indicator", "value"), prevent_initial_call=True)
def download(clicks, country, selected):
    if not clicks or not country or not selected:
        return None
    frame = get_data()
    result = frame[(frame.country_code == country) & frame.indicator_name.isin(selected)]
    return dcc.send_data_frame(result.to_csv, "economic_pulse_filtered_data.csv", index=False)

if __name__ == "__main__":
    app.run(debug=True)
