from dash import html, dcc
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
from dash import Dash, dcc, html, Output, Input
from utils import generar_resumen, plot_facilidad, plot_calidad, show_means, get_tags, plot_tendencias, get_link

app = Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])

app.title = "Análisis de Opiniones de Profesores de la Facultad de Psicología, UNAM"
URL = "https://raw.githubusercontent.com/Christian-F-Badillo/Profesor_Resume/refs/heads/master/data/professor_data.csv"
data = pd.read_csv(URL)

lista_profesores = sorted(data["profesor"].unique())

app.layout = dbc.Container([
    html.H1(children = "Análisis de Opiniones de Profesores de la Facultad de Psicología, UNAM", className="text-center my-4", style = {'fontSize': 35}),

        dbc.Row([
            dbc.Col(
                html.Div(
                    dcc.Dropdown(
                        id='selector-profesor',
                        options=[{"label": nombre, "value": nombre} for nombre in lista_profesores],
                        placeholder="Selecciona un profesor...",
                        searchable=True,
                        className="mb-4",
                        style={'fontSize': 18, 'width': '100%'}
                    ),
                    style={'textAlign': 'center', 'margin': '0 auto', 'width': '100%'}
                ),
                width=3
            ),
            dbc.Col(html.Div(id='indicador-1'), width=2),
            dbc.Col(html.Div(id='indicador-2'), width=2),
            dbc.Col(html.Div(id='indicador-3'), width=2),
            dbc.Col(html.Div(id='indicador-4'), width=2)
        ], className="mb-4", justify="center"),
        html.Div(id="contenido-profesor"),
        html.Hr(),
        html.Footer([
        html.Div(
            html.A("Si esta app de fue de ayuda, puedes apoyarme con un café ☕", href="https://ko-fi.com/christianbadillo1408", target="_blank"),
            className="text-center"
        )
        ], className="mt-4 text-muted")
    ],
    fluid=True)

@app.callback(
   Output("contenido-profesor", "children"),
    Output("indicador-1", "children"),
    Output("indicador-2", "children"),
    Output("indicador-3", "children"),
    Output("indicador-4", "children"),
    Input("selector-profesor", "value")
)
def update_dashboard(nombre:str) -> tuple:
    if nombre is None:
        return html.Div("Por favor, selecciona un profesor."), html.Div(), html.Div(), html.Div(), html.Div()
    

    indicador1, indicador2, indicador3, indicador4 = show_means(data, nombre)
    contenido_profesor = dbc.Container(
            [
                dbc.Row(
                    [
                        generar_resumen(data, nombre)
                    ],
                    className="mb-4"
                ),
                dbc.Row(
                    [
                        html.H5(children=f"Etiquetas", className="text-left mb-4"),
                        dbc.Col(children=[
                            html.Div([
                                get_tags(data, nombre)
                            ])
                        ], width=12)
                    ],
                    className="mb-4"
                ),
                dbc.Row(
                    [
                        dbc.Col(children=[
                            html.Div([
                                plot_facilidad(data, nombre)
                            ])
                            ], width=6),
                        dbc.Col(children=[
                            html.Div([
                                plot_calidad(data, nombre)
                            ])
                        ], width=6)
                    ]
                ),
                dbc.Row(
                    [
                        dbc.Col(children=[
                            html.Div([
                                plot_tendencias(data, nombre)
                            ])
                        ], width=12)
                    ]
                ),
                html.Div(
                [
                    html.Span("Opiniones de alumnos extraídas de: ", style={"fontWeight": "bold"}),
                    html.A(get_link(data, nombre),
                        href=get_link(data, nombre),  # Reemplaza con tu URL
                        target="_blank",
                        style={"color": "#1E90FF", "textDecoration": "none"})
                ],
                style={
                    "textAlign": "center",
                    "marginTop": "30px",
                    "fontSize": "16px",
                    "color": "white"  # O ajusta según tu tema
                }
            )
            ]
        )
    return contenido_profesor, indicador1, indicador2, indicador3, indicador4


if __name__ == "__main__":
    app.run(debug = True)

