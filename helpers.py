"""
Módulo de funções auxiliares para o Sistema de Monitoramento do Atleta
---------------------------------------------------------------------
Este módulo contém funções utilitárias diversas usadas em todo o sistema.
"""

import streamlit as st
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

def format_date(date_str, format_out="%d/%m/%Y"):
    """
    Formata uma string de data para o formato desejado.
    
    Args:
        date_str (str): String de data no formato ISO
        format_out (str): Formato de saída desejado
    
    Returns:
        str: Data formatada
    """
    try:
        if isinstance(date_str, str):
            date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return date_obj.strftime(format_out)
        elif isinstance(date_str, datetime):
            return date_str.strftime(format_out)
        return str(date_str)
    except:
        return str(date_str)

def get_trend_icon(value, threshold=0):
    """
    Retorna um ícone de tendência com base no valor.
    
    Args:
        value (float): Valor da tendência
        threshold (float): Limiar para considerar neutro
    
    Returns:
        str: Ícone de tendência (↑, ↓, ou →)
    """
    if value > threshold:
        return "↑"
    elif value < -threshold:
        return "↓"
    else:
        return "→"

def get_date_range(days=7):
    """
    Obtém um intervalo de datas até hoje.
    
    Args:
        days (int): Número de dias no passado
    
    Returns:
        list: Lista de objetos datetime
    """
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days-1)
    
    date_range = []
    current_date = start_date
    
    while current_date <= end_date:
        date_range.append(current_date)
        current_date += timedelta(days=1)
    
    return date_range

def get_date_labels(dates, format="%d/%m"):
    """
    Converte uma lista de datas em rótulos formatados.
    
    Args:
        dates (list): Lista de objetos datetime
        format (str): Formato de saída
    
    Returns:
        list: Lista de strings de data formatadas
    """
    return [d.strftime(format) for d in dates]

def calculate_weekly_trimp(training_data):
    """
    Calcula o TRIMP semanal a partir dos dados de treino.
    
    Args:
        training_data (list): Lista de registros de treino
    
    Returns:
        float: Soma do TRIMP na semana
    """
    if not training_data:
        return 0
    
    # Converte para DataFrame para facilitar a manipulação
    df = pd.DataFrame(training_data)
    
    # Se não houver coluna 'trimp', calcula a partir de duração e RPE
    if 'trimp' not in df.columns and 'duration' in df.columns and 'rpe' in df.columns:
        df['trimp'] = df['duration'] * df['rpe']
    
    # Retorna a soma do TRIMP
    if 'trimp' in df.columns:
        return df['trimp'].sum()
    
    return 0

def calculate_readiness_score(assessment_data):
    """
    Calcula o score de prontidão (0-100) a partir dos dados de avaliação.
    
    Args:
        assessment_data (dict): Dados da avaliação de prontidão
    
    Returns:
        int: Score de prontidão (0-100)
    """
    if not assessment_data:
        return 0
    
    # Pesos para cada componente (total = 100)
    weights = {
        'sleep_quality': 20,
        'sleep_duration': 15,
        'stress_level': 15,
        'muscle_soreness': 15,
        'energy_level': 15,
        'motivation': 10,
        'nutrition_quality': 5,
        'hydration': 5
    }
    
    # Inicializa o score
    score = 0
    
    # Calcula o score ponderado
    for component, weight in weights.items():
        if component in assessment_data:
            # Normaliza para escala 0-100
            # Assume que os valores estão em escala 1-5
            normalized_value = (assessment_data[component] / 5) * 100
            score += (normalized_value * weight / 100)
    
    # Arredonda para inteiro
    return round(score)

def calculate_stress_level(psychological_data):
    """
    Calcula o nível de estresse a partir dos dados psicológicos.
    
    Args:
        psychological_data (dict): Dados da avaliação psicológica
    
    Returns:
        str: Nível de estresse (Baixo, Moderado, Alto)
    """
    if not psychological_data or 'dass_stress' not in psychological_data:
        return "Não avaliado"
    
    stress_score = psychological_data['dass_stress']
    
    # Classificação baseada no DASS-21
    if stress_score <= 14:
        return "Baixo"
    elif stress_score <= 25:
        return "Moderado"
    else:
        return "Alto"

def calculate_goal_progress(current_value, target_value, goal_type="maximize"):
    """
    Calcula o progresso percentual em relação a uma meta.
    
    Args:
        current_value (float): Valor atual
        target_value (float): Valor alvo
        goal_type (str): Tipo de meta ('maximize' ou 'minimize')
    
    Returns:
        float: Progresso percentual (0-100)
    """
    if goal_type == "maximize":
        # Para metas de maximização (ex: aumentar prontidão)
        if target_value <= 0:
            return 100 if current_value >= 0 else 0
        
        progress = (current_value / target_value) * 100
        return min(100, max(0, progress))
    
    else:
        # Para metas de minimização (ex: reduzir estresse)
        if current_value <= target_value:
            return 100
        
        # Assume um valor máximo como referência (2x o alvo)
        max_value = target_value * 2
        
        if current_value >= max_value:
            return 0
        
        # Calcula o progresso inverso
        progress = ((max_value - current_value) / (max_value - target_value)) * 100
        return min(100, max(0, progress))

def get_color_for_value(value, scale_type="readiness"):
    """
    Retorna uma cor com base no valor e na escala.
    
    Args:
        value (float): Valor a ser avaliado
        scale_type (str): Tipo de escala ('readiness', 'stress', etc.)
    
    Returns:
        str: Código de cor hexadecimal
    """
    if scale_type == "readiness":
        # Escala de prontidão (0-100)
        if value >= 80:
            return "#4CAF50"  # Verde
        elif value >= 60:
            return "#8BC34A"  # Verde claro
        elif value >= 40:
            return "#FFC107"  # Amarelo
        elif value >= 20:
            return "#FF9800"  # Laranja
        else:
            return "#F44336"  # Vermelho
    
    elif scale_type == "stress":
        # Escala de estresse (texto)
        if value == "Baixo":
            return "#4CAF50"  # Verde
        elif value == "Moderado":
            return "#FFC107"  # Amarelo
        elif value == "Alto":
            return "#F44336"  # Vermelho
        else:
            return "#9E9E9E"  # Cinza
    
    elif scale_type == "trimp":
        # Escala de TRIMP (valor numérico)
        # Valores são contextuais, ajuste conforme necessário
        if value < 300:
            return "#8BC34A"  # Verde claro (carga baixa)
        elif value < 500:
            return "#4CAF50"  # Verde (carga ideal)
        elif value < 700:
            return "#FFC107"  # Amarelo (carga moderada)
        elif value < 900:
            return "#FF9800"  # Laranja (carga alta)
        else:
            return "#F44336"  # Vermelho (sobrecarga)
    
    # Escala padrão
    return "#1E88E5"  # Azul
