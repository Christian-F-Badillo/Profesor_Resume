import pandas as pd
from dash import html

def generar_resumen(df_prof: pd.DataFrame, name:str) -> html.Div:
    """
    Genera un resumen de las reseñas de un profesor específico.
    Args:
        df_prof (pd.DataFrame): DataFrame con las reseñas del profesor.
        name (str): Nombre del profesor.
    Returns:
        html.Div: Contenedor HTML con el resumen.
    """


    resumen = df_prof.loc[df_prof['profesor'] == name, 'resumen'].values[0] if not df_prof.empty else ''
    
    if resumen != '':
        return html.Div([
            html.H5("Resumen de Opiniones"),
            html.Blockquote(resumen),
        ])
    else:
        return html.Div([
            html.H5("Resumen"),
            html.P("No se encontró un resumen generado para este profesor."),
        ])