"""
Componentes de gráficos para o Sistema de Monitoramento do Atleta
----------------------------------------------------------------
Este módulo contém funções para criar gráficos interativos usando Plotly.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from utils.helpers import get_color_for_value

def create_trend_chart(dates, readiness=None, trimp=None, stress=None):
    """
    Cria um gráfico de tendência combinando múltiplas métricas.
    
    Args:
        dates (list): Lista de datas (eixo x)
        readiness (list): Valores de prontidão
        trimp (list): Valores de TRIMP
        stress (list): Valores de estresse
    
    Returns:
        Figure: Objeto de figura do Plotly
    """
    # Cria um gráfico com dois eixos y
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Adiciona linha de prontidão (eixo y primário)
    if readiness is not None:
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=readiness,
                name="Prontidão",
                line=dict(color="#4CAF50", width=3),
                mode="lines+markers"
            ),
            secondary_y=False
        )
    
    # Adiciona linha de TRIMP (eixo y secundário)
    if trimp is not None:
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=trimp,
                name="TRIMP",
                line=dict(color="#1E88E5", width=3),
                mode="lines+markers"
            ),
            secondary_y=True
        )
    
    # Adiciona linha de estresse (eixo y primário)
    if stress is not None:
        fig.add_trace(
            go.Scatter(
                x=dates,
                y=stress,
                name="Estresse",
                line=dict(color="#F44336", width=3, dash="dot"),
                mode="lines+markers"
            ),
            secondary_y=False
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
        height=400,
        hovermode="x unified"
    )
    
    # Atualiza eixos y
    fig.update_yaxes(title_text="Prontidão / Estresse", secondary_y=False)
    fig.update_yaxes(title_text="TRIMP", secondary_y=True)
    
    return fig

def create_radar_chart(categories, values, reference_values=None, title=""):
    """
    Cria um gráfico de radar para comparação de múltiplas categorias.
    
    Args:
        categories (list): Lista de categorias
        values (list): Valores atuais
        reference_values (list): Valores de referência para comparação
        title (str): Título do gráfico
    
    Returns:
        Figure: Objeto de figura do Plotly
    """
    # Fecha o polígono repetindo o primeiro valor
    categories = categories + [categories[0]]
    values = values + [values[0]]
    
    # Cria a figura
    fig = go.Figure()
    
    # Adiciona o traço principal
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Atual',
        line_color='#1E88E5',
        fillcolor='rgba(30, 136, 229, 0.3)'
    ))
    
    # Adiciona o traço de referência, se fornecido
    if reference_values is not None:
        reference_values = reference_values + [reference_values[0]]
        fig.add_trace(go.Scatterpolar(
            r=reference_values,
            theta=categories,
            fill='toself',
            name='Média',
            line_color='#FFC107',
            fillcolor='rgba(255, 193, 7, 0.3)'
        ))
    
    # Atualiza layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, max(max(values), max(reference_values) if reference_values else 0) * 1.1]
            )
        ),
        title=title,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=30, r=30, t=50, b=30),
        height=400
    )
    
    return fig

def create_bar_chart(categories, values, color='#1E88E5', title="", x_title="", y_title=""):
    """
    Cria um gráfico de barras simples.
    
    Args:
        categories (list): Lista de categorias (eixo x)
        values (list): Valores para cada categoria
        color (str): Cor das barras
        title (str): Título do gráfico
        x_title (str): Título do eixo x
        y_title (str): Título do eixo y
    
    Returns:
        Figure: Objeto de figura do Plotly
    """
    # Cria o DataFrame
    df = pd.DataFrame({
        'Categoria': categories,
        'Valor': values
    })
    
    # Cria o gráfico
    fig = px.bar(
        df,
        x='Categoria',
        y='Valor',
        color_discrete_sequence=[color],
        labels={'Categoria': x_title, 'Valor': y_title}
    )
    
    # Atualiza layout
    fig.update_layout(
        title=title,
        xaxis_title=x_title,
        yaxis_title=y_title,
        margin=dict(l=20, r=20, t=50, b=20),
        height=400
    )
    
    return fig

def create_heatmap(data_matrix, x_labels, y_labels, title="", colorscale="Blues"):
    """
    Cria um mapa de calor (heatmap) para visualização de correlações.
    
    Args:
        data_matrix (list): Matriz de dados 2D
        x_labels (list): Rótulos para o eixo x
        y_labels (list): Rótulos para o eixo y
        title (str): Título do gráfico
        colorscale (str): Escala de cores do Plotly
    
    Returns:
        Figure: Objeto de figura do Plotly
    """
    # Cria a figura
    fig = go.Figure(data=go.Heatmap(
        z=data_matrix,
        x=x_labels,
        y=y_labels,
        colorscale=colorscale,
        colorbar=dict(title="Correlação"),
        hoverongaps=False
    ))
    
    # Atualiza layout
    fig.update_layout(
        title=title,
        xaxis_title="",
        yaxis_title="",
        margin=dict(l=20, r=20, t=50, b=20),
        height=500
    )
    
    return fig

def create_scatter_plot(x_data, y_data, x_label, y_label, title="", color='#1E88E5', add_trendline=True):
    """
    Cria um gráfico de dispersão (scatter plot) para análise de correlações.
    
    Args:
        x_data (list): Dados para o eixo x
        y_data (list): Dados para o eixo y
        x_label (str): Rótulo para o eixo x
        y_label (str): Rótulo para o eixo y
        title (str): Título do gráfico
        color (str): Cor dos pontos
        add_trendline (bool): Se deve adicionar linha de tendência
    
    Returns:
        Figure: Objeto de figura do Plotly
    """
    # Cria o DataFrame
    df = pd.DataFrame({
        'x': x_data,
        'y': y_data
    })
    
    # Cria o gráfico
    fig = px.scatter(
        df,
        x='x',
        y='y',
        labels={'x': x_label, 'y': y_label},
        color_discrete_sequence=[color],
        trendline='ols' if add_trendline else None
    )
    
    # Atualiza layout
    fig.update_layout(
        title=title,
        xaxis_title=x_label,
        yaxis_title=y_label,
        margin=dict(l=20, r=20, t=50, b=20),
        height=400
    )
    
    return fig

def create_gauge_chart(value, min_value=0, max_value=100, title="", threshold_ranges=None):
    """
    Cria um gráfico de medidor (gauge) para visualização de métricas.
    
    Args:
        value (float): Valor atual
        min_value (float): Valor mínimo da escala
        max_value (float): Valor máximo da escala
        title (str): Título do gráfico
        threshold_ranges (list): Lista de tuplas (valor, cor) para definir faixas
    
    Returns:
        Figure: Objeto de figura do Plotly
    """
    # Define faixas de cores padrão se não fornecidas
    if threshold_ranges is None:
        threshold_ranges = [
            (0.2 * max_value, "red"),
            (0.6 * max_value, "yellow"),
            (max_value, "green")
        ]
    
    # Cria a figura
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title},
        gauge={
            'axis': {'range': [min_value, max_value]},
            'bar': {'color': get_color_for_value(value / max_value * 100, "readiness")},
            'steps': [
                {'range': [min_value, threshold_ranges[0][0]], 'color': threshold_ranges[0][1]},
                {'range': [threshold_ranges[0][0], threshold_ranges[1][0]], 'color': threshold_ranges[1][1]},
                {'range': [threshold_ranges[1][0], threshold_ranges[2][0]], 'color': threshold_ranges[2][1]}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))
    
    # Atualiza layout
    fig.update_layout(
        margin=dict(l=20, r=20, t=50, b=20),
        height=300
    )
    
    return fig

def create_pie_chart(labels, values, title="", color_sequence=None):
    """
    Cria um gráfico de pizza para visualização de distribuições.
    
    Args:
        labels (list): Rótulos para as fatias
        values (list): Valores para cada fatia
        title (str): Título do gráfico
        color_sequence (list): Lista de cores para as fatias
    
    Returns:
        Figure: Objeto de figura do Plotly
    """
    # Cria o DataFrame
    df = pd.DataFrame({
        'Categoria': labels,
        'Valor': values
    })
    
    # Cria o gráfico
    fig = px.pie(
        df,
        values='Valor',
        names='Categoria',
        title=title,
        color_discrete_sequence=color_sequence
    )
    
    # Atualiza layout
    fig.update_layout(
        margin=dict(l=20, r=20, t=50, b=20),
        height=400
    )
    
    # Atualiza traços
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    return fig
