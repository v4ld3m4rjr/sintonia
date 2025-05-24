"""
Módulo de visualização para o Sistema de Monitoramento do Atleta
-----------------------------------------------------------
Este módulo contém funções para criação de visualizações avançadas e personalizadas.
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st
import colorsys

# Configurações de estilo
THEME_COLORS = {
    "primary": "#1E88E5",    # Azul principal
    "secondary": "#7E57C2",  # Roxo secundário
    "success": "#4CAF50",    # Verde sucesso
    "warning": "#FFC107",    # Amarelo alerta
    "danger": "#F44336",     # Vermelho perigo
    "info": "#03A9F4",       # Azul claro informação
    "light": "#ECEFF1",      # Cinza claro
    "dark": "#263238",       # Cinza escuro
    "background": "#121212", # Fundo escuro
    "text": "#FFFFFF"        # Texto claro
}

# Funções de cores e paletas

def generate_color_palette(base_color, n_colors=5, mode="sequential"):
    """
    Gera uma paleta de cores a partir de uma cor base.
    
    Args:
        base_color (str): Cor base em formato hexadecimal
        n_colors (int): Número de cores na paleta
        mode (str): Modo da paleta ('sequential', 'diverging', 'qualitative')
    
    Returns:
        list: Lista de cores em formato hexadecimal
    """
    # Converte hex para RGB
    base_color = base_color.lstrip('#')
    r, g, b = tuple(int(base_color[i:i+2], 16) for i in (0, 2, 4))
    r, g, b = r/255.0, g/255.0, b/255.0
    
    # Converte RGB para HSV
    h, s, v = colorsys.rgb_to_hsv(r, g, b)
    
    palette = []
    
    if mode == "sequential":
        # Paleta sequencial (variação de luminosidade)
        for i in range(n_colors):
            # Varia a luminosidade de 0.3 a 1.0
            new_v = 0.3 + (0.7 * i / (n_colors - 1)) if n_colors > 1 else v
            new_r, new_g, new_b = colorsys.hsv_to_rgb(h, s, new_v)
            hex_color = "#{:02x}{:02x}{:02x}".format(
                int(new_r * 255), int(new_g * 255), int(new_b * 255)
            )
            palette.append(hex_color)
    
    elif mode == "diverging":
        # Paleta divergente (variação de matiz)
        for i in range(n_colors):
            # Varia a matiz de -0.3 a +0.3 em relação à cor base
            offset = -0.3 + (0.6 * i / (n_colors - 1)) if n_colors > 1 else 0
            new_h = (h + offset) % 1.0
            new_r, new_g, new_b = colorsys.hsv_to_rgb(new_h, s, v)
            hex_color = "#{:02x}{:02x}{:02x}".format(
                int(new_r * 255), int(new_g * 255), int(new_b * 255)
            )
            palette.append(hex_color)
    
    elif mode == "qualitative":
        # Paleta qualitativa (variação de matiz em intervalos regulares)
        for i in range(n_colors):
            # Distribui as cores uniformemente no círculo de cores
            new_h = (h + i / n_colors) % 1.0 if n_colors > 1 else h
            new_r, new_g, new_b = colorsys.hsv_to_rgb(new_h, s, v)
            hex_color = "#{:02x}{:02x}{:02x}".format(
                int(new_r * 255), int(new_g * 255), int(new_b * 255)
            )
            palette.append(hex_color)
    
    return palette

def get_color_by_value(value, min_val, max_val, palette=None):
    """
    Retorna uma cor baseada no valor dentro de um intervalo.
    
    Args:
        value (float): Valor a ser mapeado para uma cor
        min_val (float): Valor mínimo do intervalo
        max_val (float): Valor máximo do intervalo
        palette (list): Lista de cores (padrão: verde-amarelo-vermelho)
    
    Returns:
        str: Cor em formato hexadecimal
    """
    if palette is None:
        palette = [THEME_COLORS["success"], THEME_COLORS["warning"], THEME_COLORS["danger"]]
    
    # Normaliza o valor para o intervalo [0, 1]
    if max_val == min_val:
        normalized = 0.5
    else:
        normalized = (value - min_val) / (max_val - min_val)
    
    # Limita ao intervalo [0, 1]
    normalized = max(0, min(1, normalized))
    
    # Mapeia para o índice na paleta
    index = normalized * (len(palette) - 1)
    
    # Interpolação linear entre as cores mais próximas
    lower_idx = int(index)
    upper_idx = min(lower_idx + 1, len(palette) - 1)
    
    if lower_idx == upper_idx:
        return palette[lower_idx]
    
    # Peso para interpolação
    weight = index - lower_idx
    
    # Converte cores para RGB
    lower_color = palette[lower_idx].lstrip('#')
    upper_color = palette[upper_idx].lstrip('#')
    
    r1, g1, b1 = tuple(int(lower_color[i:i+2], 16) for i in (0, 2, 4))
    r2, g2, b2 = tuple(int(upper_color[i:i+2], 16) for i in (0, 2, 4))
    
    # Interpolação linear
    r = int(r1 * (1 - weight) + r2 * weight)
    g = int(g1 * (1 - weight) + g2 * weight)
    b = int(b1 * (1 - weight) + b2 * weight)
    
    return "#{:02x}{:02x}{:02x}".format(r, g, b)

# Funções de gráficos básicos

def create_line_chart(df, x_col, y_col, title=None, color=None, range_y=None, 
                      show_trend=False, markers=False, fill=False, 
                      reference_ranges=None, annotations=None):
    """
    Cria um gráfico de linha personalizado.
    
    Args:
        df (DataFrame): DataFrame com os dados
        x_col (str): Nome da coluna para o eixo X
        y_col (str): Nome da coluna para o eixo Y
        title (str): Título do gráfico
        color (str): Cor da linha
        range_y (list): Intervalo do eixo Y [min, max]
        show_trend (bool): Se deve mostrar linha de tendência
        markers (bool): Se deve mostrar marcadores
        fill (bool): Se deve preencher área abaixo da linha
        reference_ranges (list): Lista de dicionários com faixas de referência
        annotations (list): Lista de dicionários com anotações
    
    Returns:
        Figure: Objeto de figura do Plotly
    """
    if color is None:
        color = THEME_COLORS["primary"]
    
    # Cria o gráfico base
    fig = px.line(
        df, 
        x=x_col, 
        y=y_col,
        title=title,
        markers=markers,
        color_discrete_sequence=[color]
    )
    
    # Configurações de layout
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis_title=None,
        yaxis_title=None,
        legend_title=None,
        font=dict(family="Arial, sans-serif", size=12, color=THEME_COLORS["text"]),
        hovermode="x unified"
    )
    
    # Configurações de eixos
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(255,255,255,0.1)",
        showline=True,
        linewidth=1,
        linecolor="rgba(255,255,255,0.3)"
    )
    
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(255,255,255,0.1)",
        showline=True,
        linewidth=1,
        linecolor="rgba(255,255,255,0.3)"
    )
    
    # Define o intervalo do eixo Y
    if range_y:
        fig.update_yaxes(range=range_y)
    
    # Adiciona preenchimento
    if fill:
        fig.update_traces(fill='tozeroy', fillcolor=f"{color}20")
    
    # Adiciona linha de tendência
    if show_trend and len(df) > 1:
        # Calcula a regressão linear
        x = np.arange(len(df))
        y = df[y_col].values
        mask = ~np.isnan(y)
        
        if sum(mask) > 1:  # Precisa de pelo menos 2 pontos
            x_valid = x[mask]
            y_valid = y[mask]
            
            coeffs = np.polyfit(x_valid, y_valid, 1)
            trend_line = coeffs[0] * x + coeffs[1]
            
            # Adiciona a linha de tendência
            fig.add_trace(
                go.Scatter(
                    x=df[x_col],
                    y=trend_line,
                    mode='lines',
                    line=dict(color=color, width=1, dash='dash'),
                    name='Tendência',
                    hoverinfo='skip'
                )
            )
    
    # Adiciona faixas de referência
    if reference_ranges:
        for range_info in reference_ranges:
            fig.add_shape(
                type="rect",
                xref="paper",
                yref="y",
                x0=0,
                x1=1,
                y0=range_info["y0"],
                y1=range_info["y1"],
                fillcolor=range_info["color"] + "20",  # Adiciona transparência
                line=dict(width=0),
                layer="below"
            )
            
            # Adiciona rótulo da faixa (opcional)
            if "label" in range_info and range_info["label"]:
                fig.add_annotation(
                    xref="paper",
                    yref="y",
                    x=1.01,
                    y=(range_info["y0"] + range_info["y1"]) / 2,
                    text=range_info["label"],
                    showarrow=False,
                    font=dict(size=10, color=range_info["color"]),
                    align="left"
                )
    
    # Adiciona anotações
    if annotations:
        for annotation in annotations:
            fig.add_annotation(
                x=annotation["x"],
                y=annotation["y"],
                text=annotation["text"],
                showarrow=annotation.get("showarrow", True),
                arrowhead=annotation.get("arrowhead", 2),
                arrowcolor=annotation.get("color", THEME_COLORS["primary"]),
                font=dict(
                    color=annotation.get("color", THEME_COLORS["primary"]),
                    size=annotation.get("size", 10)
                )
            )
    
    return fig

def create_bar_chart(df, x_col, y_col, title=None, color=None, range_y=None,
                     horizontal=False, text_auto=False, group=None, 
                     reference_line=None, sort_values=False):
    """
    Cria um gráfico de barras personalizado.
    
    Args:
        df (DataFrame): DataFrame com os dados
        x_col (str): Nome da coluna para o eixo X
        y_col (str): Nome da coluna para o eixo Y
        title (str): Título do gráfico
        color (str): Cor das barras
        range_y (list): Intervalo do eixo Y [min, max]
        horizontal (bool): Se o gráfico deve ser horizontal
        text_auto (bool): Se deve mostrar valores nas barras
        group (str): Nome da coluna para agrupar barras
        reference_line (dict): Dicionário com informações da linha de referência
        sort_values (bool): Se deve ordenar por valores
    
    Returns:
        Figure: Objeto de figura do Plotly
    """
    if color is None:
        color = THEME_COLORS["primary"]
    
    # Ordena os dados se necessário
    if sort_values:
        df = df.sort_values(by=y_col)
    
    # Cria o gráfico base
    if horizontal:
        fig = px.bar(
            df,
            y=x_col,
            x=y_col,
            title=title,
            color=group,
            color_discrete_sequence=[color] if group is None else None,
            text_auto=text_auto,
            orientation='h'
        )
    else:
        fig = px.bar(
            df,
            x=x_col,
            y=y_col,
            title=title,
            color=group,
            color_discrete_sequence=[color] if group is None else None,
            text_auto=text_auto
        )
    
    # Configurações de layout
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis_title=None,
        yaxis_title=None,
        legend_title=None,
        font=dict(family="Arial, sans-serif", size=12, color=THEME_COLORS["text"]),
        hovermode="closest"
    )
    
    # Configurações de eixos
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(255,255,255,0.1)",
        showline=True,
        linewidth=1,
        linecolor="rgba(255,255,255,0.3)"
    )
    
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(255,255,255,0.1)",
        showline=True,
        linewidth=1,
        linecolor="rgba(255,255,255,0.3)"
    )
    
    # Define o intervalo do eixo Y
    if range_y and not horizontal:
        fig.update_yaxes(range=range_y)
    elif range_y and horizontal:
        fig.update_xaxes(range=range_y)
    
    # Adiciona linha de referência
    if reference_line:
        if horizontal:
            fig.add_shape(
                type="line",
                xref="x",
                yref="paper",
                x0=reference_line["value"],
                x1=reference_line["value"],
                y0=0,
                y1=1,
                line=dict(
                    color=reference_line.get("color", THEME_COLORS["warning"]),
                    width=reference_line.get("width", 2),
                    dash=reference_line.get("dash", "dash")
                )
            )
            
            if "label" in reference_line:
                fig.add_annotation(
                    xref="x",
                    yref="paper",
                    x=reference_line["value"],
                    y=1.02,
                    text=reference_line["label"],
                    showarrow=False,
                    font=dict(
                        color=reference_line.get("color", THEME_COLORS["warning"]),
                        size=10
                    )
                )
        else:
            fig.add_shape(
                type="line",
                xref="paper",
                yref="y",
                x0=0,
                x1=1,
                y0=reference_line["value"],
                y1=reference_line["value"],
                line=dict(
                    color=reference_line.get("color", THEME_COLORS["warning"]),
                    width=reference_line.get("width", 2),
                    dash=reference_line.get("dash", "dash")
                )
            )
            
            if "label" in reference_line:
                fig.add_annotation(
                    xref="paper",
                    yref="y",
                    x=1.01,
                    y=reference_line["value"],
                    text=reference_line["label"],
                    showarrow=False,
                    font=dict(
                        color=reference_line.get("color", THEME_COLORS["warning"]),
                        size=10
                    )
                )
    
    return fig

def create_pie_chart(df, names_col, values_col, title=None, colors=None, hole=0.4,
                     show_percentages=True, pull=None, sort=True):
    """
    Cria um gráfico de pizza personalizado.
    
    Args:
        df (DataFrame): DataFrame com os dados
        names_col (str): Nome da coluna para os rótulos
        values_col (str): Nome da coluna para os valores
        title (str): Título do gráfico
        colors (list): Lista de cores
        hole (float): Tamanho do buraco central (0-1)
        show_percentages (bool): Se deve mostrar percentuais
        pull (list): Lista de valores para destacar fatias
        sort (bool): Se deve ordenar por valores
    
    Returns:
        Figure: Objeto de figura do Plotly
    """
    if colors is None:
        colors = generate_color_palette(THEME_COLORS["primary"], len(df), "qualitative")
    
    # Ordena os dados se necessário
    if sort:
        df = df.sort_values(by=values_col, ascending=False)
    
    # Cria o gráfico base
    fig = go.Figure(
        data=[
            go.Pie(
                labels=df[names_col],
                values=df[values_col],
                hole=hole,
                pull=pull,
                marker_colors=colors,
                textinfo='percent' if show_percentages else 'label',
                hoverinfo='label+percent+value',
                textfont=dict(size=12, color=THEME_COLORS["text"])
            )
        ]
    )
    
    # Configurações de layout
    fig.update_layout(
        title=title,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=50, b=10),
        font=dict(family="Arial, sans-serif", size=12, color=THEME_COLORS["text"]),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        )
    )
    
    return fig

def create_scatter_chart(df, x_col, y_col, title=None, color=None, size_col=None,
                         text_col=None, trendline=False, range_x=None, range_y=None,
                         reference_ranges_x=None, reference_ranges_y=None):
    """
    Cria um gráfico de dispersão personalizado.
    
    Args:
        df (DataFrame): DataFrame com os dados
        x_col (str): Nome da coluna para o eixo X
        y_col (str): Nome da coluna para o eixo Y
        title (str): Título do gráfico
        color (str): Cor dos pontos
        size_col (str): Nome da coluna para o tamanho dos pontos
        text_col (str): Nome da coluna para o texto ao passar o mouse
        trendline (bool): Se deve mostrar linha de tendência
        range_x (list): Intervalo do eixo X [min, max]
        range_y (list): Intervalo do eixo Y [min, max]
        reference_ranges_x (list): Lista de dicionários com faixas de referência para X
        reference_ranges_y (list): Lista de dicionários com faixas de referência para Y
    
    Returns:
        Figure: Objeto de figura do Plotly
    """
    if color is None:
        color = THEME_COLORS["primary"]
    
    # Cria o gráfico base
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        title=title,
        color_discrete_sequence=[color],
        size=size_col,
        text=text_col,
        trendline='ols' if trendline else None
    )
    
    # Configurações de layout
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis_title=None,
        yaxis_title=None,
        legend_title=None,
        font=dict(family="Arial, sans-serif", size=12, color=THEME_COLORS["text"]),
        hovermode="closest"
    )
    
    # Configurações de eixos
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(255,255,255,0.1)",
        showline=True,
        linewidth=1,
        linecolor="rgba(255,255,255,0.3)"
    )
    
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(255,255,255,0.1)",
        showline=True,
        linewidth=1,
        linecolor="rgba(255,255,255,0.3)"
    )
    
    # Define os intervalos dos eixos
    if range_x:
        fig.update_xaxes(range=range_x)
    
    if range_y:
        fig.update_yaxes(range=range_y)
    
    # Adiciona faixas de referência para X
    if reference_ranges_x:
        for range_info in reference_ranges_x:
            fig.add_shape(
                type="rect",
                xref="x",
                yref="paper",
                x0=range_info["x0"],
                x1=range_info["x1"],
                y0=0,
                y1=1,
                fillcolor=range_info["color"] + "20",  # Adiciona transparência
                line=dict(width=0),
                layer="below"
            )
    
    # Adiciona faixas de referência para Y
    if reference_ranges_y:
        for range_info in reference_ranges_y:
            fig.add_shape(
                type="rect",
                xref="paper",
                yref="y",
                x0=0,
                x1=1,
                y0=range_info["y0"],
                y1=range_info["y1"],
                fillcolor=range_info["color"] + "20",  # Adiciona transparência
                line=dict(width=0),
                layer="below"
            )
    
    return fig

# Funções de gráficos avançados

def create_radar_chart(categories, values, title=None, color=None, range_r=None,
                       fill=True, show_grid=True, comparison_values=None, comparison_name=None):
    """
    Cria um gráfico de radar personalizado.
    
    Args:
        categories (list): Lista de categorias
        values (list): Lista de valores
        title (str): Título do gráfico
        color (str): Cor da área
        range_r (list): Intervalo do raio [min, max]
        fill (bool): Se deve preencher a área
        show_grid (bool): Se deve mostrar a grade
        comparison_values (list): Lista de valores para comparação
        comparison_name (str): Nome da série de comparação
    
    Returns:
        Figure: Objeto de figura do Plotly
    """
    if color is None:
        color = THEME_COLORS["primary"]
    
    # Fecha o polígono repetindo o primeiro valor
    categories_closed = categories + [categories[0]]
    values_closed = values + [values[0]]
    
    # Cria o gráfico base
    fig = go.Figure()
    
    # Adiciona a série principal
    fig.add_trace(
        go.Scatterpolar(
            r=values_closed,
            theta=categories_closed,
            fill='toself' if fill else None,
            fillcolor=color + "40",  # Adiciona transparência
            line=dict(color=color, width=2),
            name="Atual"
        )
    )
    
    # Adiciona a série de comparação
    if comparison_values is not None:
        comparison_values_closed = comparison_values + [comparison_values[0]]
        comparison_color = THEME_COLORS["secondary"]
        
        fig.add_trace(
            go.Scatterpolar(
                r=comparison_values_closed,
                theta=categories_closed,
                fill='toself' if fill else None,
                fillcolor=comparison_color + "40",  # Adiciona transparência
                line=dict(color=comparison_color, width=2, dash='dash'),
                name=comparison_name if comparison_name else "Comparação"
            )
        )
    
    # Configurações de layout
    fig.update_layout(
        title=title,
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=range_r,
                showticklabels=show_grid,
                gridcolor="rgba(255,255,255,0.1)",
                linecolor="rgba(255,255,255,0.3)"
            ),
            angularaxis=dict(
                showticklabels=True,
                gridcolor="rgba(255,255,255,0.1)",
                linecolor="rgba(255,255,255,0.3)"
            ),
            bgcolor="rgba(0,0,0,0)"
        ),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=50, b=10),
        font=dict(family="Arial, sans-serif", size=12, color=THEME_COLORS["text"]),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="center",
            x=0.5
        )
    )
    
    return fig

def create_heatmap(data, x_labels=None, y_labels=None, title=None, colorscale=None,
                   show_values=True, range_color=None, center_color=None):
    """
    Cria um mapa de calor personalizado.
    
    Args:
        data (array): Matriz de dados
        x_labels (list): Rótulos do eixo X
        y_labels (list): Rótulos do eixo Y
        title (str): Título do gráfico
        colorscale (list): Escala de cores
        show_values (bool): Se deve mostrar valores nas células
        range_color (list): Intervalo de cores [min, max]
        center_color (float): Valor central para escala divergente
    
    Returns:
        Figure: Objeto de figura do Plotly
    """
    if colorscale is None:
        if center_color is not None:
            # Escala divergente
            colorscale = [
                [0, THEME_COLORS["danger"]],
                [0.5, "#FFFFFF"],
                [1, THEME_COLORS["success"]]
            ]
        else:
            # Escala sequencial
            colorscale = [
                [0, "#FFFFFF"],
                [1, THEME_COLORS["primary"]]
            ]
    
    # Cria o gráfico base
    fig = go.Figure(
        data=go.Heatmap(
            z=data,
            x=x_labels,
            y=y_labels,
            colorscale=colorscale,
            zmin=range_color[0] if range_color else None,
            zmax=range_color[1] if range_color else None,
            zmid=center_color,
            text=data if show_values else None,
            texttemplate="%{text:.2f}" if show_values else None,
            textfont=dict(color="black", size=10),
            hoverinfo="x+y+z"
        )
    )
    
    # Configurações de layout
    fig.update_layout(
        title=title,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis_title=None,
        yaxis_title=None,
        font=dict(family="Arial, sans-serif", size=12, color=THEME_COLORS["text"])
    )
    
    return fig

def create_gauge_chart(value, title=None, min_val=0, max_val=100, threshold_values=None,
                       threshold_colors=None, show_current_value=True):
    """
    Cria um gráfico de medidor (gauge) personalizado.
    
    Args:
        value (float): Valor atual
        title (str): Título do gráfico
        min_val (float): Valor mínimo
        max_val (float): Valor máximo
        threshold_values (list): Lista de valores de limiar
        threshold_colors (list): Lista de cores para cada faixa
        show_current_value (bool): Se deve mostrar o valor atual
    
    Returns:
        Figure: Objeto de figura do Plotly
    """
    if threshold_values is None:
        threshold_values = [min_val, (min_val + max_val) / 2, max_val]
    
    if threshold_colors is None:
        threshold_colors = [THEME_COLORS["danger"], THEME_COLORS["warning"], THEME_COLORS["success"]]
    
    # Garante que os limiares estão em ordem crescente
    threshold_values = sorted(threshold_values)
    
    # Cria o gráfico base
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number" if show_current_value else "gauge",
            value=value,
            domain=dict(x=[0, 1], y=[0, 1]),
            title=dict(text=title, font=dict(color=THEME_COLORS["text"])),
            gauge=dict(
                axis=dict(
                    range=[min_val, max_val],
                    tickwidth=1,
                    tickcolor=THEME_COLORS["text"]
                ),
                bar=dict(color=THEME_COLORS["primary"]),
                bgcolor="rgba(0,0,0,0)",
                borderwidth=0,
                steps=[
                    dict(
                        range=[threshold_values[i], threshold_values[i+1]],
                        color=threshold_colors[i] + "40"  # Adiciona transparência
                    )
                    for i in range(len(threshold_values) - 1)
                ],
                threshold=dict(
                    line=dict(color=THEME_COLORS["text"], width=2),
                    thickness=0.75,
                    value=value
                )
            ),
            number=dict(
                font=dict(color=THEME_COLORS["text"]),
                suffix=""
            )
        )
    )
    
    # Configurações de layout
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=50, b=10),
        font=dict(family="Arial, sans-serif", size=12, color=THEME_COLORS["text"])
    )
    
    return fig

def create_calendar_heatmap(dates, values, title=None, colorscale=None, range_color=None):
    """
    Cria um mapa de calor em formato de calendário.
    
    Args:
        dates (list): Lista de datas
        values (list): Lista de valores
        title (str): Título do gráfico
        colorscale (list): Escala de cores
        range_color (list): Intervalo de cores [min, max]
    
    Returns:
        Figure: Objeto de figura do Plotly
    """
    if colorscale is None:
        colorscale = [
            [0, "#FFFFFF"],
            [1, THEME_COLORS["primary"]]
        ]
    
    # Converte para DataFrame
    df = pd.DataFrame({
        'date': pd.to_datetime(dates),
        'value': values
    })
    
    # Extrai ano, mês e dia
    df['year'] = df['date'].dt.year
    df['month'] = df['date'].dt.month
    df['day'] = df['date'].dt.day
    df['weekday'] = df['date'].dt.weekday
    
    # Cria o gráfico base
    fig = px.scatter(
        df,
        x='day',
        y='weekday',
        color='value',
        color_continuous_scale=colorscale,
        range_color=range_color,
        title=title,
        labels={
            'weekday': 'Dia da Semana',
            'day': 'Dia do Mês',
            'value': 'Valor'
        },
        size_max=15,
        height=250
    )
    
    # Configurações de layout
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=50, b=10),
        font=dict(family="Arial, sans-serif", size=12, color=THEME_COLORS["text"]),
        coloraxis_colorbar=dict(
            title=None,
            tickfont=dict(color=THEME_COLORS["text"])
        )
    )
    
    # Configurações de eixos
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(255,255,255,0.1)",
        showline=True,
        linewidth=1,
        linecolor="rgba(255,255,255,0.3)",
        tickvals=list(range(1, 32, 5))
    )
    
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(255,255,255,0.1)",
        showline=True,
        linewidth=1,
        linecolor="rgba(255,255,255,0.3)",
        tickvals=list(range(7)),
        ticktext=['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
    )
    
    # Ajusta o tamanho dos pontos
    fig.update_traces(marker=dict(size=15))
    
    return fig

def create_bubble_chart(df, x_col, y_col, size_col, text_col=None, color_col=None,
                        title=None, range_x=None, range_y=None, range_size=None):
    """
    Cria um gráfico de bolhas personalizado.
    
    Args:
        df (DataFrame): DataFrame com os dados
        x_col (str): Nome da coluna para o eixo X
        y_col (str): Nome da coluna para o eixo Y
        size_col (str): Nome da coluna para o tamanho das bolhas
        text_col (str): Nome da coluna para o texto ao passar o mouse
        color_col (str): Nome da coluna para a cor das bolhas
        title (str): Título do gráfico
        range_x (list): Intervalo do eixo X [min, max]
        range_y (list): Intervalo do eixo Y [min, max]
        range_size (list): Intervalo de tamanho das bolhas [min, max]
    
    Returns:
        Figure: Objeto de figura do Plotly
    """
    # Cria o gráfico base
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        size=size_col,
        color=color_col,
        text=text_col,
        title=title,
        size_max=50,
        color_discrete_sequence=[THEME_COLORS["primary"]] if color_col is None else None,
        color_continuous_scale=px.colors.sequential.Blues if color_col is not None else None
    )
    
    # Configurações de layout
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis_title=None,
        yaxis_title=None,
        legend_title=None,
        font=dict(family="Arial, sans-serif", size=12, color=THEME_COLORS["text"]),
        hovermode="closest"
    )
    
    # Configurações de eixos
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(255,255,255,0.1)",
        showline=True,
        linewidth=1,
        linecolor="rgba(255,255,255,0.3)"
    )
    
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(255,255,255,0.1)",
        showline=True,
        linewidth=1,
        linecolor="rgba(255,255,255,0.3)"
    )
    
    # Define os intervalos dos eixos
    if range_x:
        fig.update_xaxes(range=range_x)
    
    if range_y:
        fig.update_yaxes(range=range_y)
    
    # Ajusta o tamanho das bolhas
    if range_size:
        fig.update_traces(marker=dict(sizemin=range_size[0], sizeref=range_size[1]))
    
    return fig

# Funções de gráficos específicos para o sistema

def create_tss_ctl_atl_chart(df, date_col='date_only', tss_col='tss', ctl_col='ctl', 
                             atl_col='atl', tsb_col='tsb', title="Carga de Treino"):
    """
    Cria um gráfico combinado de TSS, CTL, ATL e TSB.
    
    Args:
        df (DataFrame): DataFrame com os dados
        date_col (str): Nome da coluna de data
        tss_col (str): Nome da coluna de TSS
        ctl_col (str): Nome da coluna de CTL
        atl_col (str): Nome da coluna de ATL
        tsb_col (str): Nome da coluna de TSB
        title (str): Título do gráfico
    
    Returns:
        Figure: Objeto de figura do Plotly
    """
    # Cria o gráfico com subplots
    fig = make_subplots(
        rows=2, 
        cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        row_heights=[0.7, 0.3],
        subplot_titles=["Carga de Treino", "Balanço (TSB)"]
    )
    
    # Adiciona barras de TSS
    fig.add_trace(
        go.Bar(
            x=df[date_col],
            y=df[tss_col],
            name="TSS",
            marker_color=THEME_COLORS["info"] + "80",  # Adiciona transparência
            hovertemplate="Data: %{x}<br>TSS: %{y:.0f}<extra></extra>"
        ),
        row=1, col=1
    )
    
    # Adiciona linha de CTL
    fig.add_trace(
        go.Scatter(
            x=df[date_col],
            y=df[ctl_col],
            name="CTL (Crônica)",
            line=dict(color=THEME_COLORS["success"], width=2),
            hovertemplate="Data: %{x}<br>CTL: %{y:.1f}<extra></extra>"
        ),
        row=1, col=1
    )
    
    # Adiciona linha de ATL
    fig.add_trace(
        go.Scatter(
            x=df[date_col],
            y=df[atl_col],
            name="ATL (Aguda)",
            line=dict(color=THEME_COLORS["danger"], width=2),
            hovertemplate="Data: %{x}<br>ATL: %{y:.1f}<extra></extra>"
        ),
        row=1, col=1
    )
    
    # Adiciona área de TSB
    fig.add_trace(
        go.Scatter(
            x=df[date_col],
            y=df[tsb_col],
            name="TSB",
            fill='tozeroy',
            line=dict(color=THEME_COLORS["primary"], width=2),
            fillcolor=THEME_COLORS["primary"] + "40",  # Adiciona transparência
            hovertemplate="Data: %{x}<br>TSB: %{y:.1f}<extra></extra>"
        ),
        row=2, col=1
    )
    
    # Adiciona linha de referência em TSB = 0
    fig.add_shape(
        type="line",
        xref="x2",
        yref="y2",
        x0=df[date_col].iloc[0],
        x1=df[date_col].iloc[-1],
        y0=0,
        y1=0,
        line=dict(color="white", width=1, dash="dash"),
        row=2, col=1
    )
    
    # Configurações de layout
    fig.update_layout(
        title=title,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        font=dict(family="Arial, sans-serif", size=12, color=THEME_COLORS["text"]),
        hovermode="x unified"
    )
    
    # Configurações de eixos
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(255,255,255,0.1)",
        showline=True,
        linewidth=1,
        linecolor="rgba(255,255,255,0.3)"
    )
    
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(255,255,255,0.1)",
        showline=True,
        linewidth=1,
        linecolor="rgba(255,255,255,0.3)"
    )
    
    return fig

def create_monotony_strain_chart(df, date_col='date_only', monotony_col='monotony', 
                                 strain_col='strain', title="Monotonia e Strain"):
    """
    Cria um gráfico combinado de Monotonia e Strain.
    
    Args:
        df (DataFrame): DataFrame com os dados
        date_col (str): Nome da coluna de data
        monotony_col (str): Nome da coluna de monotonia
        strain_col (str): Nome da coluna de strain
        title (str): Título do gráfico
    
    Returns:
        Figure: Objeto de figura do Plotly
    """
    # Cria o gráfico com subplots
    fig = make_subplots(
        rows=1, 
        cols=1,
        specs=[[{"secondary_y": True}]]
    )
    
    # Adiciona linha de Monotonia
    fig.add_trace(
        go.Scatter(
            x=df[date_col],
            y=df[monotony_col],
            name="Monotonia",
            line=dict(color=THEME_COLORS["warning"], width=2),
            hovertemplate="Data: %{x}<br>Monotonia: %{y:.2f}<extra></extra>"
        ),
        secondary_y=False
    )
    
    # Adiciona linha de Strain
    fig.add_trace(
        go.Scatter(
            x=df[date_col],
            y=df[strain_col],
            name="Strain",
            line=dict(color=THEME_COLORS["danger"], width=2),
            hovertemplate="Data: %{x}<br>Strain: %{y:.0f}<extra></extra>"
        ),
        secondary_y=True
    )
    
    # Adiciona faixas de referência para Monotonia
    monotony_ranges = [
        {"y0": 0, "y1": 1.0, "color": THEME_COLORS["success"], "label": "Ideal"},
        {"y0": 1.0, "y1": 1.5, "color": THEME_COLORS["warning"], "label": "Moderada"},
        {"y0": 1.5, "y1": 2.5, "color": THEME_COLORS["danger"], "label": "Alta"}
    ]
    
    for range_info in monotony_ranges:
        fig.add_shape(
            type="rect",
            xref="paper",
            yref="y",
            x0=0,
            x1=1,
            y0=range_info["y0"],
            y1=range_info["y1"],
            fillcolor=range_info["color"] + "20",  # Adiciona transparência
            line=dict(width=0),
            layer="below"
        )
    
    # Configurações de layout
    fig.update_layout(
        title=title,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        font=dict(family="Arial, sans-serif", size=12, color=THEME_COLORS["text"]),
        hovermode="x unified"
    )
    
    # Configurações de eixos
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(255,255,255,0.1)",
        showline=True,
        linewidth=1,
        linecolor="rgba(255,255,255,0.3)"
    )
    
    fig.update_yaxes(
        title_text="Monotonia",
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(255,255,255,0.1)",
        showline=True,
        linewidth=1,
        linecolor="rgba(255,255,255,0.3)",
        secondary_y=False
    )
    
    fig.update_yaxes(
        title_text="Strain",
        showgrid=False,
        showline=True,
        linewidth=1,
        linecolor="rgba(255,255,255,0.3)",
        secondary_y=True
    )
    
    return fig

def create_readiness_components_chart(df, date_col='date_only', components=None, 
                                      title="Componentes de Prontidão"):
    """
    Cria um gráfico de componentes de prontidão.
    
    Args:
        df (DataFrame): DataFrame com os dados
        date_col (str): Nome da coluna de data
        components (dict): Dicionário com nomes de colunas e rótulos
        title (str): Título do gráfico
    
    Returns:
        Figure: Objeto de figura do Plotly
    """
    if components is None:
        components = {
            'sleep_quality': 'Qualidade do Sono',
            'sleep_duration': 'Duração do Sono',
            'stress': 'Estresse',
            'fatigue': 'Fadiga',
            'muscle_soreness': 'Dor Muscular',
            'energy': 'Energia',
            'motivation': 'Motivação'
        }
    
    # Cria o gráfico base
    fig = go.Figure()
    
    # Paleta de cores
    colors = generate_color_palette(THEME_COLORS["primary"], len(components), "qualitative")
    
    # Adiciona uma linha para cada componente
    for i, (col, label) in enumerate(components.items()):
        if col in df.columns:
            fig.add_trace(
                go.Scatter(
                    x=df[date_col],
                    y=df[col],
                    name=label,
                    line=dict(color=colors[i], width=2),
                    hovertemplate=f"Data: %{{x}}<br>{label}: %{{y}}<extra></extra>"
                )
            )
    
    # Configurações de layout
    fig.update_layout(
        title=title,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ),
        font=dict(family="Arial, sans-serif", size=12, color=THEME_COLORS["text"]),
        hovermode="x unified"
    )
    
    # Configurações de eixos
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(255,255,255,0.1)",
        showline=True,
        linewidth=1,
        linecolor="rgba(255,255,255,0.3)"
    )
    
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(255,255,255,0.1)",
        showline=True,
        linewidth=1,
        linecolor="rgba(255,255,255,0.3)"
    )
    
    return fig

def create_correlation_matrix_chart(df, columns=None, labels=None, title="Matriz de Correlação"):
    """
    Cria uma matriz de correlação.
    
    Args:
        df (DataFrame): DataFrame com os dados
        columns (list): Lista de colunas para incluir na matriz
        labels (dict): Dicionário mapeando nomes de colunas para rótulos
        title (str): Título do gráfico
    
    Returns:
        Figure: Objeto de figura do Plotly
    """
    # Filtra as colunas se especificado
    if columns:
        df_corr = df[columns].copy()
    else:
        df_corr = df.select_dtypes(include=['number']).copy()
    
    # Renomeia as colunas se especificado
    if labels:
        df_corr = df_corr.rename(columns=labels)
    
    # Calcula a matriz de correlação
    corr_matrix = df_corr.corr()
    
    # Cria o mapa de calor
    fig = go.Figure(
        data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale=[
                [0, THEME_COLORS["danger"]],
                [0.5, "#FFFFFF"],
                [1, THEME_COLORS["success"]]
            ],
            zmin=-1,
            zmax=1,
            zmid=0,
            text=corr_matrix.values,
            texttemplate="%{text:.2f}",
            textfont=dict(color="black", size=10),
            hovertemplate="X: %{x}<br>Y: %{y}<br>Correlação: %{z:.2f}<extra></extra>"
        )
    )
    
    # Configurações de layout
    fig.update_layout(
        title=title,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis_title=None,
        yaxis_title=None,
        font=dict(family="Arial, sans-serif", size=12, color=THEME_COLORS["text"])
    )
    
    return fig

def create_variable_comparison_chart(df, x_col, y_col, date_col='date_only', 
                                     x_label=None, y_label=None, title=None,
                                     show_correlation=True, show_trendline=True):
    """
    Cria um gráfico de comparação entre duas variáveis.
    
    Args:
        df (DataFrame): DataFrame com os dados
        x_col (str): Nome da coluna para o eixo X
        y_col (str): Nome da coluna para o eixo Y
        date_col (str): Nome da coluna de data
        x_label (str): Rótulo para o eixo X
        y_label (str): Rótulo para o eixo Y
        title (str): Título do gráfico
        show_correlation (bool): Se deve mostrar o coeficiente de correlação
        show_trendline (bool): Se deve mostrar a linha de tendência
    
    Returns:
        Figure: Objeto de figura do Plotly
    """
    # Cria o gráfico com subplots
    fig = make_subplots(
        rows=2, 
        cols=2,
        specs=[
            [{"colspan": 2}, None],
            [{"type": "scatter"}, {"type": "scatter"}]
        ],
        subplot_titles=["Evolução Temporal", "Correlação", "Distribuição X", "Distribuição Y"],
        row_heights=[0.6, 0.4],
        column_widths=[0.6, 0.4],
        vertical_spacing=0.1,
        horizontal_spacing=0.1
    )
    
    # Adiciona linhas de evolução temporal
    fig.add_trace(
        go.Scatter(
            x=df[date_col],
            y=df[x_col],
            name=x_label if x_label else x_col,
            line=dict(color=THEME_COLORS["primary"], width=2),
            hovertemplate=f"Data: %{{x}}<br>{x_label if x_label else x_col}: %{{y}}<extra></extra>"
        ),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(
            x=df[date_col],
            y=df[y_col],
            name=y_label if y_label else y_col,
            line=dict(color=THEME_COLORS["secondary"], width=2),
            hovertemplate=f"Data: %{{x}}<br>{y_label if y_label else y_col}: %{{y}}<extra></extra>"
        ),
        row=1, col=1
    )
    
    # Adiciona gráfico de dispersão para correlação
    fig.add_trace(
        go.Scatter(
            x=df[x_col],
            y=df[y_col],
            mode='markers',
            marker=dict(
                color=THEME_COLORS["info"],
                size=8,
                opacity=0.7
            ),
            name="Correlação",
            hovertemplate=f"{x_label if x_label else x_col}: %{{x}}<br>{y_label if y_label else y_col}: %{{y}}<extra></extra>"
        ),
        row=2, col=1
    )
    
    # Adiciona linha de tendência
    if show_trendline and len(df) > 1:
        # Calcula a regressão linear
        x = df[x_col].values
        y = df[y_col].values
        mask = ~np.isnan(x) & ~np.isnan(y)
        
        if sum(mask) > 1:  # Precisa de pelo menos 2 pontos
            x_valid = x[mask]
            y_valid = y[mask]
            
            coeffs = np.polyfit(x_valid, y_valid, 1)
            trend_line = coeffs[0] * x_valid + coeffs[1]
            
            # Adiciona a linha de tendência
            fig.add_trace(
                go.Scatter(
                    x=x_valid,
                    y=trend_line,
                    mode='lines',
                    line=dict(color=THEME_COLORS["warning"], width=2, dash='dash'),
                    name='Tendência',
                    hoverinfo='skip'
                ),
                row=2, col=1
            )
    
    # Adiciona histograma para X
    fig.add_trace(
        go.Histogram(
            x=df[x_col],
            marker_color=THEME_COLORS["primary"],
            opacity=0.7,
            name=x_label if x_label else x_col,
            hovertemplate=f"{x_label if x_label else x_col}: %{{x}}<br>Contagem: %{{y}}<extra></extra>"
        ),
        row=2, col=2
    )
    
    # Adiciona histograma para Y
    fig.add_trace(
        go.Histogram(
            y=df[y_col],
            marker_color=THEME_COLORS["secondary"],
            opacity=0.7,
            name=y_label if y_label else y_col,
            hovertemplate=f"{y_label if y_label else y_col}: %{{y}}<br>Contagem: %{{x}}<extra></extra>"
        ),
        row=2, col=2
    )
    
    # Adiciona anotação de correlação
    if show_correlation:
        corr = df[[x_col, y_col]].corr().iloc[0, 1]
        
        fig.add_annotation(
            xref="x2",
            yref="y2",
            x=df[x_col].min() + (df[x_col].max() - df[x_col].min()) * 0.05,
            y=df[y_col].max() - (df[y_col].max() - df[y_col].min()) * 0.05,
            text=f"Correlação: {corr:.2f}",
            showarrow=False,
            font=dict(
                color=THEME_COLORS["text"],
                size=12
            ),
            bgcolor="rgba(0,0,0,0.5)",
            bordercolor=THEME_COLORS["text"],
            borderwidth=1,
            borderpad=4
        )
    
    # Configurações de layout
    fig.update_layout(
        title=title,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=50, b=10),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        font=dict(family="Arial, sans-serif", size=12, color=THEME_COLORS["text"]),
        hovermode="closest"
    )
    
    # Configurações de eixos
    fig.update_xaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(255,255,255,0.1)",
        showline=True,
        linewidth=1,
        linecolor="rgba(255,255,255,0.3)"
    )
    
    fig.update_yaxes(
        showgrid=True,
        gridwidth=1,
        gridcolor="rgba(255,255,255,0.1)",
        showline=True,
        linewidth=1,
        linecolor="rgba(255,255,255,0.3)"
    )
    
    # Rótulos dos eixos
    fig.update_xaxes(title_text=x_label if x_label else x_col, row=2, col=1)
    fig.update_yaxes(title_text=y_label if y_label else y_col, row=2, col=1)
    
    return fig

# Funções de visualização para Streamlit

def st_metric_card(title, value, delta=None, delta_color="normal", 
                   description=None, icon=None, color=None):
    """
    Cria um card de métrica personalizado para Streamlit.
    
    Args:
        title (str): Título da métrica
        value (str/float): Valor da métrica
        delta (str/float): Variação da métrica
        delta_color (str): Cor da variação ('normal', 'inverse', 'off')
        description (str): Descrição adicional
        icon (str): Ícone para exibir
        color (str): Cor de destaque
    """
    if color is None:
        color = THEME_COLORS["primary"]
    
    # Cria o card com CSS personalizado
    st.markdown(
        f"""
        <div style="
            background-color: rgba(255, 255, 255, 0.05);
            border-left: 5px solid {color};
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 10px;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <h3 style="margin: 0; color: rgba(255, 255, 255, 0.7); font-size: 0.9rem;">
                    {icon + ' ' if icon else ''}{title}
                </h3>
                {f'<span style="color: {color}; font-size: 0.8rem;">{delta}</span>' if delta else ''}
            </div>
            <div style="font-size: 1.8rem; font-weight: bold; margin: 10px 0;">
                {value}
            </div>
            {f'<div style="color: rgba(255, 255, 255, 0.6); font-size: 0.8rem;">{description}</div>' if description else ''}
        </div>
        """,
        unsafe_allow_html=True
    )

def st_info_card(title, content, icon=None, color=None):
    """
    Cria um card informativo personalizado para Streamlit.
    
    Args:
        title (str): Título do card
        content (str): Conteúdo do card
        icon (str): Ícone para exibir
        color (str): Cor de destaque
    """
    if color is None:
        color = THEME_COLORS["info"]
    
    # Cria o card com CSS personalizado
    st.markdown(
        f"""
        <div style="
            background-color: rgba(255, 255, 255, 0.05);
            border-left: 5px solid {color};
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 10px;
        ">
            <h3 style="margin: 0; color: rgba(255, 255, 255, 0.7); font-size: 1rem;">
                {icon + ' ' if icon else ''}{title}
            </h3>
            <div style="color: rgba(255, 255, 255, 0.9); font-size: 0.9rem; margin-top: 10px;">
                {content}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def st_progress_bar(value, min_val=0, max_val=100, label=None, color=None, 
                    show_percentage=True, height=20):
    """
    Cria uma barra de progresso personalizada para Streamlit.
    
    Args:
        value (float): Valor atual
        min_val (float): Valor mínimo
        max_val (float): Valor máximo
        label (str): Rótulo da barra
        color (str): Cor da barra
        show_percentage (bool): Se deve mostrar o percentual
        height (int): Altura da barra em pixels
    """
    if color is None:
        color = THEME_COLORS["primary"]
    
    # Normaliza o valor
    normalized = max(0, min(100, (value - min_val) / (max_val - min_val) * 100))
    
    # Cria a barra com CSS personalizado
    st.markdown(
        f"""
        <div style="margin-bottom: 10px;">
            {f'<div style="margin-bottom: 5px; color: rgba(255, 255, 255, 0.7);">{label}</div>' if label else ''}
            <div style="
                background-color: rgba(255, 255, 255, 0.1);
                border-radius: 5px;
                height: {height}px;
                position: relative;
            ">
                <div style="
                    background-color: {color};
                    width: {normalized}%;
                    height: 100%;
                    border-radius: 5px;
                    transition: width 0.5s;
                "></div>
                {f'<div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); color: white;">{normalized:.0f}%</div>' if show_percentage else ''}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def st_section_header(title, description=None, icon=None):
    """
    Cria um cabeçalho de seção personalizado para Streamlit.
    
    Args:
        title (str): Título da seção
        description (str): Descrição da seção
        icon (str): Ícone para exibir
    """
    # Cria o cabeçalho com CSS personalizado
    st.markdown(
        f"""
        <div style="margin-bottom: 20px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); padding-bottom: 10px;">
            <h2 style="margin: 0; color: white; font-size: 1.5rem;">
                {icon + ' ' if icon else ''}{title}
            </h2>
            {f'<div style="color: rgba(255, 255, 255, 0.7); font-size: 0.9rem; margin-top: 5px;">{description}</div>' if description else ''}
        </div>
        """,
        unsafe_allow_html=True
    )

def st_tabs(tab_labels):
    """
    Cria abas personalizadas para Streamlit.
    
    Args:
        tab_labels (list): Lista de rótulos das abas
    
    Returns:
        list: Lista de objetos de aba
    """
    # Usa a função de abas nativa do Streamlit
    return st.tabs(tab_labels)

def st_sidebar_menu(items, active_index=0):
    """
    Cria um menu de navegação na barra lateral do Streamlit.
    
    Args:
        items (list): Lista de dicionários com 'label', 'icon' e 'url'
        active_index (int): Índice do item ativo
    
    Returns:
        str: URL do item selecionado
    """
    # Cria o menu com CSS personalizado
    st.sidebar.markdown(
        """
        <style>
        .sidebar-menu {
            margin-bottom: 20px;
        }
        .sidebar-menu-item {
            padding: 10px 15px;
            border-radius: 5px;
            margin-bottom: 5px;
            cursor: pointer;
            transition: background-color 0.3s;
            display: flex;
            align-items: center;
        }
        .sidebar-menu-item:hover {
            background-color: rgba(255, 255, 255, 0.1);
        }
        .sidebar-menu-item.active {
            background-color: rgba(255, 255, 255, 0.2);
            font-weight: bold;
        }
        .sidebar-menu-icon {
            margin-right: 10px;
            width: 20px;
            text-align: center;
        }
        </style>
        <div class="sidebar-menu">
        """,
        unsafe_allow_html=True
    )
    
    selected = None
    
    for i, item in enumerate(items):
        is_active = i == active_index
        
        if st.sidebar.button(
            f"{item['icon']} {item['label']}" if 'icon' in item else item['label'],
            key=f"menu_item_{i}",
            help=item.get('tooltip', ''),
            use_container_width=True
        ):
            selected = item['url']
    
    st.sidebar.markdown("</div>", unsafe_allow_html=True)
    
    return selected

def st_data_table(df, height=None, selection='single', key=None):
    """
    Cria uma tabela de dados personalizada para Streamlit.
    
    Args:
        df (DataFrame): DataFrame com os dados
        height (int): Altura da tabela em pixels
        selection (str): Tipo de seleção ('single', 'multi', None)
        key (str): Chave única para o componente
    
    Returns:
        DataFrame: DataFrame com as linhas selecionadas
    """
    # Usa a função de tabela de dados nativa do Streamlit
    return st.dataframe(
        df,
        height=height,
        use_container_width=True,
        hide_index=True
    )

def st_date_range_selector(default_days=30, key=None):
    """
    Cria um seletor de intervalo de datas para Streamlit.
    
    Args:
        default_days (int): Número de dias padrão para o intervalo
        key (str): Chave única para o componente
    
    Returns:
        tuple: Data de início e fim selecionadas
    """
    today = datetime.now().date()
    default_start = today - timedelta(days=default_days)
    
    col1, col2 = st.columns(2)
    
    with col1:
        start_date = st.date_input(
            "Data de Início",
            default_start,
            key=f"{key}_start" if key else None
        )
    
    with col2:
        end_date = st.date_input(
            "Data de Fim",
            today,
            key=f"{key}_end" if key else None
        )
    
    # Garante que a data de início não seja posterior à data de fim
    if start_date > end_date:
        st.error("Erro: A data de início não pode ser posterior à data de fim.")
        start_date = end_date - timedelta(days=1)
    
    return start_date, end_date
