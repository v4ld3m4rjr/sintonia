"""
Componentes de gráficos para o Sistema de Monitoramento do Atleta
----------------------------------------------------------------
Este módulo contém funções para criar gráficos reutilizáveis.
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

def create_trend_chart(df, x_col, y_col, title="", color=None, show_markers=True, fill=False, range_y=None):
    """
    Cria um gráfico de linha para visualizar tendências.
    
    Args:
        df (DataFrame): DataFrame com os dados
        x_col (str): Nome da coluna para o eixo x
        y_col (str): Nome da coluna para o eixo y
        title (str): Título do gráfico
        color (str): Cor da linha
        show_markers (bool): Se deve mostrar marcadores
        fill (bool): Se deve preencher a área abaixo da linha
        range_y (list): Limites do eixo y [min, max]
    
    Returns:
        Figure: Objeto de figura do Plotly
    """
    mode = "lines+markers" if show_markers else "lines"
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatter(
            x=df[x_col],
            y=df[y_col],
            mode=mode,
            line=dict(color=color, width=3),
            fill='tozeroy' if fill else None
        )
    )
    
    fig.update_layout(
        title=title,
        xaxis_title="",
        yaxis_title="",
        margin=dict(l=20, r=20, t=30, b=20),
        height=300
    )
    
    if range_y:
        fig.update_yaxes(range=range_y)
    
    return fig

def create_multi_trend_chart(df, x_col, y_cols, labels=None, colors=None, title="", use_secondary_y=False):
    """
    Cria um gráfico de linha com múltiplas séries.
    
    Args:
        df (DataFrame): DataFrame com os dados
        x_col (str): Nome da coluna para o eixo x
        y_cols (list): Lista de nomes de colunas para o eixo y
        labels (list): Lista de rótulos para as séries
        colors (list): Lista de cores para as séries
        title (str): Título do gráfico
        use_secondary_y (bool): Se deve usar eixo y secundário
    
    Returns:
        Figure: Objeto de figura do Plotly
    """
    if labels is None:
        labels = y_cols
    
    if colors is None:
        colors = px.colors.qualitative.Plotly
    
    # Cria um gráfico com eixos y secundários se necessário
    fig = make_subplots(specs=[[{"secondary_y": use_secondary_y}]])
    
    for i, (y_col, label) in enumerate(zip(y_cols, labels)):
        # Determina se deve usar o eixo y secundário
        use_secondary_axis = use_secondary_y and i > 0
        
        # Adiciona a linha
        fig.add_trace(
            go.Scatter(
                x=df[x_col],
                y=df[y_col],
                name=label,
                line=dict(color=colors[i % len(colors)], width=3),
                mode="lines+markers"
            ),
            secondary_y=use_secondary_axis
        )
    
    # Atualiza layout
    fig.update_layout(
        title=title,
        xaxis_title="",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=20, r=20, t=30, b=20),
        height=400
    )
    
    # Atualiza eixos y
    if use_secondary_y:
        fig.update_yaxes(title_text=labels[0], secondary_y=False)
        fig.update_yaxes(title_text=", ".join(labels[1:]), secondary_y=True)
    
    return fig

def create_bar_chart(df, x_col, y_col, title="", color=None, horizontal=False):
    """
    Cria um gráfico de barras.
    
    Args:
        df (DataFrame): DataFrame com os dados
        x_col (str): Nome da coluna para o eixo x
        y_col (str): Nome da coluna para o eixo y
        title (str): Título do gráfico
        color (str): Cor das barras
        horizontal (bool): Se as barras devem ser horizontais
    
    Returns:
        Figure: Objeto de figura do Plotly
    """
    if horizontal:
        fig = px.bar(
            df,
            y=x_col,
            x=y_col,
            title=title,
            color_discrete_sequence=[color] if color else None,
            orientation='h'
        )
    else:
        fig = px.bar(
            df,
            x=x_col,
            y=y_col,
            title=title,
            color_discrete_sequence=[color] if color else None
        )
    
    fig.update_layout(
        xaxis_title="",
        yaxis_title="",
        margin=dict(l=20, r=20, t=30, b=20),
        height=300
    )
    
    return fig

def create_grouped_bar_chart(df, x_col, y_cols, labels=None, colors=None, title="", barmode="group"):
    """
    Cria um gráfico de barras agrupadas.
    
    Args:
        df (DataFrame): DataFrame com os dados
        x_col (str): Nome da coluna para o eixo x
        y_cols (list): Lista de nomes de colunas para o eixo y
        labels (list): Lista de rótulos para as séries
        colors (list): Lista de cores para as séries
        title (str): Título do gráfico
        barmode (str): Modo de agrupamento das barras ('group', 'stack', 'relative')
    
    Returns:
        Figure: Objeto de figura do Plotly
    """
    if labels is None:
        labels = y_cols
    
    if colors is None:
        colors = px.colors.qualitative.Plotly
    
    fig = go.Figure()
    
    for i, (y_col, label) in enumerate(zip(y_cols, labels)):
        fig.add_trace(
            go.Bar(
                x=df[x_col],
                y=df[y_col],
                name=label,
                marker_color=colors[i % len(colors)]
            )
        )
    
    fig.update_layout(
        title=title,
        xaxis_title="",
        yaxis_title="",
        barmode=barmode,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=20, r=20, t=30, b=20),
        height=400
    )
    
    return fig

def create_pie_chart(labels, values, title=""):
    """
    Cria um gráfico de pizza.
    
    Args:
        labels (list): Lista de rótulos
        values (list): Lista de valores
        title (str): Título do gráfico
    
    Returns:
        Figure: Objeto de figura do Plotly
    """
    fig = go.Figure(
        data=[
            go.Pie(
                labels=labels,
                values=values,
                hole=0.4,
                textinfo="percent+label",
                insidetextorientation="radial"
            )
        ]
    )
    
    fig.update_layout(
        title=title,
        margin=dict(l=20, r=20, t=30, b=20),
        height=400
    )
    
    return fig

def create_radar_chart(categories, values, title="", max_value=None):
    """
    Cria um gráfico de radar.
    
    Args:
        categories (list): Lista de categorias
        values (list): Lista de valores
        title (str): Título do gráfico
        max_value (float): Valor máximo para o eixo radial
    
    Returns:
        Figure: Objeto de figura do Plotly
    """
    fig = go.Figure()
    
    fig.add_trace(
        go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            line=dict(color="#1E88E5", width=3)
        )
    )
    
    fig.update_layout(
        title=title,
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max_value] if max_value else None
            )
        ),
        margin=dict(l=40, r=40, t=30, b=40),
        height=400
    )
    
    return fig

def create_multi_radar_chart(categories, values_list, labels, colors=None, title="", max_value=None):
    """
    Cria um gráfico de radar com múltiplas séries.
    
    Args:
        categories (list): Lista de categorias
        values_list (list): Lista de listas de valores
        labels (list): Lista de rótulos para as séries
        colors (list): Lista de cores para as séries
        title (str): Título do gráfico
        max_value (float): Valor máximo para o eixo radial
    
    Returns:
        Figure: Objeto de figura do Plotly
    """
    if colors is None:
        colors = px.colors.qualitative.Plotly
    
    fig = go.Figure()
    
    for i, (values, label) in enumerate(zip(values_list, labels)):
        fig.add_trace(
            go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=label,
                line=dict(color=colors[i % len(colors)], width=3)
            )
        )
    
    fig.update_layout(
        title=title,
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max_value] if max_value else None
            )
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=40, r=40, t=30, b=40),
        height=400
    )
    
    return fig

def create_scatter_plot(df, x_col, y_col, color_col=None, size_col=None, title="", add_trendline=True):
    """
    Cria um gráfico de dispersão.
    
    Args:
        df (DataFrame): DataFrame com os dados
        x_col (str): Nome da coluna para o eixo x
        y_col (str): Nome da coluna para o eixo y
        color_col (str): Nome da coluna para a cor dos pontos
        size_col (str): Nome da coluna para o tamanho dos pontos
        title (str): Título do gráfico
        add_trendline (bool): Se deve adicionar linha de tendência
    
    Returns:
        Figure: Objeto de figura do Plotly
    """
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        color=color_col,
        size=size_col,
        title=title
    )
    
    if add_trendline:
        fig.add_traces(
            px.scatter(
                df, x=x_col, y=y_col, trendline='ols'
            ).data[1]
        )
        
        # Calcula correlação
        correlation = df[x_col].corr(df[y_col])
        
        # Adiciona anotação com correlação
        fig.add_annotation(
            x=0.95,
            y=0.05,
            xref="paper",
            yref="paper",
            text=f"r = {correlation:.2f}",
            showarrow=False,
            font=dict(
                size=14,
                color="black"
            ),
            bgcolor="white",
            bordercolor="black",
            borderwidth=1,
            borderpad=4
        )
    
    fig.update_layout(
        xaxis_title="",
        yaxis_title="",
        margin=dict(l=20, r=20, t=30, b=20),
        height=400
    )
    
    return fig

def create_heatmap(data, x_labels=None, y_labels=None, title="", colorscale="RdBu_r", text_auto=True):
    """
    Cria um mapa de calor.
    
    Args:
        data (array): Matriz de dados
        x_labels (list): Lista de rótulos para o eixo x
        y_labels (list): Lista de rótulos para o eixo y
        title (str): Título do gráfico
        colorscale (str): Escala de cores
        text_auto (bool): Se deve mostrar valores nas células
    
    Returns:
        Figure: Objeto de figura do Plotly
    """
    fig = px.imshow(
        data,
        x=x_labels,
        y=y_labels,
        color_continuous_scale=colorscale,
        text_auto=text_auto
    )
    
    fig.update_layout(
        title=title,
        xaxis_title="",
        yaxis_title="",
        margin=dict(l=20, r=20, t=30, b=20),
        height=400
    )
    
    return fig

def create_gauge_chart(value, min_value=0, max_value=100, title="", threshold_values=None, threshold_colors=None):
    """
    Cria um gráfico de medidor.
    
    Args:
        value (float): Valor a ser exibido
        min_value (float): Valor mínimo da escala
        max_value (float): Valor máximo da escala
        title (str): Título do gráfico
        threshold_values (list): Lista de valores de limiar
        threshold_colors (list): Lista de cores para os limiares
    
    Returns:
        Figure: Objeto de figura do Plotly
    """
    if threshold_values is None:
        threshold_values = [0, 20, 40, 60, 80, 100]
    
    if threshold_colors is None:
        threshold_colors = ["#F44336", "#FF9800", "#FFC107", "#8BC34A", "#4CAF50"]
    
    # Cria os passos de cor
    steps = []
    for i in range(len(threshold_values) - 1):
        steps.append({
            'range': [threshold_values[i], threshold_values[i + 1]],
            'color': threshold_colors[i]
        })
    
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': title},
            gauge={
                'axis': {'range': [min_value, max_value]},
                'bar': {'color': "#1E88E5"},
                'steps': steps,
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': value
                }
            }
        )
    )
    
    fig.update_layout(
        margin=dict(l=20, r=20, t=30, b=20),
        height=300
    )
    
    return fig

def create_calendar_heatmap(df, date_col, value_col, title="", colorscale="RdYlGn"):
    """
    Cria um mapa de calor em formato de calendário.
    
    Args:
        df (DataFrame): DataFrame com os dados
        date_col (str): Nome da coluna de data
        value_col (str): Nome da coluna de valor
        title (str): Título do gráfico
        colorscale (str): Escala de cores
    
    Returns:
        Figure: Objeto de figura do Plotly
    """
    # Garante que a data está no formato correto
    df = df.copy()
    df['date'] = pd.to_datetime(df[date_col])
    
    # Extrai ano, mês e dia
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['weekday'] = df['date'].dt.weekday
    
    # Cria o gráfico
    fig = px.scatter(
        df,
        x="day",
        y="weekday",
        color=value_col,
        color_continuous_scale=colorscale,
        size_max=15,
        facet_col="month",
        facet_col_wrap=3,
        labels={
            "weekday": "Dia da Semana",
            "day": "Dia do Mês",
            value_col: value_col
        },
        category_orders={
            "weekday": [0, 1, 2, 3, 4, 5, 6],
            "month": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        },
        hover_data=["date", value_col]
    )
    
    # Atualiza layout
    fig.update_layout(
        title=title,
        margin=dict(l=20, r=20, t=50, b=20),
        height=600
    )
    
    # Atualiza rótulos dos dias da semana
    weekday_names = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    fig.update_yaxes(
        tickvals=[0, 1, 2, 3, 4, 5, 6],
        ticktext=weekday_names
    )
    
    # Atualiza rótulos dos meses
    month_names = ["Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
    for i, m in enumerate(sorted(df['month'].unique())):
        fig.layout.annotations[i].text = month_names[m-1]
    
    return fig

def create_advanced_chart_with_zones(df, x_col, y_col, title="", color=None, zones=None):
    """
    Cria um gráfico de linha com zonas de referência.
    
    Args:
        df (DataFrame): DataFrame com os dados
        x_col (str): Nome da coluna para o eixo x
        y_col (str): Nome da coluna para o eixo y
        title (str): Título do gráfico
        color (str): Cor da linha
        zones (list): Lista de dicionários com zonas {min, max, color, label}
    
    Returns:
        Figure: Objeto de figura do Plotly
    """
    fig = go.Figure()
    
    # Adiciona as zonas de referência
    if zones:
        for zone in zones:
            fig.add_shape(
                type="rect",
                x0=df[x_col].iloc[0],
                x1=df[x_col].iloc[-1],
                y0=zone['min'],
                y1=zone['max'],
                fillcolor=zone['color'],
                opacity=0.2,
                line=dict(width=0),
                layer="below"
            )
    
    # Adiciona a linha
    fig.add_trace(
        go.Scatter(
            x=df[x_col],
            y=df[y_col],
            mode="lines+markers",
            line=dict(color=color, width=3)
        )
    )
    
    # Atualiza layout
    fig.update_layout(
        title=title,
        xaxis_title="",
        yaxis_title="",
        margin=dict(l=20, r=20, t=30, b=20),
        height=400
    )
    
    return fig

def create_tss_ctl_atl_chart(df, date_col='date_formatted'):
    """
    Cria um gráfico específico para TSS, CTL e ATL.
    
    Args:
        df (DataFrame): DataFrame com os dados
        date_col (str): Nome da coluna de data formatada
    
    Returns:
        Figure: Objeto de figura do Plotly
    """
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Adiciona barras de TSS
    fig.add_trace(
        go.Bar(
            x=df[date_col],
            y=df['tss'],
            name="TSS",
            marker_color="#FFC107"
        ),
        secondary_y=False
    )
    
    # Adiciona linha de CTL
    fig.add_trace(
        go.Scatter(
            x=df[date_col],
            y=df['ctl'],
            name="CTL",
            line=dict(color="#4CAF50", width=3),
            mode="lines+markers"
        ),
        secondary_y=True
    )
    
    # Adiciona linha de ATL
    fig.add_trace(
        go.Scatter(
            x=df[date_col],
            y=df['atl'],
            name="ATL",
            line=dict(color="#F44336", width=3),
            mode="lines+markers"
        ),
        secondary_y=True
    )
    
    # Adiciona faixas de referência para CTL (para atleta intermediário)
    fig.add_shape(
        type="rect",
        x0=df[date_col].iloc[0],
        x1=df[date_col].iloc[-1],
        y0=0,
        y1=30,
        fillcolor="rgba(244, 67, 54, 0.2)",  # Vermelho
        line=dict(width=0),
        layer="below",
        secondary_y=True
    )
    fig.add_shape(
        type="rect",
        x0=df[date_col].iloc[0],
        x1=df[date_col].iloc[-1],
        y0=30,
        y1=60,
        fillcolor="rgba(255, 152, 0, 0.2)",  # Laranja
        line=dict(width=0),
        layer="below",
        secondary_y=True
    )
    fig.add_shape(
        type="rect",
        x0=df[date_col].iloc[0],
        x1=df[date_col].iloc[-1],
        y0=60,
        y1=90,
        fillcolor="rgba(76, 175, 80, 0.2)",  # Verde
        line=dict(width=0),
        layer="below",
        secondary_y=True
    )
    fig.add_shape(
        type="rect",
        x0=df[date_col].iloc[0],
        x1=df[date_col].iloc[-1],
        y0=90,
        y1=120,
        fillcolor="rgba(255, 152, 0, 0.2)",  # Laranja
        line=dict(width=0),
        layer="below",
        secondary_y=True
    )
    fig.add_shape(
        type="rect",
        x0=df[date_col].iloc[0],
        x1=df[date_col].iloc[-1],
        y0=120,
        y1=200,
        fillcolor="rgba(244, 67, 54, 0.2)",  # Vermelho
        line=dict(width=0),
        layer="below",
        secondary_y=True
    )
    
    # Atualiza layout
    fig.update_layout(
        title="",
        xaxis_title="Data",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=20, r=20, t=30, b=20),
        height=500,
        hovermode="x unified"
    )
    
    # Atualiza eixos y
    fig.update_yaxes(title_text="TSS", secondary_y=False)
    fig.update_yaxes(title_text="CTL / ATL", secondary_y=True)
    
    return fig

def create_monotony_strain_chart(df, date_col='date_formatted'):
    """
    Cria um gráfico específico para Monotonia e Strain.
    
    Args:
        df (DataFrame): DataFrame com os dados
        date_col (str): Nome da coluna de data formatada
    
    Returns:
        Figure: Objeto de figura do Plotly
    """
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Adiciona linha de Monotonia
    fig.add_trace(
        go.Scatter(
            x=df[date_col],
            y=df['monotony'],
            name="Monotonia",
            line=dict(color="#4CAF50", width=3),
            mode="lines+markers"
        ),
        secondary_y=False
    )
    
    # Adiciona linha de Strain
    fig.add_trace(
        go.Scatter(
            x=df[date_col],
            y=df['strain'],
            name="Strain",
            line=dict(color="#F44336", width=3),
            mode="lines+markers"
        ),
        secondary_y=True
    )
    
    # Adiciona faixas de referência para Monotonia
    fig.add_shape(
        type="rect",
        x0=df[date_col].iloc[0],
        x1=df[date_col].iloc[-1],
        y0=0,
        y1=1.0,
        fillcolor="rgba(76, 175, 80, 0.2)",  # Verde
        line=dict(width=0),
        layer="below",
        secondary_y=False
    )
    fig.add_shape(
        type="rect",
        x0=df[date_col].iloc[0],
        x1=df[date_col].iloc[-1],
        y0=1.0,
        y1=1.5,
        fillcolor="rgba(139, 195, 74, 0.2)",  # Verde claro
        line=dict(width=0),
        layer="below",
        secondary_y=False
    )
    fig.add_shape(
        type="rect",
        x0=df[date_col].iloc[0],
        x1=df[date_col].iloc[-1],
        y0=1.5,
        y1=2.0,
        fillcolor="rgba(255, 152, 0, 0.2)",  # Laranja
        line=dict(width=0),
        layer="below",
        secondary_y=False
    )
    fig.add_shape(
        type="rect",
        x0=df[date_col].iloc[0],
        x1=df[date_col].iloc[-1],
        y0=2.0,
        y1=5.0,
        fillcolor="rgba(244, 67, 54, 0.2)",  # Vermelho
        line=dict(width=0),
        layer="below",
        secondary_y=False
    )
    
    # Adiciona faixas de referência para Strain
    fig.add_shape(
        type="rect",
        x0=df[date_col].iloc[0],
        x1=df[date_col].iloc[-1],
        y0=0,
        y1=1000,
        fillcolor="rgba(76, 175, 80, 0.2)",  # Verde
        line=dict(width=0),
        layer="below",
        secondary_y=True
    )
    fig.add_shape(
        type="rect",
        x0=df[date_col].iloc[0],
        x1=df[date_col].iloc[-1],
        y0=1000,
        y1=1500,
        fillcolor="rgba(139, 195, 74, 0.2)",  # Verde claro
        line=dict(width=0),
        layer="below",
        secondary_y=True
    )
    fig.add_shape(
        type="rect",
        x0=df[date_col].iloc[0],
        x1=df[date_col].iloc[-1],
        y0=1500,
        y1=2000,
        fillcolor="rgba(255, 152, 0, 0.2)",  # Laranja
        line=dict(width=0),
        layer="below",
        secondary_y=True
    )
    fig.add_shape(
        type="rect",
        x0=df[date_col].iloc[0],
        x1=df[date_col].iloc[-1],
        y0=2000,
        y1=3000,
        fillcolor="rgba(244, 67, 54, 0.2)",  # Vermelho
        line=dict(width=0),
        layer="below",
        secondary_y=True
    )
    fig.add_shape(
        type="rect",
        x0=df[date_col].iloc[0],
        x1=df[date_col].iloc[-1],
        y0=3000,
        y1=10000,
        fillcolor="rgba(183, 28, 28, 0.2)",  # Vermelho escuro
        line=dict(width=0),
        layer="below",
        secondary_y=True
    )
    
    # Atualiza layout
    fig.update_layout(
        title="",
        xaxis_title="Data",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=20, r=20, t=30, b=20),
        height=500,
        hovermode="x unified"
    )
    
    # Atualiza eixos y
    fig.update_yaxes(title_text="Monotonia", secondary_y=False)
    fig.update_yaxes(title_text="Strain", secondary_y=True)
    
    return fig
