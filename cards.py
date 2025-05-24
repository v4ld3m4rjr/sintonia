"""
Componentes de cards para o Sistema de Monitoramento do Atleta
-------------------------------------------------------------
Este módulo contém funções para criar cards de métricas e informações.
"""

import streamlit as st
from utils.helpers import get_trend_icon, get_color_for_value

def metric_card(title, value, delta="", is_positive=None, neutral=False, description=""):
    """
    Cria um card de métrica com título, valor e tendência.
    
    Args:
        title (str): Título da métrica
        value (str): Valor principal da métrica
        delta (str): Valor de variação (ex: "5%")
        is_positive (bool): Se a variação é positiva (True) ou negativa (False)
        neutral (bool): Se a métrica deve ser exibida em cor neutra
        description (str): Descrição adicional da métrica
    """
    # Define cores com base no contexto
    if neutral:
        color = "#1E88E5"  # Azul
        bg_color = "#E3F2FD"  # Azul claro
    elif is_positive is not None:
        if is_positive:
            color = "#4CAF50"  # Verde
            bg_color = "#E8F5E9"  # Verde claro
        else:
            color = "#F44336"  # Vermelho
            bg_color = "#FFEBEE"  # Vermelho claro
    else:
        color = "#1E88E5"  # Azul
        bg_color = "#E3F2FD"  # Azul claro
    
    # Ícone de tendência
    if delta:
        if is_positive is not None:
            trend_icon = "↑" if is_positive else "↓"
        else:
            trend_icon = ""
    else:
        trend_icon = ""
    
    # Estilo CSS para o card
    card_style = f"""
    <style>
    .metric-card {{
        background-color: {bg_color};
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 10px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }}
    .metric-title {{
        color: #424242;
        font-size: 16px;
        font-weight: 500;
        margin-bottom: 10px;
    }}
    .metric-value {{
        color: {color};
        font-size: 28px;
        font-weight: 700;
        margin-bottom: 5px;
    }}
    .metric-delta {{
        color: {color};
        font-size: 14px;
        font-weight: 500;
        margin-bottom: 10px;
    }}
    .metric-description {{
        color: #616161;
        font-size: 14px;
        font-style: italic;
    }}
    </style>
    """
    
    # HTML do card
    card_html = f"""
    <div class="metric-card">
        <div class="metric-title">{title}</div>
        <div class="metric-value">{value}</div>
        <div class="metric-delta">{trend_icon} {delta}</div>
        <div class="metric-description">{description}</div>
    </div>
    """
    
    # Renderiza o card
    st.markdown(card_style + card_html, unsafe_allow_html=True)

def info_card(title, content, icon="ℹ️", color="#1E88E5"):
    """
    Cria um card informativo com título e conteúdo.
    
    Args:
        title (str): Título do card
        content (str): Conteúdo do card
        icon (str): Ícone para o card
        color (str): Cor principal do card
    """
    # Estilo CSS para o card
    card_style = f"""
    <style>
    .info-card {{
        background-color: white;
        border-left: 5px solid {color};
        border-radius: 5px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }}
    .info-title {{
        color: {color};
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 10px;
        display: flex;
        align-items: center;
    }}
    .info-icon {{
        margin-right: 10px;
        font-size: 20px;
    }}
    .info-content {{
        color: #424242;
        font-size: 15px;
        line-height: 1.5;
    }}
    </style>
    """
    
    # HTML do card
    card_html = f"""
    <div class="info-card">
        <div class="info-title">
            <span class="info-icon">{icon}</span>
            {title}
        </div>
        <div class="info-content">{content}</div>
    </div>
    """
    
    # Renderiza o card
    st.markdown(card_style + card_html, unsafe_allow_html=True)

def recommendation_card(title, recommendations, color="#4CAF50"):
    """
    Cria um card de recomendações com título e lista de itens.
    
    Args:
        title (str): Título do card
        recommendations (list): Lista de recomendações
        color (str): Cor principal do card
    """
    # Estilo CSS para o card
    card_style = f"""
    <style>
    .recommendation-card {{
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }}
    .recommendation-title {{
        color: {color};
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 15px;
        padding-bottom: 10px;
        border-bottom: 1px solid #E0E0E0;
    }}
    .recommendation-list {{
        color: #424242;
        font-size: 15px;
        line-height: 1.6;
    }}
    .recommendation-item {{
        margin-bottom: 10px;
        display: flex;
    }}
    .recommendation-bullet {{
        color: {color};
        margin-right: 10px;
        font-weight: bold;
    }}
    </style>
    """
    
    # Gera os itens da lista de recomendações
    items_html = ""
    for rec in recommendations:
        items_html += f"""
        <div class="recommendation-item">
            <div class="recommendation-bullet">•</div>
            <div>{rec}</div>
        </div>
        """
    
    # HTML do card
    card_html = f"""
    <div class="recommendation-card">
        <div class="recommendation-title">{title}</div>
        <div class="recommendation-list">
            {items_html}
        </div>
    </div>
    """
    
    # Renderiza o card
    st.markdown(card_style + card_html, unsafe_allow_html=True)

def goal_progress_card(goal_name, current_value, target_value, progress_pct, description=""):
    """
    Cria um card de progresso de meta com barra de progresso.
    
    Args:
        goal_name (str): Nome da meta
        current_value (str): Valor atual
        target_value (str): Valor alvo
        progress_pct (float): Percentual de progresso (0-100)
        description (str): Descrição adicional
    """
    # Define a cor com base no progresso
    if progress_pct >= 80:
        color = "#4CAF50"  # Verde
    elif progress_pct >= 50:
        color = "#8BC34A"  # Verde claro
    elif progress_pct >= 30:
        color = "#FFC107"  # Amarelo
    else:
        color = "#FF9800"  # Laranja
    
    # Estilo CSS para o card
    card_style = f"""
    <style>
    .goal-card {{
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }}
    .goal-title {{
        color: #424242;
        font-size: 16px;
        font-weight: 600;
        margin-bottom: 10px;
    }}
    .goal-progress-container {{
        background-color: #F5F5F5;
        border-radius: 5px;
        height: 10px;
        margin-bottom: 10px;
        overflow: hidden;
    }}
    .goal-progress-bar {{
        background-color: {color};
        height: 100%;
        width: {progress_pct}%;
    }}
    .goal-values {{
        display: flex;
        justify-content: space-between;
        color: #616161;
        font-size: 14px;
        margin-bottom: 10px;
    }}
    .goal-description {{
        color: #757575;
        font-size: 14px;
        font-style: italic;
    }}
    </style>
    """
    
    # HTML do card
    card_html = f"""
    <div class="goal-card">
        <div class="goal-title">{goal_name}</div>
        <div class="goal-progress-container">
            <div class="goal-progress-bar"></div>
        </div>
        <div class="goal-values">
            <div>{current_value}</div>
            <div>{int(progress_pct)}%</div>
            <div>{target_value}</div>
        </div>
        <div class="goal-description">{description}</div>
    </div>
    """
    
    # Renderiza o card
    st.markdown(card_style + card_html, unsafe_allow_html=True)
