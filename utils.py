import pandas as pd
from dash import html
from plotly import express as px
import plotly.graph_objects as go
from dash import dcc
import dash_daq as daq
import plotly.io as pio
import dash_bootstrap_components as dbc

pio.templates.default = "plotly_dark"
theme = {
    'dark': True
}

etiqueta_color = {
    'ASPECTOS DE CALIFICACIÓN CLAROS': 'info',
    'MUCHOS EXÁMENES': 'warning',
    'MUCHAS TAREAS': 'warning',
    'ASISTENCIA OBLIGATORIA': 'secondary',
    'LAS CLASES SON LARGAS': 'secondary',
    'INSPIRACIONAL': 'primary',
    'BARCO': 'light',
    'LA PARTICIPACIÓN IMPORTA': 'info',
    'LOS EXÁMENES SON DIFÍCILES': 'danger',
    'CALIFICA DURO': 'danger',
    'POCOS EXÁMENES': 'success',
    'PREPÁRATE PARA LEER': 'info',
    'DA BUENA RETROALIMENTACIÓN': 'success',
    'DEJA TRABAJOS LARGOS': 'warning',
    'CLASES EXCELENTES': 'success',
    'MUCHOS PROYECTOS GRUPALES': 'warning',
    'TOMARÍA SU CLASE OTRA VEZ': 'success',
    'BRINDA APOYO': 'primary',
    'MUY CÓMICO': 'info',
    'HACE EXÁMENES SORPRESA': 'danger',
    'DA CRÉDITO EXTRA': 'success',
    'RESPETADO POR LOS ESTUDIANTES': 'primary',
}

meses_es_a_en = {
    'Ene': 'Jan', 'Feb': 'Feb', 'Mar': 'Mar', 'Abr': 'Apr', 'May': 'May', 'Jun': 'Jun',
    'Jul': 'Jul', 'Ago': 'Aug', 'Sep': 'Sep', 'Oct': 'Oct', 'Nov': 'Nov', 'Dic': 'Dec'
    }

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

def plot_facilidad (df_prof: pd.DataFrame, name: str) -> html.Div:
    """
    Genera un histograma de la facilidad de comprensión de un profesor.
    Args:
        df_prof (pd.DataFrame): DataFrame con las reseñas del profesor.
        name (str): Nombre del profesor.
    Returns:
        html.Div: Contenedor HTML con el histograma.
    """
    if df_prof.empty:
        return html.Div("No hay datos disponibles para este profesor.")

    facilidad = df_prof.loc[df_prof['profesor'] == name, ['facilidad']]['facilidad'].values[0]
    facilidad = facilidad.split(',')
    facilidad = pd.to_numeric(facilidad, errors='coerce')
    facilidad = pd.DataFrame({'facilidad': facilidad}).astype("category")
    facilidad = facilidad['facilidad'].value_counts().reset_index()
    facilidad.columns = ['facilidad', 'frecuencia']

    if facilidad.empty:
        return html.Div("No hay datos de facilidad de comprensión para este profesor.")
    
    # Convertimos de string a num los datos separados por comas

    fig = go.Figure(
    data=go.Bar(
        x=facilidad['facilidad'],
        y=facilidad['frecuencia'],
        text=facilidad['frecuencia'],    
        textposition='auto',
        hovertext=[f"Facilidad: {f}, Frecuencia: {v}" for f, v in zip(facilidad['facilidad'], facilidad['frecuencia'])],
        hoverinfo='text',
        marker=dict(line=dict(width=0)),       
        orientation='v'
    ))

    fig.update_layout(
        title=f"Facilidad del docente {name}",
        xaxis_title='Facilidad',
        yaxis_title='Frecuencia',
        bargap=0.2,
        plot_bgcolor='black',
        paper_bgcolor='black',
        barcornerradius=30,
        xaxis=dict(tickvals = facilidad['facilidad'].unique())
    )
    fig.update_xaxes(
        showgrid= False,
        ticks="outside",
    )

    return html.Div(dcc.Graph(figure=fig))

def plot_calidad (df_prof: pd.DataFrame, name: str) -> html.Div:
    """
    Genera un histograma de la calidad de las reseñas de un profesor.
    Args:
        df_prof (pd.DataFrame): DataFrame con las reseñas del profesor.
        name (str): Nombre del profesor.
    Returns:
        html.Div: Contenedor HTML con el histograma.
    """
    if df_prof.empty:
        return html.Div("No hay datos disponibles para este profesor.")

    calidad = df_prof.loc[df_prof['profesor'] == name, ['calidad_general']]['calidad_general'].values[0]
    calidad = calidad.split(',')
    calidad = pd.to_numeric(calidad, errors='coerce')
    calidad = pd.DataFrame({'calidad': calidad}).astype("category")
    calidad = calidad['calidad'].value_counts().reset_index()
    calidad.columns = ['calidad', 'frecuencia']

    if calidad.empty:
        return html.Div("No hay datos de calidad para este profesor.")

    # Convertimos de string a num los datos separados por comas

    fig = go.Figure(
    data=go.Bar(
        x=calidad['calidad'],
        y=calidad['frecuencia'],
        text=calidad['frecuencia'],    
        textposition='auto',
        hovertext=[f"Calidad: {f}, Frecuencia: {v}" for f, v in zip(calidad['calidad'], calidad['frecuencia'])],
        hoverinfo='text',
        marker=dict(line=dict(width=0)),       
        orientation='v'
    ))

    fig.update_layout(
        title=f"Calidad del docente {name}",
        xaxis_title='Calidad',
        yaxis_title='Frecuencia',
        plot_bgcolor='black',
        paper_bgcolor='black',
        bargap=0.2,
        barcornerradius=30,
        xaxis=dict(tickvals = calidad['calidad'].unique())
    )
    fig.update_xaxes(
        showgrid= False,
        ticks="outside",
    )

    return html.Div(dcc.Graph(figure=fig))

def show_means(df_prof: pd.DataFrame, name: str):
    row = df_prof[df_prof['profesor'] == name]
    if row.empty:
        return "", "", "", ""

    row = row.iloc[0]

    facilidad_vals = pd.to_numeric(str(row['facilidad']).split(','), errors='coerce')
    calidad_vals = pd.to_numeric(str(row['calidad_general']).split(','), errors='coerce')
    media = float(row['promedio'])

    facilidad_mean = round(facilidad_vals.mean(), 2)
    calidad_mean = round(calidad_vals.mean(), 2)
    media_round = round(media, 2)

    numero_reseñas = row['num_reviews']

    def color(valor):
        if valor >= 7.5:
            return "#00FF00"
        elif valor >= 5.0:
            return "#FFFF00"
        else:
            return "#FF4136"
        
    def color_num_reviews(valor):
        if valor >= 25:
            return "#00FF00"
        elif valor >= 10:
            return "#FFFF00"
        else:
            return "#FF4136"

    estilo_led = {'marginBottom': '15px'}

    indicador_1 = daq.LEDDisplay(
        label="Facilidad Promedio",
        value=facilidad_mean,
        color=color(facilidad_mean),
        backgroundColor="#000000",
        style=estilo_led,
        labelPosition = "bottom"
    )
    indicador_2 = daq.LEDDisplay(
        label="Calidad Promedio",
        value=calidad_mean,
        color=color(calidad_mean),
        backgroundColor="#000000",
        style=estilo_led,
        labelPosition = "bottom"
    )
    indicador_3 = daq.LEDDisplay(
        label="Promedio General",
        value=media_round,
        color=color(media_round),
        backgroundColor="#000000",
        style=estilo_led,
        labelPosition = "bottom"
    )
    indicador_4 = daq.LEDDisplay(
        label="Número de Opiniones Evaluadas",
        value=numero_reseñas,
        color=color_num_reviews(numero_reseñas),
        backgroundColor="#000000",
        style=estilo_led,
        labelPosition = "bottom"
    )

    return indicador_1, indicador_2, indicador_3, indicador_4

def get_tags(df_prof: pd.DataFrame, name: str) -> html.Div:
    """
    Obtiene las etiquetas asociadas a un profesor específico.
    Args:
        df_prof (pd.DataFrame): DataFrame con las reseñas del profesor.
        name (str): Nombre del profesor.
    Returns:
        list: Lista de etiquetas asociadas al profesor.
    """
    row = df_prof[df_prof['profesor'] == name]
    if row.empty:
        return html.Div("No hay etiquetas disponibles para este profesor.")

    tags = row.iloc[0]['tags']
    if pd.isna(tags):
        return html.Div("No hay etiquetas disponibles para este profesor.")

    tags = tags.split(',')
    tags = [tag.strip() for tag in tags if tag.strip() != '']
    
    return html.Div(
        [
            dbc.Badge(etiqueta,
                      color=etiqueta_color.get(etiqueta, 'secondary'),
                      className="me-1 mb-1",
                      pill=True)
            for etiqueta in tags
        ],
        className="mb-3"
    )

def plot_tendencias(df_prof: pd.DataFrame, name: str) -> html.Div:
    """
    Genera un gráfico de líneas que muestra la evolución de las calificaciones a lo largo del tiempo.
    Args:
        df_prof (pd.DataFrame): DataFrame con las reseñas del profesor.
        name (str): Nombre del profesor.
    Returns:
        html.Div: Contenedor HTML con el gráfico de líneas.
    """
    if df_prof.empty:
        return html.Div("No hay datos disponibles para este profesor.")

    df_prof = df_prof[df_prof['profesor'] == name]
    if df_prof.empty:
        return html.Div("No hay datos disponibles para este profesor.")

    fechas_str = df_prof['fecha'].values[0]
    facilidad_str = df_prof['facilidad'].values[0]
    calidad_str = df_prof['calidad_general'].values[0]
    # Convertir a listas
    fechas = [f.strip() for f in fechas_str.split(',')]
    facilidad = [float(f.strip()) for f in facilidad_str.split(',')]
    calidad = [float(c.strip()) for c in calidad_str.split(',')]

    # Reemplazar meses
    fechas_en = [f.replace(mes_es, mes_en) for f in fechas for mes_es, mes_en in meses_es_a_en.items() if mes_es in f]


    # Crear dataframe
    df = pd.DataFrame({
        'fecha': pd.to_datetime(fechas_en, format="%d/%b/%Y"),
        'facilidad': facilidad,
        'calidad': calidad
    })

    # Crear columna 'semestre' como texto tipo "2025-1" o "2024-2"
    df['año'] = df['fecha'].dt.year
    df['mes'] = df['fecha'].dt.month
    df['semestre'] = df.apply(lambda x: f"{x['año']}-1" if x['mes'] <= 6 else f"{x['año']}-2", axis=1)

    # Crear fecha de referencia (1 de enero o 1 de julio de cada semestre)
    df['fecha_referencia'] = df.apply(
        lambda x: pd.Timestamp(year=x['año'], month=1 if x['mes'] <= 6 else 7, day=1),
        axis=1
    )

    # Agrupar por semestre
    df_resumen = df.groupby(['semestre', 'fecha_referencia'], as_index=False)[['facilidad', 'calidad']].mean()
    df_resumen['n'] = df.groupby(['semestre', 'fecha_referencia']).size().values

    # Crear gráfico
    fig = px.line(
        df_resumen,
        x="fecha_referencia",
        y=["facilidad", "calidad"],
        markers=True,
        title="Promedio por semestre",
        labels={"fecha_referencia": "Semestre", "value": "Calificación promedio"}
    )

    # Ajustar trazo y marcadores proporcional al número de evaluaciones
    fig.update_traces(
        mode='lines+markers',
        line=dict(width=4),
        marker=dict(
            size=df_resumen['n'],
            sizemode='area',
            sizeref=2.*max(df_resumen['n'])/(40.**2),  # controla el tamaño relativo
            sizemin=6
        ),
        hovertemplate='%{y:.2f}<br>Semestre: %{x|%Y-%m}<br>N: %{customdata}',
        customdata=df_resumen[['n']].values
    )

    # Agregar etiquetas de valores encima de los puntos
    for columna in ["facilidad", "calidad"]:
        fig.add_scatter(
            x=df_resumen["fecha_referencia"],
            y=df_resumen[columna],
            mode="text",
            text=[f"{v:.1f}" for v in df_resumen[columna]],
            textposition="top center",
            showlegend=False
        )

    # Personalizar apariencia
    fig.update_layout(
        xaxis_title="Semestre",
        yaxis_title="Calificación promedio",
        template='plotly_dark',
        plot_bgcolor='black',
        paper_bgcolor='black',
        font=dict(color='white'),
        legend_title_text='Calificaciones',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )

    # Eje X con etiquetas de semestre
    fig.update_xaxes(
        tickvals=df_resumen["fecha_referencia"],
        ticktext=df_resumen["semestre"],
        tickangle=45,
        showgrid=False,
        ticks="outside"
    )

    # Eje Y
    fig.update_yaxes(
        showgrid=True,
        gridcolor='LightGray',
        ticks="outside"
    )

    return html.Div(dcc.Graph(figure=fig))

def get_link(df_prof: pd.DataFrame, name: str) -> str:
    """
    Obtiene el enlace asociado a un profesor específico.
    Args:
        df_prof (pd.DataFrame): DataFrame con las reseñas del profesor.
        name (str): Nombre del profesor.
    Returns:
        str: Enlace asociado al profesor.
    """
    row = df_prof[df_prof['profesor'] == name]
    if row.empty:
        return "https://www.misprofesores.com/"

    link = row.iloc[0]['enlace']
    return link if pd.notna(link) else "https://www.misprofesores.com/"