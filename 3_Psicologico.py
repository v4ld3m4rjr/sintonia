"""
Módulo Psicológico para o Sistema de Monitoramento do Atleta
-----------------------------------------------------------
Este módulo permite ao atleta registrar e analisar seu estado psicológico.
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
from utils.database import get_psychological_data, save_psychological_data, get_readiness_data, get_training_data
from utils.helpers import format_date, get_date_range, get_date_labels
from utils.scale_descriptions import get_scale_description

# Importa os componentes reutilizáveis
from components.cards import metric_card, recommendation_card, info_card
from components.charts import create_trend_chart, create_bar_chart, create_radar_chart, create_heatmap
from components.navigation import create_sidebar, create_tabs, create_breadcrumbs, create_section_header

# Configuração da página
st.set_page_config(
    page_title="Psicológico - Sistema de Monitoramento do Atleta",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Verifica autenticação
if not check_authentication():
    st.switch_page("app.py")

# Cria a barra lateral
create_sidebar()

# Título da página
st.title("🧠 Psicológico")
create_breadcrumbs(["Dashboard", "Psicológico"])

# Função para obter descrição qualitativa para a escala DASS (0-3)
def get_dass_description(value, type_dass):
    """
    Retorna uma descrição qualitativa para um valor na escala DASS (0-3).
    
    Args:
        value: Valor numérico na escala (0-3)
        type_dass: Tipo de escala DASS (anxiety, depression, stress)
    
    Returns:
        str: Descrição qualitativa
    """
    descriptions = {
        "anxiety": {
            0: "Nenhum - Ausência de sintomas de ansiedade",
            1: "Leve - Sintomas leves e ocasionais de ansiedade",
            2: "Moderado - Sintomas frequentes que causam algum desconforto",
            3: "Severo - Sintomas intensos e persistentes de ansiedade"
        },
        "depression": {
            0: "Nenhum - Ausência de sintomas de depressão",
            1: "Leve - Humor levemente baixo, recupera-se facilmente",
            2: "Moderado - Humor baixo persistente, afeta algumas atividades",
            3: "Severo - Humor muito baixo, afeta significativamente o dia a dia"
        },
        "stress": {
            0: "Nenhum - Ausência de sintomas de estresse",
            1: "Leve - Tensão ocasional, recupera-se facilmente",
            2: "Moderado - Tensão frequente, dificuldade para relaxar",
            3: "Severo - Tensão constante, irritabilidade, dificuldade para tolerar interrupções"
        }
    }
    
    return descriptions.get(type_dass, {}).get(value, "")

# Função para obter descrição qualitativa para a escala de humor (1-5)
def get_mood_description(value):
    """
    Retorna uma descrição qualitativa para um valor na escala de humor (1-5).
    
    Args:
        value: Valor numérico na escala (1-5)
    
    Returns:
        str: Descrição qualitativa
    """
    descriptions = {
        1: "Muito Negativo - Humor extremamente baixo, sentimentos intensos de tristeza ou irritabilidade",
        2: "Negativo - Humor baixo, predominância de emoções negativas",
        3: "Neutro - Equilíbrio entre emoções positivas e negativas",
        4: "Positivo - Humor bom, predominância de emoções positivas",
        5: "Muito Positivo - Humor excelente, sentimentos intensos de alegria e bem-estar"
    }
    
    return descriptions.get(value, "")

# Função para calcular o score DASS total
def calculate_dass_score(anxiety, depression, stress):
    """
    Calcula o score DASS total (0-100).
    
    Args:
        anxiety (int): Nível de ansiedade (0-3)
        depression (int): Nível de depressão (0-3)
        stress (int): Nível de estresse (0-3)
    
    Returns:
        int: Score DASS total (0-100)
    """
    # Calcula a média dos três componentes (0-3)
    mean_score = (anxiety + depression + stress) / 3
    
    # Converte para escala 0-100 (invertida, pois valores mais baixos são melhores)
    dass_score = 100 - (mean_score * 100 / 3)
    
    # Arredonda para inteiro
    return round(dass_score)

# Função para obter recomendações baseadas no score DASS
def get_dass_recommendations(anxiety, depression, stress):
    """
    Retorna recomendações baseadas nos scores DASS.
    
    Args:
        anxiety (int): Nível de ansiedade (0-3)
        depression (int): Nível de depressão (0-3)
        stress (int): Nível de estresse (0-3)
    
    Returns:
        list: Lista de recomendações
    """
    recommendations = []
    
    # Recomendações para ansiedade
    if anxiety >= 2:
        recommendations.append("Pratique técnicas de respiração profunda e mindfulness para reduzir a ansiedade.")
        recommendations.append("Considere reduzir a intensidade dos treinos em dias de maior ansiedade.")
    
    # Recomendações para depressão
    if depression >= 2:
        recommendations.append("Mantenha-se ativo, mesmo que com treinos mais leves, pois o exercício pode ajudar a melhorar o humor.")
        recommendations.append("Busque atividades sociais e apoio de amigos ou familiares.")
    
    # Recomendações para estresse
    if stress >= 2:
        recommendations.append("Inclua técnicas de relaxamento na sua rotina, como meditação ou yoga.")
        recommendations.append("Garanta tempo adequado para recuperação entre sessões de treino intensas.")
    
    # Recomendações gerais
    if anxiety + depression + stress >= 4:
        recommendations.append("Considere consultar um profissional de saúde mental para orientação especializada.")
    
    # Se todos os scores forem baixos
    if anxiety + depression + stress <= 1:
        recommendations.append("Continue com suas práticas atuais de bem-estar mental, que parecem estar funcionando bem.")
    
    return recommendations

# Função para exibir o formulário de nova avaliação psicológica
def show_new_assessment():
    """Exibe o formulário para registro de nova avaliação psicológica."""
    create_section_header(
        "Nova Avaliação Psicológica", 
        "Registre seu estado psicológico atual para monitorar sua saúde mental.",
        "📝"
    )
    
    # Cria o formulário
    with st.form("psychological_form"):
        st.markdown("### Escala DASS (Depressão, Ansiedade e Estresse)")
        st.markdown("Avalie como você se sentiu nos últimos dias:")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Ansiedade
            anxiety = st.slider(
                "Ansiedade",
                0, 3, 0,
                help="0 = Nenhum, 1 = Leve, 2 = Moderado, 3 = Severo",
                format="%d"
            )
            st.caption(get_dass_description(anxiety, "anxiety"))
            
            # Depressão
            depression = st.slider(
                "Depressão",
                0, 3, 0,
                help="0 = Nenhum, 1 = Leve, 2 = Moderado, 3 = Severo",
                format="%d"
            )
            st.caption(get_dass_description(depression, "depression"))
        
        with col2:
            # Estresse
            stress = st.slider(
                "Estresse",
                0, 3, 0,
                help="0 = Nenhum, 1 = Leve, 2 = Moderado, 3 = Severo",
                format="%d"
            )
            st.caption(get_dass_description(stress, "stress"))
            
            # Humor
            mood = st.slider(
                "Humor Geral",
                1, 5, 3,
                help="1 = Muito Negativo, 3 = Neutro, 5 = Muito Positivo",
                format="%d"
            )
            st.caption(get_mood_description(mood))
        
        # Qualidade do sono (para correlação)
        sleep_quality = st.slider(
            "Qualidade do Sono",
            1, 5, 3,
            help="1 = Muito Ruim, 3 = Regular, 5 = Excelente",
            format="%d"
        )
        st.caption(get_scale_description(sleep_quality, "sleep_quality"))
        
        # Notas adicionais
        notes = st.text_area(
            "Notas Adicionais",
            placeholder="Descreva fatores que podem estar influenciando seu estado psicológico atual..."
        )
        
        # Botão de envio
        submit = st.form_submit_button("Registrar Avaliação", use_container_width=True)
        
        if submit:
            # Calcula o score DASS total
            dass_score = calculate_dass_score(anxiety, depression, stress)
            
            # Coleta os dados do formulário
            psychological_data = {
                'date': datetime.now().isoformat(),
                'dass_anxiety': anxiety,
                'dass_depression': depression,
                'dass_stress': stress,
                'dass_score': dass_score,
                'mood': mood,
                'sleep_quality': sleep_quality,
                'notes': notes
            }
            
            # Salva no banco de dados
            if save_psychological_data(st.session_state.user_id, psychological_data):
                st.success("Avaliação psicológica registrada com sucesso!")
                
                # Exibe resumo da avaliação
                st.markdown("### Resumo da Avaliação")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    # Score DASS
                    if dass_score >= 80:
                        color = "#4CAF50"  # Verde
                        status = "Excelente"
                    elif dass_score >= 60:
                        color = "#8BC34A"  # Verde claro
                        status = "Bom"
                    elif dass_score >= 40:
                        color = "#FFC107"  # Amarelo
                        status = "Moderado"
                    elif dass_score >= 20:
                        color = "#FF9800"  # Laranja
                        status = "Preocupante"
                    else:
                        color = "#F44336"  # Vermelho
                        status = "Crítico"
                    
                    st.markdown(f"""
                    <div style="background-color: {color}; padding: 10px; border-radius: 5px; text-align: center;">
                        <h1 style="color: white; margin: 0;">{dass_score}</h1>
                        <p style="color: white; margin: 0;">Score DASS</p>
                        <p style="color: white; margin: 0; font-weight: bold;">{status}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    # Radar chart dos componentes DASS
                    fig = create_radar_chart(
                        categories=["Ansiedade", "Depressão", "Estresse"],
                        values=[anxiety, depression, stress],
                        max_value=3
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with col3:
                    # Humor e sono
                    metric_card(
                        title="Humor",
                        value=f"{mood}/5",
                        description=get_mood_description(mood)
                    )
                    
                    metric_card(
                        title="Qualidade do Sono",
                        value=f"{sleep_quality}/5",
                        description=get_scale_description(sleep_quality, "sleep_quality")
                    )
                
                # Recomendações
                st.markdown("### Recomendações")
                
                recommendations = get_dass_recommendations(anxiety, depression, stress)
                
                for recommendation in recommendations:
                    recommendation_card(recommendation)
            else:
                st.error("Erro ao salvar a avaliação psicológica. Tente novamente.")

# Função para exibir o histórico de avaliações psicológicas
def show_history():
    """Exibe o histórico de avaliações psicológicas com gráficos e análises."""
    create_section_header(
        "Histórico Psicológico", 
        "Acompanhe a evolução do seu estado psicológico ao longo do tempo.",
        "📈"
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
    
    # Obtém os dados psicológicos
    psychological_data = get_psychological_data(st.session_state.user_id, days)
    
    if not psychological_data:
        info_card(
            "Sem dados",
            "Você ainda não possui avaliações psicológicas registradas neste período.",
            "ℹ️"
        )
        return
    
    # Converte para DataFrame para facilitar a manipulação
    df = pd.DataFrame(psychological_data)
    
    # Formata as datas
    df['date_obj'] = pd.to_datetime(df['date'])
    df['date_formatted'] = df['date_obj'].dt.strftime("%d/%m")
    
    # Ordena por data
    df = df.sort_values('date_obj')
    
    # Gráfico de linha para Score DASS ao longo do tempo
    st.subheader("Evolução do Score DASS")
    
    fig = go.Figure()
    
    # Adiciona a linha de Score DASS
    fig.add_trace(
        go.Scatter(
            x=df['date_formatted'],
            y=df['dass_score'],
            name="Score DASS",
            line=dict(color="#4CAF50", width=3),
            mode="lines+markers"
        )
    )
    
    # Adiciona faixas de referência
    fig.add_shape(
        type="rect",
        x0=df['date_formatted'].iloc[0],
        x1=df['date_formatted'].iloc[-1],
        y0=0,
        y1=20,
        fillcolor="rgba(244, 67, 54, 0.2)",  # Vermelho
        line=dict(width=0),
        layer="below"
    )
    fig.add_shape(
        type="rect",
        x0=df['date_formatted'].iloc[0],
        x1=df['date_formatted'].iloc[-1],
        y0=20,
        y1=40,
        fillcolor="rgba(255, 152, 0, 0.2)",  # Laranja
        line=dict(width=0),
        layer="below"
    )
    fig.add_shape(
        type="rect",
        x0=df['date_formatted'].iloc[0],
        x1=df['date_formatted'].iloc[-1],
        y0=40,
        y1=60,
        fillcolor="rgba(255, 193, 7, 0.2)",  # Amarelo
        line=dict(width=0),
        layer="below"
    )
    fig.add_shape(
        type="rect",
        x0=df['date_formatted'].iloc[0],
        x1=df['date_formatted'].iloc[-1],
        y0=60,
        y1=80,
        fillcolor="rgba(139, 195, 74, 0.2)",  # Verde claro
        line=dict(width=0),
        layer="below"
    )
    fig.add_shape(
        type="rect",
        x0=df['date_formatted'].iloc[0],
        x1=df['date_formatted'].iloc[-1],
        y0=80,
        y1=100,
        fillcolor="rgba(76, 175, 80, 0.2)",  # Verde
        line=dict(width=0),
        layer="below"
    )
    
    # Atualiza layout
    fig.update_layout(
        xaxis_title="Data",
        yaxis_title="Score DASS",
        yaxis=dict(range=[0, 100]),
        height=400,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Gráfico de linha para componentes DASS ao longo do tempo
    st.subheader("Evolução dos Componentes DASS")
    
    fig = go.Figure()
    
    # Adiciona as linhas para cada componente
    fig.add_trace(
        go.Scatter(
            x=df['date_formatted'],
            y=df['dass_anxiety'],
            name="Ansiedade",
            line=dict(color="#F44336", width=3),
            mode="lines+markers"
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['date_formatted'],
            y=df['dass_depression'],
            name="Depressão",
            line=dict(color="#2196F3", width=3),
            mode="lines+markers"
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['date_formatted'],
            y=df['dass_stress'],
            name="Estresse",
            line=dict(color="#FF9800", width=3),
            mode="lines+markers"
        )
    )
    
    # Atualiza layout
    fig.update_layout(
        xaxis_title="Data",
        yaxis_title="Nível (0-3)",
        yaxis=dict(range=[0, 3]),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        height=400,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Gráfico de linha para humor e sono ao longo do tempo
    st.subheader("Evolução do Humor e Sono")
    
    fig = go.Figure()
    
    # Adiciona as linhas para humor e sono
    fig.add_trace(
        go.Scatter(
            x=df['date_formatted'],
            y=df['mood'],
            name="Humor",
            line=dict(color="#9C27B0", width=3),
            mode="lines+markers"
        )
    )
    
    fig.add_trace(
        go.Scatter(
            x=df['date_formatted'],
            y=df['sleep_quality'],
            name="Qualidade do Sono",
            line=dict(color="#00BCD4", width=3),
            mode="lines+markers"
        )
    )
    
    # Atualiza layout
    fig.update_layout(
        xaxis_title="Data",
        yaxis_title="Nível (1-5)",
        yaxis=dict(range=[1, 5]),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        height=400,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Estatísticas do período
    st.subheader("Estatísticas do Período")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        metric_card(
            title="Score DASS Médio",
            value=f"{df['dass_score'].mean():.1f}",
            description=f"Máx: {df['dass_score'].max():.0f}, Mín: {df['dass_score'].min():.0f}"
        )
    
    with col2:
        metric_card(
            title="Humor Médio",
            value=f"{df['mood'].mean():.1f}/5",
            description=f"Máx: {df['mood'].max():.0f}, Mín: {df['mood'].min():.0f}"
        )
    
    with col3:
        metric_card(
            title="Qualidade do Sono Média",
            value=f"{df['sleep_quality'].mean():.1f}/5",
            description=f"Máx: {df['sleep_quality'].max():.0f}, Mín: {df['sleep_quality'].min():.0f}"
        )
    
    # Tabela com histórico de avaliações
    st.subheader("Registro de Avaliações")
    
    # Prepara os dados para a tabela
    table_data = df[['date_formatted', 'dass_score', 'dass_anxiety', 'dass_depression', 'dass_stress', 'mood', 'sleep_quality']].copy()
    table_data.columns = ['Data', 'Score DASS', 'Ansiedade', 'Depressão', 'Estresse', 'Humor', 'Qualidade do Sono']
    
    # Exibe a tabela
    st.dataframe(
        table_data,
        use_container_width=True,
        hide_index=True
    )

# Função para exibir análises avançadas
def show_analysis():
    """Exibe análises avançadas dos dados psicológicos."""
    create_section_header(
        "Análise Avançada", 
        "Insights e correlações para entender melhor seu estado psicológico.",
        "🔍"
    )
    
    # Obtém os dados psicológicos (últimos 90 dias)
    psychological_data = get_psychological_data(st.session_state.user_id, 90)
    
    if not psychological_data or len(psychological_data) < 7:
        info_card(
            "Dados insuficientes",
            "São necessárias pelo menos 7 avaliações psicológicas para gerar análises. Continue registrando suas avaliações regularmente.",
            "ℹ️"
        )
        return
    
    # Converte para DataFrame
    df_psych = pd.DataFrame(psychological_data)
    df_psych['date'] = pd.to_datetime(df_psych['date'])
    df_psych['date_only'] = df_psych['date'].dt.date
    
    # Obtém os dados de prontidão
    readiness_data = get_readiness_data(st.session_state.user_id, 90)
    df_readiness = None
    if readiness_data:
        df_readiness = pd.DataFrame(readiness_data)
        df_readiness['date'] = pd.to_datetime(df_readiness['date'])
        df_readiness['date_only'] = df_readiness['date'].dt.date
    
    # Obtém os dados de treino
    training_data = get_training_data(st.session_state.user_id, 90)
    df_training = None
    if training_data:
        df_training = pd.DataFrame(training_data)
        df_training['date'] = pd.to_datetime(df_training['date'])
        df_training['date_only'] = df_training['date'].dt.date
        
        # Agrega por dia
        df_training = df_training.groupby('date_only').agg({
            'trimp': 'sum',
            'rpe': 'mean',
            'duration': 'sum'
        }).reset_index()
    
    # Análise de correlação entre componentes psicológicos
    st.subheader("Correlação entre Componentes Psicológicos")
    
    # Seleciona as colunas relevantes
    psych_cols = ['dass_anxiety', 'dass_depression', 'dass_stress', 'mood', 'sleep_quality']
    
    # Calcula a matriz de correlação
    corr_matrix = df_psych[psych_cols].corr()
    
    # Mapeia os nomes das colunas
    col_names = {
        'dass_anxiety': 'Ansiedade',
        'dass_depression': 'Depressão',
        'dass_stress': 'Estresse',
        'mood': 'Humor',
        'sleep_quality': 'Qualidade do Sono'
    }
    
    corr_matrix.index = [col_names[col] for col in corr_matrix.index]
    corr_matrix.columns = [col_names[col] for col in corr_matrix.columns]
    
    # Cria o heatmap
    fig = create_heatmap(
        data=corr_matrix,
        x_labels=corr_matrix.columns,
        y_labels=corr_matrix.index,
        colorscale="RdBu_r",
        text_auto=".2f"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Análise de correlação com prontidão e treino
    if df_readiness is not None or df_training is not None:
        st.subheader("Correlação com Prontidão e Treino")
        
        # Mescla os DataFrames
        df_merged = df_psych[['date_only', 'dass_score', 'mood', 'sleep_quality']].copy()
        
        if df_readiness is not None:
            df_merged = df_merged.merge(
                df_readiness[['date_only', 'score']],
                on='date_only',
                how='left'
            )
            df_merged = df_merged.rename(columns={'score': 'readiness_score'})
        
        if df_training is not None:
            df_merged = df_merged.merge(
                df_training[['date_only', 'trimp', 'rpe']],
                on='date_only',
                how='left'
            )
        
        # Remove linhas com valores ausentes
        df_merged = df_merged.dropna()
        
        if not df_merged.empty:
            # Seleciona as colunas para correlação
            corr_cols = ['dass_score', 'mood', 'sleep_quality']
            
            if 'readiness_score' in df_merged.columns:
                corr_cols.append('readiness_score')
            
            if 'trimp' in df_merged.columns:
                corr_cols.append('trimp')
            
            if 'rpe' in df_merged.columns:
                corr_cols.append('rpe')
            
            # Calcula a matriz de correlação
            corr_matrix = df_merged[corr_cols].corr()
            
            # Mapeia os nomes das colunas
            col_names = {
                'dass_score': 'Score DASS',
                'mood': 'Humor',
                'sleep_quality': 'Qualidade do Sono',
                'readiness_score': 'Prontidão',
                'trimp': 'TRIMP',
                'rpe': 'RPE'
            }
            
            corr_matrix.index = [col_names[col] for col in corr_matrix.index]
            corr_matrix.columns = [col_names[col] for col in corr_matrix.columns]
            
            # Cria o heatmap
            fig = create_heatmap(
                data=corr_matrix,
                x_labels=corr_matrix.columns,
                y_labels=corr_matrix.index,
                colorscale="RdBu_r",
                text_auto=".2f"
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Gráficos de dispersão para correlações importantes
            if 'readiness_score' in df_merged.columns:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Correlação entre Score DASS e Prontidão
                    fig = px.scatter(
                        df_merged,
                        x='dass_score',
                        y='readiness_score',
                        trendline='ols',
                        labels={
                            'dass_score': 'Score DASS',
                            'readiness_score': 'Score de Prontidão'
                        },
                        title="Score DASS vs. Prontidão"
                    )
                    
                    # Calcula correlação
                    corr = df_merged['dass_score'].corr(df_merged['readiness_score'])
                    
                    # Adiciona anotação com correlação
                    fig.add_annotation(
                        x=0.95,
                        y=0.05,
                        xref="paper",
                        yref="paper",
                        text=f"r = {corr:.2f}",
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
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Correlação entre Humor e Prontidão
                    fig = px.scatter(
                        df_merged,
                        x='mood',
                        y='readiness_score',
                        trendline='ols',
                        labels={
                            'mood': 'Humor',
                            'readiness_score': 'Score de Prontidão'
                        },
                        title="Humor vs. Prontidão"
                    )
                    
                    # Calcula correlação
                    corr = df_merged['mood'].corr(df_merged['readiness_score'])
                    
                    # Adiciona anotação com correlação
                    fig.add_annotation(
                        x=0.95,
                        y=0.05,
                        xref="paper",
                        yref="paper",
                        text=f"r = {corr:.2f}",
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
                    
                    st.plotly_chart(fig, use_container_width=True)
            
            if 'trimp' in df_merged.columns:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Correlação entre Score DASS e TRIMP
                    fig = px.scatter(
                        df_merged,
                        x='dass_score',
                        y='trimp',
                        trendline='ols',
                        labels={
                            'dass_score': 'Score DASS',
                            'trimp': 'TRIMP'
                        },
                        title="Score DASS vs. TRIMP"
                    )
                    
                    # Calcula correlação
                    corr = df_merged['dass_score'].corr(df_merged['trimp'])
                    
                    # Adiciona anotação com correlação
                    fig.add_annotation(
                        x=0.95,
                        y=0.05,
                        xref="paper",
                        yref="paper",
                        text=f"r = {corr:.2f}",
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
                    
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Correlação entre Humor e TRIMP
                    fig = px.scatter(
                        df_merged,
                        x='mood',
                        y='trimp',
                        trendline='ols',
                        labels={
                            'mood': 'Humor',
                            'trimp': 'TRIMP'
                        },
                        title="Humor vs. TRIMP"
                    )
                    
                    # Calcula correlação
                    corr = df_merged['mood'].corr(df_merged['trimp'])
                    
                    # Adiciona anotação com correlação
                    fig.add_annotation(
                        x=0.95,
                        y=0.05,
                        xref="paper",
                        yref="paper",
                        text=f"r = {corr:.2f}",
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
                    
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Não há dados suficientes para análise de correlação com prontidão e treino.")
    
    # Análise de tendências por dia da semana
    st.subheader("Tendências por Dia da Semana")
    
    # Adiciona dia da semana
    df_psych['weekday'] = df_psych['date'].dt.weekday
    
    # Calcula médias por dia da semana
    weekday_avg = df_psych.groupby('weekday').agg({
        'dass_score': 'mean',
        'mood': 'mean',
        'sleep_quality': 'mean'
    }).reset_index()
    
    # Mapeia os dias da semana
    weekday_names = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
    weekday_avg['weekday_name'] = weekday_avg['weekday'].apply(lambda x: weekday_names[x])
    
    # Ordena por dia da semana
    weekday_avg = weekday_avg.sort_values('weekday')
    
    # Cria o gráfico de barras
    fig = go.Figure()
    
    # Adiciona barras para cada métrica
    fig.add_trace(
        go.Bar(
            x=weekday_avg['weekday_name'],
            y=weekday_avg['dass_score'],
            name="Score DASS",
            marker_color="#4CAF50"
        )
    )
    
    fig.add_trace(
        go.Bar(
            x=weekday_avg['weekday_name'],
            y=weekday_avg['mood'] * 20,  # Escala para comparar com DASS
            name="Humor (x20)",
            marker_color="#9C27B0"
        )
    )
    
    fig.add_trace(
        go.Bar(
            x=weekday_avg['weekday_name'],
            y=weekday_avg['sleep_quality'] * 20,  # Escala para comparar com DASS
            name="Qualidade do Sono (x20)",
            marker_color="#00BCD4"
        )
    )
    
    # Atualiza layout
    fig.update_layout(
        xaxis_title="Dia da Semana",
        yaxis_title="Score",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="center",
            x=0.5
        ),
        height=400,
        margin=dict(l=20, r=20, t=20, b=20),
        barmode='group'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Insights automáticos
    st.subheader("Insights Automáticos")
    
    insights = []
    
    # Insight sobre correlação entre humor e sono
    corr_mood_sleep = df_psych['mood'].corr(df_psych['sleep_quality'])
    if abs(corr_mood_sleep) > 0.5:
        if corr_mood_sleep > 0:
            insights.append(f"Existe uma forte correlação positiva (r={corr_mood_sleep:.2f}) entre seu humor e qualidade do sono. Melhorar seu sono pode ajudar a melhorar seu humor.")
        else:
            insights.append(f"Curiosamente, existe uma forte correlação negativa (r={corr_mood_sleep:.2f}) entre seu humor e qualidade do sono.")
    
    # Insight sobre correlação entre componentes DASS
    corr_anx_dep = df_psych['dass_anxiety'].corr(df_psych['dass_depression'])
    if abs(corr_anx_dep) > 0.5:
        insights.append(f"Existe uma forte correlação (r={corr_anx_dep:.2f}) entre seus níveis de ansiedade e depressão, sugerindo que eles podem estar interligados.")
    
    # Insight sobre dia da semana com melhor/pior humor
    best_mood_day = weekday_avg.loc[weekday_avg['mood'].idxmax()]
    worst_mood_day = weekday_avg.loc[weekday_avg['mood'].idxmin()]
    insights.append(f"Seu humor tende a ser melhor às {best_mood_day['weekday_name']}s e pior às {worst_mood_day['weekday_name']}s.")
    
    # Insight sobre dia da semana com melhor/pior sono
    best_sleep_day = weekday_avg.loc[weekday_avg['sleep_quality'].idxmax()]
    worst_sleep_day = weekday_avg.loc[weekday_avg['sleep_quality'].idxmin()]
    insights.append(f"Sua qualidade de sono tende a ser melhor às {best_sleep_day['weekday_name']}s e pior às {worst_sleep_day['weekday_name']}s.")
    
    # Insight sobre tendência geral
    dass_trend = np.polyfit(range(len(df_psych)), df_psych['dass_score'], 1)[0]
    if abs(dass_trend) > 1:
        if dass_trend > 0:
            insights.append(f"Seu score DASS está melhorando ao longo do tempo (tendência de +{dass_trend:.1f} pontos por avaliação).")
        else:
            insights.append(f"Seu score DASS está piorando ao longo do tempo (tendência de {dass_trend:.1f} pontos por avaliação).")
    
    # Exibe os insights
    for insight in insights:
        info_card("Insight", insight, "💡")

# Função principal
def main():
    """Função principal que controla o fluxo da página."""
    # Adiciona o logo na barra lateral
    logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "images", "logo_sintonia.png")
    if os.path.exists(logo_path):
        logo = Image.open(logo_path)
        st.sidebar.image(logo, width=200)
    
    # Cria as abas
    tabs = create_tabs(["Nova Avaliação", "Histórico", "Análise"])
    
    # Aba de Nova Avaliação
    with tabs[0]:
        show_new_assessment()
    
    # Aba de Histórico
    with tabs[1]:
        show_history()
    
    # Aba de Análise
    with tabs[2]:
        show_analysis()

# Executa a função principal
if __name__ == "__main__":
    main()
