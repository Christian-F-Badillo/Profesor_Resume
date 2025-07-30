from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from dash import Dash, dcc, html, Output, Input
from utils import generar_resumen

app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

app.title = "Análisis de Opiniones de Profesores de la Facultad de Psicología, UNAM"
data_reviews = pd.read_csv('https://raw.githubusercontent.com/Christian-F-Badillo/Profesor_Resume/refs/heads/master/data/summaries.csv')

lista_profesores = sorted(data_reviews["profesor"].unique())

app.layout = dbc.Container([
    html.H1(children = "Análisis de Opiniones de Profesores de la Facultad de Psicología, UNAM", className="text-center my-4", style = {'fontSize': 35}),

        dcc.Dropdown(
            id='selector-profesor',
            options=[{"label": nombre, "value": nombre} for nombre in lista_profesores],
            placeholder="Selecciona un profesor...",
            searchable=True,
            className="mb-4"
        ),
        html.Div(id="contenido-profesor"),
        html.Hr(),
        html.Footer([
        html.P("¿Te sirvió esta app? Invítame un café ☕", className="text-center"),
        html.Div(
            html.A("Donar en Ko-fi", href="https://ko-fi.com/christianbadillo1408", target="_blank"),
            className="text-center"
        )
        ], className="mt-4 text-muted")
    ],
    fluid=True)

@app.callback(
    Output("contenido-profesor", "children"),
    Input("selector-profesor", "value")
)
def update_dashboard(nombre:str) -> dbc.Container:
    if nombre is None:
        return html.Div("Selecciona un profesor para ver sus datos.")
    
    return dbc.Container(
        [
            dbc.Row(
                [
                    generar_resumen(data_reviews, nombre)
                ]
            )
        ]
    )


if __name__ == "__main__":
    app.run(debug = True)

