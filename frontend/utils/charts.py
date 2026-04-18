import plotly.graph_objects as go
import plotly.express as px
from typing import List


def milk_quality_pie(good: int, average: int, poor: int):
    fig = go.Figure(go.Pie(
        labels=["Good", "Average", "Poor"],
        values=[good, average, poor],
        hole=0.4,
        marker=dict(colors=["#2e7d32", "#f9a825", "#c62828"]),
    ))
    fig.update_layout(title="Milk Quality Distribution", showlegend=True, height=300)
    return fig


def health_status_bar(healthy: int, diseased: int):
    fig = go.Figure(go.Bar(
        x=["Healthy", "Diseased"],
        y=[healthy, diseased],
        marker_color=["#2e7d32", "#c62828"],
        text=[healthy, diseased],
        textposition="outside",
    ))
    fig.update_layout(title="Cattle Health Overview", yaxis_title="Count", height=300)
    return fig


def milk_trend_line(records: List[dict]):
    if not records:
        return go.Figure()
    dates  = [r.get("created_at", r.get("date", ""))[:10] for r in records]
    scores = [r.get("quality_score", r.get("score", 0)) for r in records]
    grades = [r.get("quality_grade", r.get("grade", "")) for r in records]

    color_map = {"Good": "#2e7d32", "Average": "#f9a825", "Poor": "#c62828"}
    colors = [color_map.get(g, "#888") for g in grades]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=scores, mode="lines+markers", name="Quality Score",
                             marker=dict(color=colors, size=10), line=dict(color="#66bb6a")))
    fig.update_layout(title="Milk Quality Trend", xaxis_title="Date", yaxis_title="Score", height=300)
    return fig


def disease_donut(predictions: dict):
    labels = list(predictions.keys())
    values = list(predictions.values())
    fig = go.Figure(go.Pie(labels=labels, values=values, hole=0.5,
                           marker=dict(colors=["#c62828", "#e53935", "#2e7d32", "#f9a825"])))
    fig.update_layout(title="Disease Prediction Confidence", height=300)
    return fig


def collection_bar(collections: List[dict]):
    if not collections:
        return go.Figure()
    dates   = [c["collection_date"] for c in collections]
    liters  = [c["quantity_liters"] for c in collections]
    fig = px.bar(x=dates, y=liters, title="Daily Milk Collection (Liters)",
                 labels={"x": "Date", "y": "Liters"}, color_discrete_sequence=["#2e7d32"])
    fig.update_layout(height=300)
    return fig
