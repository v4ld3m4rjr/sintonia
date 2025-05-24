"""
Módulo de Dashboard Avançado para o Sistema de Monitoramento do Atleta
---------------------------------------------------------------------
Este módulo permite ao atleta visualizar gráficos personalizáveis e análises avançadas.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
from PIL import Image

# Adiciona os diretórios ao path para importação dos módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importa os módulos de utilidades
from utils.auth import check_authentication
from utils.database import get_readiness_data, get_training_data, get_psychological_data
from utils.helpers import format_date, get_date_range, get_date_labels
from utils.training_load import (
    calculate_tss_from_rpe, calculate_ctl, calculate_atl, calculate_tsb,
    calculate_monotony, calculate_strain, calculate_readiness_from_tsb,
    get_training_load_zone, get_tsb_zone
)
from utils.scale_descriptions import (
    get_scale_description, get_readiness_score_description, get_tsb_description,
    get_ctl_description, get_monotony_description, get_strain_description
)

# Importa os componentes reutilizáveis
from components.cards import metric_card, recommendation_card, info_card
from components.charts import create_trend_chart, create_scatter_plot, create_heatmap
from components.navigation import create_sidebar, create_tabs, create_breadcrumbs, create_section_header

# Configuração da página
st.set_page_config(
    page_title="Dashboard Avançado - Sistema de Monitoramento do Atleta",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Verifica autenticação
if not check_authentication():
    st.switch_page("app.py")

# Cria a barra lateral
create_sidebar()

# Título da página
st.title("📈 Dashboard Avançado")
create_breadcrumbs(["Dashboard", "Dashboard Avançado"])

# Função para preparar os dados para análise
def prepare_data(days=30):
    """
    Prepara os dados de prontidão, treino e psicológicos para análise.
    
    Args:
        days (int): Número de dias para buscar dados
    
    Returns:
        tuple: (df_combined, available_metrics)
    """
    # Obtém os dados
    readiness_data = get_readiness_data(st.session_state.user_id, days)
    training_data = get_training_data(st.session_state.user_id, days)
    psychological_data = get_psychological_data(st.session_state.user_id, days)
    
    # Verifica se há dados suficientes
    if not readiness_data and not training_data and not psychological_data:
        return None, []
    
    # Converte para DataFrames
    df_readiness = pd.DataFrame(readiness_data) if readiness_data else pd.DataFrame()
    df_training = pd.DataFrame(training_data) if training_data else pd.DataFrame()
    df_psychological = pd.DataFrame(psychological_data) if psychological_data else pd.DataFrame()
    
    # Garante que a data está no formato correto
    if not df_readiness.empty:
        df_readiness['date'] = pd.to_datetime(df_readiness['date'])
        df_readiness['date_only'] = df_readiness['date'].dt.date
    
    if not df_training.empty:
        df_training['date'] = pd.to_datetime(df_training['date'])
        df_training['date_only'] = df_training['date'].dt.date
        
        # Calcula métricas adicionais de carga
        df_training['tss'] = df_training.apply(
            lambda row: calculate_tss_from_rpe(row['duration'], row['rpe']),
            axis=1
        )
    
    if not df_psychological.empty:
        df_psychological['date'] = pd.to_datetime(df_psychological['date'])
        df_psychological['date_only'] = df_psychological['date'].dt.date
    
    # Cria um DataFrame com todas as datas no período
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days-1)
    date_range = [start_date + timedelta(days=i) for i in range(days)]
    df_dates = pd.DataFrame({'date_only': date_range})
    
    # Prepara DataFrames para merge
    df_readiness_daily = None
    if not df_readiness.empty:
        df_readiness_daily = df_readiness.groupby('date_only').agg({
            'score': 'mean',
            'sleep_quality': 'mean',
            'sleep_duration': 'mean',
            'stress_level': 'mean',
            'muscle_soreness': 'mean',
            'energy_level': 'mean',
            'motivation': 'mean',
            'nutrition_quality': 'mean',
            'hydration': 'mean'
        }).reset_index()
    
    df_training_daily = None
    if not df_training.empty:
        df_training_daily = df_training.groupby('date_only').agg({
            'duration': 'sum',
            'rpe': 'mean',
            'trimp': 'sum',
            'tss': 'sum'
        }).reset_index()
        
        # Calcula métricas avançadas de carga
        # Precisamos de um DataFrame com todas as datas para cálculos corretos
        df_training_all_dates = df_dates.merge(
            df_training_daily, on='date_only', how='left'
        ).fillna(0)
        
        # Calcula CTL, ATL e TSB para cada dia
        df_training_all_dates['ctl'] = df_training_all_dates['tss'].ewm(span=42, adjust=False).mean()
        df_training_all_dates['atl'] = df_training_all_dates['tss'].ewm(span=7, adjust=False).mean()
        df_training_all_dates['tsb'] = df_training_all_dates['ctl'] - df_training_all_dates['atl']
        
        # Calcula monotonia e strain para janelas móveis de 7 dias
        monotony_values = []
        strain_values = []
        
        for i in range(len(df_training_all_dates)):
            if i < 6:  # Primeiros 6 dias não têm dados suficientes
                monotony_values.append(np.nan)
                strain_values.append(np.nan)
            else:
                # Pega os últimos 7 dias
                window = df_training_all_dates.iloc[i-6:i+1]
                
                # Calcula monotonia
                mean_load = window['tss'].mean()
                std_load = window['tss'].std()
                monotony = mean_load / std_load if std_load > 0 else 0
                monotony_values.append(monotony)
                
                # Calcula strain
                weekly_load = window['tss'].sum()
                strain = weekly_load * monotony
                strain_values.append(strain)
        
        df_training_all_dates['monotony'] = monotony_values
        df_training_all_dates['strain'] = strain_values
        
        # Calcula prontidão baseada em TSB
        df_training_all_dates['readiness_tsb'] = df_training_all_dates['tsb'].apply(
            lambda x: calculate_readiness_from_tsb(x)
        )
        
        # Filtra para manter apenas as datas com treinos registrados
        df_training_daily = df_training_all_dates[df_training_all_dates['date_only'].isin(df_training_daily['date_only'])]
    
    df_psychological_daily = None
    if not df_psychological.empty:
        df_psychological_daily = df_psychological.groupby('date_only').agg({
            'dass_anxiety': 'mean',
            'dass_depression': 'mean',
            'dass_stress': 'mean',
            'mood': 'mean',
            'sleep_quality': 'mean'
        }).reset_index()
    
    # Combina os DataFrames
    df_combined = df_dates.copy()
    
    if df_readiness_daily is not None:
        df_combined = df_combined.merge(df_readiness_daily, on='date_only', how='left')
    
    if df_training_daily is not None:
        df_combined = df_combined.merge(df_training_daily, on='date_only', how='left')
    
    if df_psychological_daily is not None:
        df_combined = df_combined.merge(df_psychological_daily, on='date_only', how='left')
    
    # Formata as datas para exibição
    df_combined['date_formatted'] = df_combined['date_only'].apply(lambda x: x.strftime('%d/%m'))
    
    # Lista de métricas disponíveis
    available_metrics = []
    
    # Métricas de prontidão
    if df_readiness_daily is not None:
        available_metrics.extend([
            {'value': 'score', 'label': 'Score de Prontidão', 'group': 'Prontidão', 'color': '#4CAF50'},
            {'value': 'sleep_quality', 'label': 'Qualidade do Sono', 'group': 'Prontidão', 'color': '#8BC34A'},
            {'value': 'sleep_duration', 'label': 'Duração do Sono (h)', 'group': 'Prontidão', 'color': '#CDDC39'},
            {'value': 'stress_level', 'label': 'Nível de Estresse', 'group': 'Prontidão', 'color': '#FFC107'},
            {'value': 'muscle_soreness', 'label': 'Dor Muscular', 'group': 'Prontidão', 'color': '#FF9800'},
            {'value': 'energy_level', 'label': 'Nível de Energia', 'group': 'Prontidão', 'color': '#FF5722'},
            {'value': 'motivation', 'label': 'Motivação', 'group': 'Prontidão', 'color': '#F44336'},
            {'value': 'nutrition_quality', 'label': 'Qualidade da Nutrição', 'group': 'Prontidão', 'color': '#E91E63'},
            {'value': 'hydration', 'label': 'Hidratação', 'group': 'Prontidão', 'color': '#9C27B0'}
        ])
    
    # Métricas de treino
    if df_training_daily is not None:
        available_metrics.extend([
            {'value': 'duration', 'label': 'Duração do Treino (min)', 'group': 'Treino', 'color': '#673AB7'},
            {'value': 'rpe', 'label': 'RPE', 'group': 'Treino', 'color': '#3F51B5'},
            {'value': 'trimp', 'label': 'TRIMP', 'group': 'Treino', 'color': '#2196F3'},
            {'value': 'tss', 'label': 'TSS', 'group': 'Treino', 'color': '#03A9F4'},
            {'value': 'ctl', 'label': 'CTL', 'group': 'Treino', 'color': '#00BCD4'},
            {'value': 'atl', 'label': 'ATL', 'group': 'Treino', 'color': '#009688'},
            {'value': 'tsb', 'label': 'TSB', 'group': 'Treino', 'color': '#4CAF50'},
            {'value': 'monotony', 'label': 'Monotonia', 'group': 'Treino', 'color': '#8BC34A'},
            {'value': 'strain', 'label': 'Strain', 'group': 'Treino', 'color': '#CDDC39'},
            {'value': 'readiness_tsb', 'label': 'Prontidão (TSB)', 'group': 'Treino', 'color': '#FFC107'}
        ])
    
    # Métricas psicológicas
    if df_psychological_daily is not None:
        available_metrics.extend([
            {'value': 'dass_anxiety', 'label': 'Ansiedade', 'group': 'Psicológico', 'color': '#FF9800'},
            {'value': 'dass_depression', 'label': 'Depressão', 'group': 'Psicológico', 'color': '#FF5722'},
            {'value': 'dass_stress', 'label': 'Estresse', 'group': 'Psicológico', 'color': '#F44336'},
            {'value': 'mood', 'label': 'Humor', 'group': 'Psicológico', 'color': '#E91E63'}
        ])
    
    return df_combined, available_metrics

# Função para criar gráfico de tendência personalizado
def create_custom_trend_chart(df, metrics, date_col='date_formatted'):
    """
    Cria um gráfico de tendência personalizado com múltiplas métricas.
    
    Args:
        df (DataFrame): DataFrame com os dados
        metrics (list): Lista de métricas para exibir
        date_col (str): Nome da coluna de data formatada
    
    Returns:
        Figure: Objeto de figura do Plotly
    """
    if df is None or df.empty or not metrics:
        return None
    
    # Cria um gráfico com eixos y secundários se necessário
    use_secondary = len(metrics) > 1
    fig = make_subplots(specs=[[{"secondary_y": use_secondary}]])
    
    # Adiciona cada métrica ao gráfico
    for i, metric in enumerate(metrics):
        # Determina se deve usar o eixo y secundário
        use_secondary_axis = use_secondary and i > 0
        
        # Adiciona a linha
        fig.add_trace(
            go.Scatter(
                x=df[date_col],
                y=df[metric['value']],
                name=metric['label'],
                line=dict(color=metric['color'], width=3),
                mode="lines+markers"
            ),
            secondary_y=use_secondary_axis
        )
        
        # Adiciona faixas de referência para métricas específicas
        if metric['value'] == 'score' or metric['value'] == 'readiness_tsb':
            # Faixas de prontidão
            fig.add_shape(
                type="rect",
                x0=df[date_col].iloc[0],
                x1=df[date_col].iloc[-1],
                y0=0,
                y1=20,
                fillcolor="rgba(244, 67, 54, 0.2)",  # Vermelho
                line=dict(width=0),
                layer="below",
                secondary_y=use_secondary_axis
            )
            fig.add_shape(
                type="rect",
                x0=df[date_col].iloc[0],
                x1=df[date_col].iloc[-1],
                y0=20,
                y1=40,
                fillcolor="rgba(255, 152, 0, 0.2)",  # Laranja
                line=dict(width=0),
                layer="below",
                secondary_y=use_secondary_axis
            )
            fig.add_shape(
                type="rect",
                x0=df[date_col].iloc[0],
                x1=df[date_col].iloc[-1],
                y0=40,
                y1=60,
                fillcolor="rgba(255, 193, 7, 0.2)",  # Amarelo
                line=dict(width=0),
                layer="below",
                secondary_y=use_secondary_axis
            )
            fig.add_shape(
                type="rect",
                x0=df[date_col].iloc[0],
                x1=df[date_col].iloc[-1],
                y0=60,
                y1=80,
                fillcolor="rgba(139, 195, 74, 0.2)",  # Verde claro
                line=dict(width=0),
                layer="below",
                secondary_y=use_secondary_axis
            )
            fig.add_shape(
                type="rect",
                x0=df[date_col].iloc[0],
                x1=df[date_col].iloc[-1],
                y0=80,
                y1=100,
                fillcolor="rgba(76, 175, 80, 0.2)",  # Verde
                line=dict(width=0),
                layer="below",
                secondary_y=use_secondary_axis
            )
        elif metric['value'] == 'tsb':
            # Faixas de TSB
            fig.add_shape(
                type="rect",
                x0=df[date_col].iloc[0],
                x1=df[date_col].iloc[-1],
                y0=-100,
                y1=-30,
                fillcolor="rgba(183, 28, 28, 0.2)",  # Vermelho escuro
                line=dict(width=0),
                layer="below",
                secondary_y=use_secondary_axis
            )
            fig.add_shape(
                type="rect",
                x0=df[date_col].iloc[0],
                x1=df[date_col].iloc[-1],
                y0=-30,
                y1=-15,
                fillcolor="rgba(244, 67, 54, 0.2)",  # Vermelho
                line=dict(width=0),
                layer="below",
                secondary_y=use_secondary_axis
            )
            fig.add_shape(
                type="rect",
                x0=df[date_col].iloc[0],
                x1=df[date_col].iloc[-1],
                y0=-15,
                y1=-5,
                fillcolor="rgba(255, 152, 0, 0.2)",  # Laranja
                line=dict(width=0),
                layer="below",
                secondary_y=use_secondary_axis
            )
            fig.add_shape(
                type="rect",
                x0=df[date_col].iloc[0],
                x1=df[date_col].iloc[-1],
                y0=-5,
                y1=5,
                fillcolor="rgba(76, 175, 80, 0.2)",  # Verde
                line=dict(width=0),
                layer="below",
                secondary_y=use_secondary_axis
            )
            fig.add_shape(
                type="rect",
                x0=df[date_col].iloc[0],
                x1=df[date_col].iloc[-1],
                y0=5,
                y1=15,
                fillcolor="rgba(139, 195, 74, 0.2)",  # Verde claro
                line=dict(width=0),
                layer="below",
                secondary_y=use_secondary_axis
            )
            fig.add_shape(
                type="rect",
                x0=df[date_col].iloc[0],
                x1=df[date_col].iloc[-1],
                y0=15,
                y1=30,
                fillcolor="rgba(255, 193, 7, 0.2)",  # Amarelo
                line=dict(width=0),
                layer="below",
                secondary_y=use_secondary_axis
            )
            fig.add_shape(
                type="rect",
                x0=df[date_col].iloc[0],
                x1=df[date_col].iloc[-1],
                y0=30,
                y1=100,
                fillcolor="rgba(244, 67, 54, 0.2)",  # Vermelho
                line=dict(width=0),
                layer="below",
                secondary_y=use_secondary_axis
            )
        elif metric['value'] == 'ctl':
            # Faixas de CTL (para atleta intermediário)
            fig.add_shape(
                type="rect",
                x0=df[date_col].iloc[0],
                x1=df[date_col].iloc[-1],
                y0=0,
                y1=30,
                fillcolor="rgba(244, 67, 54, 0.2)",  # Vermelho
                line=dict(width=0),
                layer="below",
                secondary_y=use_secondary_axis
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
                secondary_y=use_secondary_axis
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
                secondary_y=use_secondary_axis
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
                secondary_y=use_secondary_axis
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
                secondary_y=use_secondary_axis
            )
        elif metric['value'] == 'monotony':
            # Faixas de Monotonia
            fig.add_shape(
                type="rect",
                x0=df[date_col].iloc[0],
                x1=df[date_col].iloc[-1],
                y0=0,
                y1=1.0,
                fillcolor="rgba(76, 175, 80, 0.2)",  # Verde
                line=dict(width=0),
                layer="below",
                secondary_y=use_secondary_axis
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
                secondary_y=use_secondary_axis
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
                secondary_y=use_secondary_axis
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
                secondary_y=use_secondary_axis
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
    if use_secondary:
        fig.update_yaxes(title_text=metrics[0]['label'], secondary_y=False)
        fig.update_yaxes(title_text=", ".join([m['label'] for m in metrics[1:]]), secondary_y=True)
    else:
        fig.update_yaxes(title_text=metrics[0]['label'], secondary_y=False)
    
    return fig

# Função para criar gráfico de dispersão personalizado
def create_custom_scatter_plot(df, x_metric, y_metric):
    """
    Cria um gráfico de dispersão personalizado para análise de correlação.
    
    Args:
        df (DataFrame): DataFrame com os dados
        x_metric (dict): Métrica para o eixo x
        y_metric (dict): Métrica para o eixo y
    
    Returns:
        Figure: Objeto de figura do Plotly
    """
    if df is None or df.empty:
        return None
    
    # Remove linhas com valores ausentes
    df_clean = df.dropna(subset=[x_metric['value'], y_metric['value']])
    
    if df_clean.empty:
        return None
    
    # Cria o gráfico
    fig = px.scatter(
        df_clean,
        x=x_metric['value'],
        y=y_metric['value'],
        color='date_formatted',
        color_discrete_sequence=px.colors.sequential.Viridis,
        labels={
            x_metric['value']: x_metric['label'],
            y_metric['value']: y_metric['label'],
            'date_formatted': 'Data'
        },
        hover_data=['date_formatted']
    )
    
    # Adiciona linha de tendência
    fig.add_traces(
        px.scatter(
            df_clean, 
            x=x_metric['value'], 
            y=y_metric['value'], 
            trendline='ols'
        ).data[1]
    )
    
    # Calcula correlação
    correlation = df_clean[x_metric['value']].corr(df_clean[y_metric['value']])
    
    # Adiciona anotação com correlação
    fig.add_annotation(
        x=0.95,
        y=0.05,
        xref="paper",
        yref="paper",
        text=f"Correlação: {correlation:.2f}",
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
    
    # Atualiza layout
    fig.update_layout(
        title=f"Correlação entre {x_metric['label']} e {y_metric['label']}",
        xaxis_title=x_metric['label'],
        yaxis_title=y_metric['label'],
        margin=dict(l=20, r=20, t=50, b=20),
        height=500
    )
    
    return fig

# Função para criar matriz de correlação
def create_correlation_matrix(df, metrics):
    """
    Cria uma matriz de correlação entre as métricas selecionadas.
    
    Args:
        df (DataFrame): DataFrame com os dados
        metrics (list): Lista de métricas para incluir
    
    Returns:
        Figure: Objeto de figura do Plotly
    """
    if df is None or df.empty or not metrics:
        return None
    
    # Seleciona apenas as colunas relevantes
    metric_values = [m['value'] for m in metrics]
    df_corr = df[metric_values].copy()
    
    # Remove linhas com valores ausentes
    df_corr = df_corr.dropna()
    
    if df_corr.empty:
        return None
    
    # Calcula a matriz de correlação
    corr_matrix = df_corr.corr()
    
    # Mapeia os nomes das métricas
    metric_map = {m['value']: m['label'] for m in metrics}
    corr_matrix.index = [metric_map[col] for col in corr_matrix.index]
    corr_matrix.columns = [metric_map[col] for col in corr_matrix.columns]
    
    # Cria o heatmap
    fig = px.imshow(
        corr_matrix,
        text_auto='.2f',
        color_continuous_scale='RdBu_r',
        zmin=-1,
        zmax=1,
        aspect="auto"
    )
    
    # Atualiza layout
    fig.update_layout(
        title="Matriz de Correlação",
        margin=dict(l=20, r=20, t=50, b=20),
        height=600
    )
    
    return fig

# Função para exibir gráficos personalizáveis
def show_custom_charts():
    """Exibe gráficos personalizáveis para análise de dados."""
    create_section_header(
        "Gráficos Personalizáveis", 
        "Selecione as variáveis que deseja analisar em conjunto.",
        "📊"
    )
    
    # Opções de período
    period_options = {
        "7 dias": 7,
        "15 dias": 15,
        "30 dias": 30,
        "90 dias": 90,
        "6 meses": 180
    }
    
    selected_period = st.selectbox("Selecione o período", list(period_options.keys()))
    days = period_options[selected_period]
    
    # Prepara os dados
    df, available_metrics = prepare_data(days)
    
    if df is None or not available_metrics:
        info_card(
            "Sem dados",
            "Não há dados suficientes para análise. Registre avaliações de prontidão, treinos e dados psicológicos para visualizar gráficos personalizados.",
            "ℹ️"
        )
        return
    
    # Agrupa métricas por categoria
    metric_groups = {}
    for metric in available_metrics:
        if metric['group'] not in metric_groups:
            metric_groups[metric['group']] = []
        metric_groups[metric['group']].append(metric)
    
    # Cria abas para diferentes tipos de gráficos
    chart_tabs = create_tabs(["Tendências", "Correlações", "Matriz de Correlação"])
    
    # Aba de Tendências
    with chart_tabs[0]:
        st.subheader("Gráfico de Tendências")
        st.write("Selecione até 3 variáveis para visualizar suas tendências ao longo do tempo.")
        
        # Cria colunas para seleção de métricas
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Primeiro, seleciona o grupo
            group1 = st.selectbox(
                "Grupo da Variável 1",
                list(metric_groups.keys()),
                key="trend_group1"
            )
            
            # Depois, seleciona a métrica dentro do grupo
            metric1 = st.selectbox(
                "Variável 1",
                [m['label'] for m in metric_groups[group1]],
                key="trend_metric1"
            )
            
            # Encontra o objeto de métrica correspondente
            selected_metric1 = next(
                (m for m in metric_groups[group1] if m['label'] == metric1),
                None
            )
        
        with col2:
            # Opção para não selecionar uma segunda métrica
            include_metric2 = st.checkbox("Incluir segunda variável", value=True)
            
            if include_metric2:
                # Seleciona o grupo
                group2 = st.selectbox(
                    "Grupo da Variável 2",
                    list(metric_groups.keys()),
                    key="trend_group2"
                )
                
                # Seleciona a métrica
                metric2 = st.selectbox(
                    "Variável 2",
                    [m['label'] for m in metric_groups[group2]],
                    key="trend_metric2"
                )
                
                # Encontra o objeto de métrica
                selected_metric2 = next(
                    (m for m in metric_groups[group2] if m['label'] == metric2),
                    None
                )
            else:
                selected_metric2 = None
        
        with col3:
            # Opção para não selecionar uma terceira métrica
            include_metric3 = st.checkbox("Incluir terceira variável", value=False)
            
            if include_metric3:
                # Seleciona o grupo
                group3 = st.selectbox(
                    "Grupo da Variável 3",
                    list(metric_groups.keys()),
                    key="trend_group3"
                )
                
                # Seleciona a métrica
                metric3 = st.selectbox(
                    "Variável 3",
                    [m['label'] for m in metric_groups[group3]],
                    key="trend_metric3"
                )
                
                # Encontra o objeto de métrica
                selected_metric3 = next(
                    (m for m in metric_groups[group3] if m['label'] == metric3),
                    None
                )
            else:
                selected_metric3 = None
        
        # Cria lista de métricas selecionadas
        selected_metrics = [selected_metric1]
        if selected_metric2:
            selected_metrics.append(selected_metric2)
        if selected_metric3:
            selected_metrics.append(selected_metric3)
        
        # Cria o gráfico
        trend_fig = create_custom_trend_chart(df, selected_metrics)
        
        if trend_fig:
            st.plotly_chart(trend_fig, use_container_width=True)
            
            # Adiciona descrições das faixas para métricas específicas
            for metric in selected_metrics:
                if metric['value'] in ['score', 'readiness_tsb', 'tsb', 'ctl', 'monotony']:
                    st.markdown(f"**Faixas de referência para {metric['label']}:**")
                    
                    if metric['value'] == 'score' or metric['value'] == 'readiness_tsb':
                        st.markdown("""
                        - 0-20: Muito Baixo - Recuperação severamente comprometida
                        - 21-40: Baixo - Recuperação insuficiente
                        - 41-60: Moderado - Recuperação parcial
                        - 61-80: Bom - Boa recuperação
                        - 81-100: Excelente - Recuperação completa
                        """)
                    elif metric['value'] == 'tsb':
                        st.markdown("""
                        - < -30: Sobrecarga Severa - Alto risco de overtraining
                        - -30 a -15: Sobrecarga - Fadiga significativa
                        - -15 a -5: Fadiga - Alguma fadiga acumulada
                        - -5 a +5: Equilíbrio - Boa relação carga/recuperação
                        - +5 a +15: Recuperado - Pronto para treinos intensos
                        - +15 a +30: Muito Recuperado - Completamente recuperado
                        - > +30: Destreinamento - Perda de adaptações
                        """)
                    elif metric['value'] == 'ctl':
                        st.markdown("""
                        - 0-30: Muito Baixa - Carga insuficiente para adaptações
                        - 31-60: Baixa - Carga mínima para manutenção
                        - 61-90: Moderada - Carga adequada para desenvolvimento
                        - 91-120: Alta - Carga elevada, bom condicionamento
                        - > 120: Muito Alta - Carga muito elevada, atleta bem treinado
                        """)
                    elif metric['value'] == 'monotony':
                        st.markdown("""
                        - 0-1.0: Baixa - Boa variabilidade na carga
                        - 1.01-1.5: Moderada - Variabilidade adequada
                        - 1.51-2.0: Elevada - Variabilidade reduzida
                        - > 2.0: Muito Elevada - Variabilidade muito baixa, risco de overtraining
                        """)
        else:
            st.warning("Não há dados suficientes para criar o gráfico de tendências.")
    
    # Aba de Correlações
    with chart_tabs[1]:
        st.subheader("Gráfico de Correlação")
        st.write("Selecione duas variáveis para analisar sua correlação.")
        
        # Cria colunas para seleção de métricas
        col1, col2 = st.columns(2)
        
        with col1:
            # Seleciona o grupo para o eixo X
            group_x = st.selectbox(
                "Grupo da Variável X",
                list(metric_groups.keys()),
                key="corr_group_x"
            )
            
            # Seleciona a métrica para o eixo X
            metric_x = st.selectbox(
                "Variável X",
                [m['label'] for m in metric_groups[group_x]],
                key="corr_metric_x"
            )
            
            # Encontra o objeto de métrica
            selected_metric_x = next(
                (m for m in metric_groups[group_x] if m['label'] == metric_x),
                None
            )
        
        with col2:
            # Seleciona o grupo para o eixo Y
            group_y = st.selectbox(
                "Grupo da Variável Y",
                list(metric_groups.keys()),
                key="corr_group_y"
            )
            
            # Seleciona a métrica para o eixo Y
            metric_y = st.selectbox(
                "Variável Y",
                [m['label'] for m in metric_groups[group_y]],
                key="corr_metric_y"
            )
            
            # Encontra o objeto de métrica
            selected_metric_y = next(
                (m for m in metric_groups[group_y] if m['label'] == metric_y),
                None
            )
        
        # Cria o gráfico
        scatter_fig = create_custom_scatter_plot(df, selected_metric_x, selected_metric_y)
        
        if scatter_fig:
            st.plotly_chart(scatter_fig, use_container_width=True)
            
            # Adiciona interpretação da correlação
            correlation = df[[selected_metric_x['value'], selected_metric_y['value']]].corr().iloc[0, 1]
            
            st.subheader("Interpretação da Correlação")
            
            if abs(correlation) < 0.3:
                st.info(f"Correlação fraca (r = {correlation:.2f}): Há pouca ou nenhuma relação linear entre {selected_metric_x['label']} e {selected_metric_y['label']}.")
            elif abs(correlation) < 0.7:
                st.info(f"Correlação moderada (r = {correlation:.2f}): Existe alguma relação linear entre {selected_metric_x['label']} e {selected_metric_y['label']}.")
            else:
                st.info(f"Correlação forte (r = {correlation:.2f}): Existe uma forte relação linear entre {selected_metric_x['label']} e {selected_metric_y['label']}.")
            
            if correlation > 0:
                st.write(f"A correlação é positiva, o que significa que quando {selected_metric_x['label']} aumenta, {selected_metric_y['label']} tende a aumentar também.")
            else:
                st.write(f"A correlação é negativa, o que significa que quando {selected_metric_x['label']} aumenta, {selected_metric_y['label']} tende a diminuir.")
        else:
            st.warning("Não há dados suficientes para criar o gráfico de correlação.")
    
    # Aba de Matriz de Correlação
    with chart_tabs[2]:
        st.subheader("Matriz de Correlação")
        st.write("Selecione as variáveis para incluir na matriz de correlação.")
        
        # Cria colunas para seleção de grupos
        cols = st.columns(len(metric_groups))
        
        # Para cada grupo, cria uma caixa de seleção múltipla
        selected_metrics_by_group = {}
        
        for i, (group, metrics) in enumerate(metric_groups.items()):
            with cols[i]:
                selected_metrics_by_group[group] = st.multiselect(
                    f"Variáveis de {group}",
                    [m['label'] for m in metrics],
                    default=[m['label'] for m in metrics[:2]],  # Seleciona as primeiras 2 por padrão
                    key=f"matrix_{group}"
                )
        
        # Combina todas as métricas selecionadas
        all_selected_metrics = []
        
        for group, selected_labels in selected_metrics_by_group.items():
            for label in selected_labels:
                metric = next((m for m in metric_groups[group] if m['label'] == label), None)
                if metric:
                    all_selected_metrics.append(metric)
        
        # Cria a matriz de correlação
        if all_selected_metrics:
            matrix_fig = create_correlation_matrix(df, all_selected_metrics)
            
            if matrix_fig:
                st.plotly_chart(matrix_fig, use_container_width=True)
                
                st.subheader("Interpretação das Correlações")
                st.write("""
                - Correlação próxima de 1: Forte correlação positiva
                - Correlação próxima de -1: Forte correlação negativa
                - Correlação próxima de 0: Pouca ou nenhuma correlação
                
                Cores mais intensas indicam correlações mais fortes (azul para negativas, vermelho para positivas).
                """)
            else:
                st.warning("Não há dados suficientes para criar a matriz de correlação.")
        else:
            st.warning("Selecione pelo menos uma variável para criar a matriz de correlação.")

# Função para exibir métricas avançadas de carga
def show_advanced_metrics():
    """Exibe métricas avançadas de carga de treino."""
    create_section_header(
        "Métricas Avançadas de Carga", 
        "Visualize métricas avançadas de carga de treino e prontidão.",
        "📉"
    )
    
    # Obtém os dados de treino (últimos 90 dias)
    training_data = get_training_data(st.session_state.user_id, 90)
    
    if not training_data or len(training_data) < 7:
        info_card(
            "Dados insuficientes",
            "São necessárias pelo menos 7 sessões de treino para calcular métricas avançadas. Continue registrando seus treinos regularmente.",
            "ℹ️"
        )
        return
    
    # Converte para DataFrame
    df = pd.DataFrame(training_data)
    
    # Garante que a data está no formato correto
    df['date'] = pd.to_datetime(df['date'])
    
    # Calcula TSS para cada sessão
    df['tss'] = df.apply(
        lambda row: calculate_tss_from_rpe(row['duration'], row['rpe']),
        axis=1
    )
    
    # Calcula métricas avançadas
    ctl = calculate_ctl(training_data)
    atl = calculate_atl(training_data)
    tsb = calculate_tsb(ctl, atl)
    monotony = calculate_monotony(training_data)
    strain = calculate_strain(training_data)
    readiness_tsb = calculate_readiness_from_tsb(tsb)
    
    # Obtém descrições e zonas
    ctl_info = get_ctl_description(ctl)
    tsb_info = get_tsb_description(tsb)
    monotony_info = get_monotony_description(monotony)
    strain_info = get_strain_description(strain)
    readiness_info = get_readiness_score_description(readiness_tsb)
    
    # Exibe as métricas em cards
    st.subheader("Métricas Atuais")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Card para CTL
        st.markdown(f"""
        <style>
        .metric-card {{
            background-color: white;
            border-radius: 10px;
            padding: 15px;
            margin-bottom: 15px;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        }}
        .metric-title {{
            color: #424242;
            font-size: 16px;
            font-weight: 500;
            margin-bottom: 5px;
        }}
        .metric-value {{
            color: {ctl_info['color']};
            font-size: 28px;
            font-weight: 700;
            margin-bottom: 5px;
        }}
        .metric-zone {{
            color: {ctl_info['color']};
            font-size: 16px;
            font-weight: 500;
            margin-bottom: 10px;
        }}
        .metric-description {{
            color: #616161;
            font-size: 14px;
            margin-bottom: 10px;
        }}
        .metric-recommendation {{
            color: #424242;
            font-size: 14px;
            font-style: italic;
        }}
        </style>
        
        <div class="metric-card">
            <div class="metric-title">CTL (Carga Crônica)</div>
            <div class="metric-value">{ctl:.1f}</div>
            <div class="metric-zone">{ctl_info['zone']}</div>
            <div class="metric-description">{ctl_info['description']}</div>
            <div class="metric-recommendation">{ctl_info['recommendation']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Card para ATL
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">ATL (Carga Aguda)</div>
            <div class="metric-value">{atl:.1f}</div>
            <div class="metric-description">Média ponderada da carga dos últimos 7 dias</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Card para TSB
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">TSB (Balanço de Estresse)</div>
            <div class="metric-value">{tsb:.1f}</div>
            <div class="metric-zone">{tsb_info['zone']}</div>
            <div class="metric-description">{tsb_info['description']}</div>
            <div class="metric-recommendation">{tsb_info['recommendation']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Card para Prontidão baseada em TSB
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Prontidão (baseada em TSB)</div>
            <div class="metric-value">{readiness_tsb}</div>
            <div class="metric-zone">{readiness_info['status']}</div>
            <div class="metric-description">{readiness_info['description']}</div>
            <div class="metric-recommendation">{readiness_info['recommendation']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Card para Monotonia
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Monotonia</div>
            <div class="metric-value">{monotony:.2f}</div>
            <div class="metric-zone">{monotony_info['zone']}</div>
            <div class="metric-description">{monotony_info['description']}</div>
            <div class="metric-recommendation">{monotony_info['recommendation']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Card para Strain
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Strain</div>
            <div class="metric-value">{strain:.0f}</div>
            <div class="metric-zone">{strain_info['zone']}</div>
            <div class="metric-description">{strain_info['description']}</div>
            <div class="metric-recommendation">{strain_info['recommendation']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Explicações das métricas
    with st.expander("O que significam essas métricas?"):
        st.markdown("""
        ### CTL (Chronic Training Load)
        Representa a carga de treino crônica, calculada como uma média ponderada exponencial dos últimos 42 dias. É um indicador do seu condicionamento físico geral.
        
        ### ATL (Acute Training Load)
        Representa a carga de treino aguda, calculada como uma média ponderada exponencial dos últimos 7 dias. É um indicador da fadiga recente.
        
        ### TSB (Training Stress Balance)
        Também conhecido como "Form", é calculado como CTL - ATL. Valores positivos indicam boa recuperação, enquanto valores negativos indicam fadiga acumulada.
        
        ### Monotonia
        Mede a variabilidade da carga de treino. Valores altos indicam pouca variação entre dias de treino, o que pode aumentar o risco de overtraining.
        
        ### Strain
        Mede o estresse geral do treino, calculado como carga semanal × monotonia. Valores altos indicam alto estresse e risco de overtraining.
        
        ### Prontidão (baseada em TSB)
        Score de prontidão (0-100) calculado a partir do TSB, fornecendo uma estimativa da sua prontidão para treinar com base no balanço entre carga crônica e aguda.
        """)

# Função principal
def main():
    """Função principal que controla o fluxo da página."""
    # Adiciona o logo na barra lateral
    logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "images", "logo_sintonia.png")
    if os.path.exists(logo_path):
        logo = Image.open(logo_path)
        st.sidebar.image(logo, width=200)
    
    # Cria as abas
    tabs = create_tabs(["Gráficos Personalizáveis", "Métricas Avançadas"])
    
    # Aba de Gráficos Personalizáveis
    with tabs[0]:
        show_custom_charts()
    
    # Aba de Métricas Avançadas
    with tabs[1]:
        show_advanced_metrics()

# Executa a função principal
if __name__ == "__main__":
    main()
