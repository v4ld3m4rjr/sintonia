"""
Módulo de Prontidão 2 para o Sistema de Monitoramento do Atleta
--------------------------------------------------------------
Este módulo permite ao atleta visualizar e analisar sua prontidão baseada em CTL/ATL.
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
from utils.database import get_training_data
from utils.helpers import format_date, get_date_range, get_date_labels
from utils.training_load import (
    calculate_tss_from_rpe, calculate_ctl, calculate_atl, calculate_tsb,
    calculate_monotony, calculate_strain, calculate_readiness_from_tsb,
    get_training_load_zone, get_tsb_zone, calculate_volume_reduction
)
from utils.scale_descriptions import (
    get_scale_description, get_readiness_score_description, get_tsb_description,
    get_ctl_description, get_monotony_description, get_strain_description,
    get_volume_reduction_description
)

# Importa os componentes reutilizáveis
from components.cards import metric_card, recommendation_card, info_card
from components.charts import create_trend_chart, create_bar_chart, create_pie_chart
from components.navigation import create_sidebar, create_tabs, create_breadcrumbs, create_section_header

# Configuração da página
st.set_page_config(
    page_title="Prontidão 2 - Sistema de Monitoramento do Atleta",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Verifica autenticação
if not check_authentication():
    st.switch_page("app.py")

# Cria a barra lateral
create_sidebar()

# Título da página
st.title("🔄 Prontidão 2 (CTL/ATL)")
create_breadcrumbs(["Dashboard", "Prontidão 2"])

# Função para preparar os dados para análise
def prepare_data(days=90):
    """
    Prepara os dados de treino para análise de prontidão baseada em CTL/ATL.
    
    Args:
        days (int): Número de dias para buscar dados
    
    Returns:
        DataFrame: DataFrame com dados processados
    """
    # Obtém os dados de treino
    training_data = get_training_data(st.session_state.user_id, days)
    
    if not training_data:
        return None
    
    # Converte para DataFrame
    df = pd.DataFrame(training_data)
    
    # Garante que a data está no formato correto
    df['date'] = pd.to_datetime(df['date'])
    df['date_only'] = df['date'].dt.date
    
    # Calcula TSS para cada sessão
    df['tss'] = df.apply(
        lambda row: calculate_tss_from_rpe(row['duration'], row['rpe']),
        axis=1
    )
    
    # Agrega por dia
    df_daily = df.groupby('date_only').agg({
        'tss': 'sum',
        'trimp': 'sum',
        'duration': 'sum',
        'rpe': 'mean'
    }).reset_index()
    
    # Cria um DataFrame com todas as datas no período
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days-1)
    date_range = [start_date + timedelta(days=i) for i in range(days)]
    df_dates = pd.DataFrame({'date_only': date_range})
    
    # Mescla com os dados diários
    df_all = df_dates.merge(df_daily, on='date_only', how='left')
    
    # Preenche valores ausentes com 0
    df_all = df_all.fillna(0)
    
    # Calcula CTL, ATL e TSB para cada dia
    df_all['ctl'] = df_all['tss'].ewm(span=42, adjust=False).mean()
    df_all['atl'] = df_all['tss'].ewm(span=7, adjust=False).mean()
    df_all['tsb'] = df_all['ctl'] - df_all['atl']
    
    # Calcula monotonia e strain para janelas móveis de 7 dias
    monotony_values = []
    strain_values = []
    
    for i in range(len(df_all)):
        if i < 6:  # Primeiros 6 dias não têm dados suficientes
            monotony_values.append(np.nan)
            strain_values.append(np.nan)
        else:
            # Pega os últimos 7 dias
            window = df_all.iloc[i-6:i+1]
            
            # Calcula monotonia
            mean_load = window['tss'].mean()
            std_load = window['tss'].std()
            monotony = mean_load / std_load if std_load > 0 else 0
            monotony_values.append(monotony)
            
            # Calcula strain
            weekly_load = window['tss'].sum()
            strain = weekly_load * monotony
            strain_values.append(strain)
    
    df_all['monotony'] = monotony_values
    df_all['strain'] = strain_values
    
    # Calcula prontidão baseada em TSB
    df_all['readiness_tsb'] = df_all['tsb'].apply(
        lambda x: calculate_readiness_from_tsb(x)
    )
    
    # Calcula recomendação de volume
    df_all['volume_reduction'] = df_all['readiness_tsb'].apply(
        lambda x: calculate_volume_reduction(x)['reduction_pct']
    )
    
    # Formata as datas para exibição
    df_all['date_formatted'] = df_all['date_only'].apply(lambda x: x.strftime('%d/%m'))
    
    return df_all

# Função para exibir o status atual de prontidão
def show_current_readiness():
    """Exibe o status atual de prontidão baseada em CTL/ATL."""
    create_section_header(
        "Status Atual", 
        "Sua prontidão atual baseada no balanço entre carga crônica e aguda.",
        "📊"
    )
    
    # Obtém os dados
    df = prepare_data(90)
    
    if df is None or df.empty:
        info_card(
            "Sem dados",
            "Não há dados de treino suficientes para calcular a prontidão baseada em CTL/ATL. Registre suas sessões de treino regularmente.",
            "ℹ️"
        )
        return
    
    # Obtém os valores mais recentes
    latest = df.iloc[-1]
    ctl = latest['ctl']
    atl = latest['atl']
    tsb = latest['tsb']
    readiness = latest['readiness_tsb']
    monotony = latest['monotony']
    strain = latest['strain']
    
    # Obtém descrições e zonas
    ctl_info = get_ctl_description(ctl)
    tsb_info = get_tsb_description(tsb)
    readiness_info = get_readiness_score_description(readiness)
    monotony_info = get_monotony_description(monotony)
    strain_info = get_strain_description(strain)
    
    # Calcula recomendação de volume
    volume_reduction = calculate_volume_reduction(readiness)
    volume_info = get_volume_reduction_description(volume_reduction['reduction_pct'])
    
    # Exibe o score de prontidão em destaque
    st.markdown(f"""
    <style>
    .readiness-container {{
        background-color: {readiness_info['color']};
        border-radius: 10px;
        padding: 20px;
        text-align: center;
        margin-bottom: 20px;
    }}
    .readiness-score {{
        color: white;
        font-size: 72px;
        font-weight: 700;
        margin: 0;
        line-height: 1;
    }}
    .readiness-label {{
        color: white;
        font-size: 24px;
        font-weight: 500;
        margin: 0;
        opacity: 0.9;
    }}
    .readiness-description {{
        color: white;
        font-size: 18px;
        margin-top: 10px;
        opacity: 0.9;
    }}
    </style>
    
    <div class="readiness-container">
        <p class="readiness-score">{readiness}</p>
        <p class="readiness-label">Prontidão (baseada em CTL/ATL)</p>
        <p class="readiness-description">{readiness_info['description']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Exibe recomendação de volume
    st.markdown(f"""
    <style>
    .volume-container {{
        background-color: white;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }}
    .volume-title {{
        color: #424242;
        font-size: 18px;
        font-weight: 500;
        margin-bottom: 10px;
    }}
    .volume-bar-container {{
        background-color: #F5F5F5;
        border-radius: 5px;
        height: 25px;
        margin: 10px 0 15px 0;
        overflow: hidden;
    }}
    .volume-bar {{
        background-color: {volume_info['color']};
        height: 100%;
        width: {100 - volume_reduction['reduction_pct']}%;
        display: flex;
        align-items: center;
        justify-content: center;
        color: {'#000' if volume_reduction['reduction_pct'] < 50 else '#FFF'};
        font-weight: bold;
        font-size: 14px;
    }}
    .volume-description {{
        color: #616161;
        font-size: 16px;
        margin-bottom: 10px;
    }}
    .volume-recommendation {{
        color: #424242;
        font-size: 14px;
        font-style: italic;
    }}
    </style>
    
    <div class="volume-container">
        <div class="volume-title">Recomendação de Volume de Treino</div>
        <div class="volume-description">{volume_info['description']}</div>
        <div class="volume-bar-container">
            <div class="volume-bar">{100 - volume_reduction['reduction_pct']}% do volume normal</div>
        </div>
        <div class="volume-recommendation">{volume_info['recommendation']}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Exibe as métricas em cards
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
        </style>
        
        <div class="metric-card">
            <div class="metric-title">CTL (Carga Crônica)</div>
            <div class="metric-value">{ctl:.1f}</div>
            <div class="metric-zone">{ctl_info['zone']}</div>
            <div class="metric-description">{ctl_info['description']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Card para ATL
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">ATL (Carga Aguda)</div>
            <div class="metric-value">{atl:.1f}</div>
            <div class="metric-description">Média ponderada da carga dos últimos 7 dias</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        # Card para TSB
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">TSB (Balanço de Estresse)</div>
            <div class="metric-value">{tsb:.1f}</div>
            <div class="metric-zone">{tsb_info['zone']}</div>
            <div class="metric-description">{tsb_info['description']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Exibe métricas adicionais
    col1, col2 = st.columns(2)
    
    with col1:
        # Card para Monotonia
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Monotonia</div>
            <div class="metric-value">{monotony:.2f}</div>
            <div class="metric-zone">{monotony_info['zone']}</div>
            <div class="metric-description">{monotony_info['description']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Card para Strain
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Strain</div>
            <div class="metric-value">{strain:.0f}</div>
            <div class="metric-zone">{strain_info['zone']}</div>
            <div class="metric-description">{strain_info['description']}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Explicações das métricas
    with st.expander("O que significam essas métricas?"):
        st.markdown("""
        ### Prontidão baseada em CTL/ATL
        Este score (0-100) é calculado a partir do TSB (Training Stress Balance), que representa o balanço entre sua carga de treino crônica (CTL) e aguda (ATL). Um score alto indica boa recuperação e prontidão para treinar, enquanto um score baixo indica fadiga acumulada.
        
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
        
        ### Recomendação de Volume
        Baseada no score de prontidão, indica quanto do volume normal de treino você deve realizar hoje. Por exemplo, uma recomendação de 70% significa que você deve reduzir o volume em 30%.
        """)

# Função para exibir o histórico de prontidão
def show_readiness_history():
    """Exibe o histórico de prontidão baseada em CTL/ATL."""
    create_section_header(
        "Histórico de Prontidão", 
        "Acompanhe a evolução da sua prontidão baseada em CTL/ATL ao longo do tempo.",
        "📈"
    )
    
    # Opções de período
    period_options = {
        "15 dias": 15,
        "30 dias": 30,
        "60 dias": 60,
        "90 dias": 90
    }
    
    selected_period = st.selectbox("Selecione o período", list(period_options.keys()))
    days = period_options[selected_period]
    
    # Obtém os dados
    df = prepare_data(days)
    
    if df is None or df.empty:
        info_card(
            "Sem dados",
            "Não há dados de treino suficientes para exibir o histórico de prontidão baseada em CTL/ATL.",
            "ℹ️"
        )
        return
    
    # Cria o gráfico de prontidão
    st.subheader("Evolução da Prontidão")
    
    # Cria um gráfico com eixos y secundários
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Adiciona a linha de prontidão
    fig.add_trace(
        go.Scatter(
            x=df['date_formatted'],
            y=df['readiness_tsb'],
            name="Prontidão",
            line=dict(color="#4CAF50", width=3),
            mode="lines+markers"
        ),
        secondary_y=False
    )
    
    # Adiciona a linha de TSB
    fig.add_trace(
        go.Scatter(
            x=df['date_formatted'],
            y=df['tsb'],
            name="TSB",
            line=dict(color="#2196F3", width=3),
            mode="lines+markers"
        ),
        secondary_y=True
    )
    
    # Adiciona faixas de referência para prontidão
    fig.add_shape(
        type="rect",
        x0=df['date_formatted'].iloc[0],
        x1=df['date_formatted'].iloc[-1],
        y0=0,
        y1=20,
        fillcolor="rgba(244, 67, 54, 0.2)",  # Vermelho
        line=dict(width=0),
        layer="below",
        secondary_y=False
    )
    fig.add_shape(
        type="rect",
        x0=df['date_formatted'].iloc[0],
        x1=df['date_formatted'].iloc[-1],
        y0=20,
        y1=40,
        fillcolor="rgba(255, 152, 0, 0.2)",  # Laranja
        line=dict(width=0),
        layer="below",
        secondary_y=False
    )
    fig.add_shape(
        type="rect",
        x0=df['date_formatted'].iloc[0],
        x1=df['date_formatted'].iloc[-1],
        y0=40,
        y1=60,
        fillcolor="rgba(255, 193, 7, 0.2)",  # Amarelo
        line=dict(width=0),
        layer="below",
        secondary_y=False
    )
    fig.add_shape(
        type="rect",
        x0=df['date_formatted'].iloc[0],
        x1=df['date_formatted'].iloc[-1],
        y0=60,
        y1=80,
        fillcolor="rgba(139, 195, 74, 0.2)",  # Verde claro
        line=dict(width=0),
        layer="below",
        secondary_y=False
    )
    fig.add_shape(
        type="rect",
        x0=df['date_formatted'].iloc[0],
        x1=df['date_formatted'].iloc[-1],
        y0=80,
        y1=100,
        fillcolor="rgba(76, 175, 80, 0.2)",  # Verde
        line=dict(width=0),
        layer="below",
        secondary_y=False
    )
    
    # Adiciona faixas de referência para TSB
    fig.add_shape(
        type="rect",
        x0=df['date_formatted'].iloc[0],
        x1=df['date_formatted'].iloc[-1],
        y0=-100,
        y1=-30,
        fillcolor="rgba(183, 28, 28, 0.2)",  # Vermelho escuro
        line=dict(width=0),
        layer="below",
        secondary_y=True
    )
    fig.add_shape(
        type="rect",
        x0=df['date_formatted'].iloc[0],
        x1=df['date_formatted'].iloc[-1],
        y0=-30,
        y1=-15,
        fillcolor="rgba(244, 67, 54, 0.2)",  # Vermelho
        line=dict(width=0),
        layer="below",
        secondary_y=True
    )
    fig.add_shape(
        type="rect",
        x0=df['date_formatted'].iloc[0],
        x1=df['date_formatted'].iloc[-1],
        y0=-15,
        y1=-5,
        fillcolor="rgba(255, 152, 0, 0.2)",  # Laranja
        line=dict(width=0),
        layer="below",
        secondary_y=True
    )
    fig.add_shape(
        type="rect",
        x0=df['date_formatted'].iloc[0],
        x1=df['date_formatted'].iloc[-1],
        y0=-5,
        y1=5,
        fillcolor="rgba(76, 175, 80, 0.2)",  # Verde
        line=dict(width=0),
        layer="below",
        secondary_y=True
    )
    fig.add_shape(
        type="rect",
        x0=df['date_formatted'].iloc[0],
        x1=df['date_formatted'].iloc[-1],
        y0=5,
        y1=15,
        fillcolor="rgba(139, 195, 74, 0.2)",  # Verde claro
        line=dict(width=0),
        layer="below",
        secondary_y=True
    )
    fig.add_shape(
        type="rect",
        x0=df['date_formatted'].iloc[0],
        x1=df['date_formatted'].iloc[-1],
        y0=15,
        y1=30,
        fillcolor="rgba(255, 193, 7, 0.2)",  # Amarelo
        line=dict(width=0),
        layer="below",
        secondary_y=True
    )
    fig.add_shape(
        type="rect",
        x0=df['date_formatted'].iloc[0],
        x1=df['date_formatted'].iloc[-1],
        y0=30,
        y1=100,
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
    fig.update_yaxes(title_text="Prontidão (0-100)", secondary_y=False)
    fig.update_yaxes(title_text="TSB", secondary_y=True)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Cria o gráfico de CTL e ATL
    st.subheader("Evolução de CTL e ATL")
    
    fig = go.Figure()
    
    # Adiciona a linha de CTL
    fig.add_trace(
        go.Scatter(
            x=df['date_formatted'],
            y=df['ctl'],
            name="CTL",
            line=dict(color="#4CAF50", width=3),
            mode="lines+markers"
        )
    )
    
    # Adiciona a linha de ATL
    fig.add_trace(
        go.Scatter(
            x=df['date_formatted'],
            y=df['atl'],
            name="ATL",
            line=dict(color="#F44336", width=3),
            mode="lines+markers"
        )
    )
    
    # Adiciona faixas de referência para CTL (para atleta intermediário)
    fig.add_shape(
        type="rect",
        x0=df['date_formatted'].iloc[0],
        x1=df['date_formatted'].iloc[-1],
        y0=0,
        y1=30,
        fillcolor="rgba(244, 67, 54, 0.2)",  # Vermelho
        line=dict(width=0),
        layer="below"
    )
    fig.add_shape(
        type="rect",
        x0=df['date_formatted'].iloc[0],
        x1=df['date_formatted'].iloc[-1],
        y0=30,
        y1=60,
        fillcolor="rgba(255, 152, 0, 0.2)",  # Laranja
        line=dict(width=0),
        layer="below"
    )
    fig.add_shape(
        type="rect",
        x0=df['date_formatted'].iloc[0],
        x1=df['date_formatted'].iloc[-1],
        y0=60,
        y1=90,
        fillcolor="rgba(76, 175, 80, 0.2)",  # Verde
        line=dict(width=0),
        layer="below"
    )
    fig.add_shape(
        type="rect",
        x0=df['date_formatted'].iloc[0],
        x1=df['date_formatted'].iloc[-1],
        y0=90,
        y1=120,
        fillcolor="rgba(255, 152, 0, 0.2)",  # Laranja
        line=dict(width=0),
        layer="below"
    )
    fig.add_shape(
        type="rect",
        x0=df['date_formatted'].iloc[0],
        x1=df['date_formatted'].iloc[-1],
        y0=120,
        y1=200,
        fillcolor="rgba(244, 67, 54, 0.2)",  # Vermelho
        line=dict(width=0),
        layer="below"
    )
    
    # Atualiza layout
    fig.update_layout(
        title="",
        xaxis_title="Data",
        yaxis_title="Carga",
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
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Cria o gráfico de recomendação de volume
    st.subheader("Recomendação de Volume")
    
    fig = go.Figure()
    
    # Adiciona a linha de redução de volume
    fig.add_trace(
        go.Scatter(
            x=df['date_formatted'],
            y=100 - df['volume_reduction'],
            name="Volume Recomendado (%)",
            line=dict(color="#2196F3", width=3),
            mode="lines+markers",
            fill='tozeroy'
        )
    )
    
    # Atualiza layout
    fig.update_layout(
        title="",
        xaxis_title="Data",
        yaxis_title="Volume Recomendado (%)",
        yaxis=dict(range=[0, 100]),
        margin=dict(l=20, r=20, t=30, b=20),
        height=400,
        hovermode="x unified"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Estatísticas do período
    st.subheader("Estatísticas do Período")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        metric_card(
            title="Prontidão Média",
            value=f"{df['readiness_tsb'].mean():.1f}",
            description=f"Máx: {df['readiness_tsb'].max():.0f}, Mín: {df['readiness_tsb'].min():.0f}"
        )
    
    with col2:
        metric_card(
            title="TSB Médio",
            value=f"{df['tsb'].mean():.1f}",
            description=f"Máx: {df['tsb'].max():.1f}, Mín: {df['tsb'].min():.1f}"
        )
    
    with col3:
        metric_card(
            title="Volume Recomendado Médio",
            value=f"{(100 - df['volume_reduction'].mean()):.1f}%",
            description=f"Máx: {(100 - df['volume_reduction'].min()):.0f}%, Mín: {(100 - df['volume_reduction'].max()):.0f}%"
        )

# Função para exibir comparação entre métodos de prontidão
def show_readiness_comparison():
    """Exibe comparação entre os dois métodos de cálculo de prontidão."""
    create_section_header(
        "Comparação de Métodos", 
        "Compare os dois métodos de cálculo de prontidão: questionário e CTL/ATL.",
        "🔍"
    )
    
    # Obtém os dados de treino
    df_training = prepare_data(30)
    
    if df_training is None or df_training.empty:
        info_card(
            "Sem dados de treino",
            "Não há dados de treino suficientes para comparar os métodos de prontidão.",
            "ℹ️"
        )
        return
    
    # Obtém os dados de prontidão do questionário
    from utils.database import get_readiness_data
    readiness_data = get_readiness_data(st.session_state.user_id, 30)
    
    if not readiness_data:
        info_card(
            "Sem dados de questionário",
            "Não há dados de questionário de prontidão para comparar com o método CTL/ATL.",
            "ℹ️"
        )
        return
    
    # Converte para DataFrame
    df_readiness = pd.DataFrame(readiness_data)
    
    # Garante que a data está no formato correto
    df_readiness['date'] = pd.to_datetime(df_readiness['date'])
    df_readiness['date_only'] = df_readiness['date'].dt.date
    
    # Formata as datas para exibição
    df_readiness['date_formatted'] = df_readiness['date_only'].apply(lambda x: x.strftime('%d/%m'))
    
    # Mescla os DataFrames
    df_combined = df_training[['date_only', 'date_formatted', 'readiness_tsb']].merge(
        df_readiness[['date_only', 'score']],
        on='date_only',
        how='inner'
    )
    
    if df_combined.empty:
        info_card(
            "Sem dados correspondentes",
            "Não há datas correspondentes entre os dados de treino e questionário para comparar.",
            "ℹ️"
        )
        return
    
    # Renomeia as colunas
    df_combined = df_combined.rename(columns={
        'readiness_tsb': 'Prontidão (CTL/ATL)',
        'score': 'Prontidão (Questionário)'
    })
    
    # Cria o gráfico de comparação
    st.subheader("Comparação dos Scores de Prontidão")
    
    fig = go.Figure()
    
    # Adiciona a linha de prontidão CTL/ATL
    fig.add_trace(
        go.Scatter(
            x=df_combined['date_formatted'],
            y=df_combined['Prontidão (CTL/ATL)'],
            name="Prontidão (CTL/ATL)",
            line=dict(color="#4CAF50", width=3),
            mode="lines+markers"
        )
    )
    
    # Adiciona a linha de prontidão do questionário
    fig.add_trace(
        go.Scatter(
            x=df_combined['date_formatted'],
            y=df_combined['Prontidão (Questionário)'],
            name="Prontidão (Questionário)",
            line=dict(color="#2196F3", width=3),
            mode="lines+markers"
        )
    )
    
    # Atualiza layout
    fig.update_layout(
        title="",
        xaxis_title="Data",
        yaxis_title="Score de Prontidão (0-100)",
        yaxis=dict(range=[0, 100]),
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
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Calcula correlação entre os métodos
    correlation = df_combined['Prontidão (CTL/ATL)'].corr(df_combined['Prontidão (Questionário)'])
    
    # Cria o gráfico de dispersão
    st.subheader("Correlação entre os Métodos")
    
    fig = px.scatter(
        df_combined,
        x='Prontidão (Questionário)',
        y='Prontidão (CTL/ATL)',
        color='date_formatted',
        color_discrete_sequence=px.colors.sequential.Viridis,
        labels={
            'Prontidão (Questionário)': 'Prontidão (Questionário)',
            'Prontidão (CTL/ATL)': 'Prontidão (CTL/ATL)',
            'date_formatted': 'Data'
        },
        hover_data=['date_formatted']
    )
    
    # Adiciona linha de tendência
    fig.add_traces(
        px.scatter(
            df_combined, 
            x='Prontidão (Questionário)', 
            y='Prontidão (CTL/ATL)', 
            trendline='ols'
        ).data[1]
    )
    
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
        title="",
        xaxis_title="Prontidão (Questionário)",
        yaxis_title="Prontidão (CTL/ATL)",
        margin=dict(l=20, r=20, t=30, b=20),
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Interpretação da correlação
    st.subheader("Interpretação da Correlação")
    
    if abs(correlation) < 0.3:
        st.info(f"Correlação fraca (r = {correlation:.2f}): Há pouca relação entre os dois métodos de cálculo de prontidão.")
    elif abs(correlation) < 0.7:
        st.info(f"Correlação moderada (r = {correlation:.2f}): Existe alguma relação entre os dois métodos de cálculo de prontidão.")
    else:
        st.info(f"Correlação forte (r = {correlation:.2f}): Existe uma forte relação entre os dois métodos de cálculo de prontidão.")
    
    if correlation > 0:
        st.write("A correlação é positiva, o que significa que quando a prontidão calculada por um método aumenta, a prontidão calculada pelo outro método tende a aumentar também.")
    else:
        st.write("A correlação é negativa, o que significa que quando a prontidão calculada por um método aumenta, a prontidão calculada pelo outro método tende a diminuir.")
    
    # Estatísticas comparativas
    st.subheader("Estatísticas Comparativas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        metric_card(
            title="Prontidão Média (CTL/ATL)",
            value=f"{df_combined['Prontidão (CTL/ATL)'].mean():.1f}",
            description=f"Desvio padrão: {df_combined['Prontidão (CTL/ATL)'].std():.1f}"
        )
    
    with col2:
        metric_card(
            title="Prontidão Média (Questionário)",
            value=f"{df_combined['Prontidão (Questionário)'].mean():.1f}",
            description=f"Desvio padrão: {df_combined['Prontidão (Questionário)'].std():.1f}"
        )
    
    # Explicação dos métodos
    with st.expander("Diferenças entre os métodos"):
        st.markdown("""
        ### Método do Questionário
        O método do questionário calcula a prontidão com base nas respostas diárias do atleta sobre qualidade do sono, duração do sono, estresse, dor muscular, energia, motivação, nutrição e hidratação. É um método subjetivo que depende da percepção do atleta.
        
        ### Método CTL/ATL
        O método CTL/ATL calcula a prontidão com base no histórico de treinos do atleta, especificamente no balanço entre a carga de treino crônica (CTL) e a carga de treino aguda (ATL). É um método objetivo que depende apenas dos dados de treino registrados.
        
        ### Quando usar cada método
        - **Método do Questionário**: Ideal para uso diário, especialmente quando não há histórico de treino suficiente ou quando fatores externos (como estresse, sono, nutrição) são importantes.
        - **Método CTL/ATL**: Mais preciso para atletas com histórico de treino consistente, especialmente para avaliar o impacto da carga de treino na recuperação.
        
        Recomendamos usar ambos os métodos em conjunto para uma visão mais completa da sua prontidão para treinar.
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
    tabs = create_tabs(["Status Atual", "Histórico", "Comparação de Métodos"])
    
    # Aba de Status Atual
    with tabs[0]:
        show_current_readiness()
    
    # Aba de Histórico
    with tabs[1]:
        show_readiness_history()
    
    # Aba de Comparação de Métodos
    with tabs[2]:
        show_readiness_comparison()

# Executa a função principal
if __name__ == "__main__":
    main()
