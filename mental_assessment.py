
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import supabase

def init_connection():
    """Inicializa a conexão com o Supabase."""
    client = supabase.create_client(
        st.secrets["supabase_url"],
        st.secrets["supabase_key"]
    )
    return client

def get_user_id():
    """Obtém o ID do usuário logado."""
    if 'user_id' in st.session_state:
        return st.session_state.user_id
    return None

def mental_assessment_module():
    """Módulo principal de avaliação mental."""
    st.header("Avaliação Mental")

    tabs = st.tabs(["Avaliação de Prontidão", "Análise Pós-Treino", "Histórico"])

    with tabs[0]:
        readiness_assessment()

    with tabs[1]:
        post_training_analysis()

    with tabs[2]:
        history_view()

def readiness_assessment():
    """Interface para avaliação de prontidão."""
    st.subheader("Avaliação de Prontidão")

    with st.form("readiness_form"):
        col1, col2 = st.columns(2)

        with col1:
            date = st.date_input("Data", datetime.now())
            sleep_quality = st.slider("Qualidade do Sono (1-10)", 1, 10, 5)
            sleep_duration = st.number_input("Duração do Sono (horas)", 0.0, 12.0, 7.0, 0.5)

        with col2:
            psr = st.slider("Percepção de Status de Recuperação (1-10)", 1, 10, 5)
            waking_sensation = st.slider("Sensação ao Acordar (1-10)", 1, 10, 5)
            stress_level = st.slider("Nível de Estresse (1-10, 10=baixo)", 1, 10, 5)

        submit = st.form_submit_button("Salvar Avaliação")

        if submit:
            user_id = get_user_id()
            if not user_id:
                st.error("Usuário não logado.")
                return

            # Calcular índice de prontidão
            readiness_index = calculate_readiness_index(
                sleep_quality, sleep_duration, psr, waking_sensation, stress_level
            )

            # Salvar no banco de dados
            supabase_client = init_connection()

            try:
                data = {
                    "user_id": user_id,
                    "date": date.isoformat(),
                    "sleep_quality": sleep_quality,
                    "sleep_duration": sleep_duration,
                    "psr": psr,
                    "waking_sensation": waking_sensation,
                    "stress_level": stress_level,
                    "readiness_index": readiness_index
                }

                response = supabase_client.table("readiness_assessments").insert(data).execute()

                if hasattr(response, 'error') and response.error:
                    st.error(f"Erro ao salvar: {response.error.message}")
                else:
                    st.success("Avaliação salva com sucesso!")
                    display_readiness_result(readiness_index)
            except Exception as e:
                st.error(f"Erro ao salvar: {str(e)}")

def calculate_readiness_index(sleep_quality, sleep_duration, psr, waking_sensation, stress_level):
    """Calcula o índice de prontidão com base nos parâmetros fornecidos."""
    # Pesos para cada componente
    weights = {
        "sleep_quality": 0.25,
        "sleep_duration": 0.15,
        "psr": 0.30,
        "waking_sensation": 0.20,
        "stress_level": 0.10
    }

    # Normalizar duração do sono (considerando 8h como ideal)
    normalized_sleep = min(sleep_duration / 8.0, 1.0) * 10

    # Calcular índice ponderado
    readiness_index = (
        weights["sleep_quality"] * sleep_quality +
        weights["sleep_duration"] * normalized_sleep +
        weights["psr"] * psr +
        weights["waking_sensation"] * waking_sensation +
        weights["stress_level"] * stress_level
    )

    return round(readiness_index, 1)

def display_readiness_result(readiness_index):
    """Exibe o resultado da avaliação de prontidão."""
    st.subheader("Resultado da Avaliação")

    # Criar gráfico de gauge
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=readiness_index,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Índice de Prontidão"},
        gauge={
            'axis': {'range': [0, 10]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 4], 'color': "red"},
                {'range': [4, 7], 'color': "yellow"},
                {'range': [7, 10], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "black", 'width': 4},
                'thickness': 0.75,
                'value': readiness_index
            }
        }
    ))

    st.plotly_chart(fig, use_container_width=True)

    # Interpretação
    st.subheader("Interpretação")
    if readiness_index < 4:
        st.warning("Baixa prontidão (< 4): Considere um treino leve ou recuperativo, ou até mesmo descanso.")
    elif readiness_index < 7:
        st.info("Prontidão moderada (4-7): Treino de intensidade moderada recomendado.")
    else:
        st.success("Alta prontidão (> 7): Você está bem recuperado e pronto para um treino de alta intensidade.")

def post_training_analysis():
    """Interface para análise pós-treino."""
    st.subheader("Análise Pós-Treino")

    with st.form("post_training_form"):
        col1, col2 = st.columns(2)

        with col1:
            date = st.date_input("Data do Treino", datetime.now())
            training_type = st.selectbox(
                "Tipo de Treino",
                ["Corrida", "Ciclismo", "Natação", "Musculação", "Funcional", "Outro"]
            )
            pse = st.slider("Percepção Subjetiva de Esforço (1-10)", 1, 10, 5)

        with col2:
            duration = st.number_input("Duração (minutos)", 5, 300, 60, 5)
            notes = st.text_area("Observações", height=100)

        submit = st.form_submit_button("Salvar Análise")

        if submit:
            user_id = get_user_id()
            if not user_id:
                st.error("Usuário não logado.")
                return

            # Calcular TRIMP
            trimp = calculate_trimp(pse, duration)

            # Salvar no banco de dados
            supabase_client = init_connection()

            try:
                data = {
                    "user_id": user_id,
                    "date": date.isoformat(),
                    "training_type": training_type,
                    "pse": pse,
                    "duration": duration,
                    "trimp": trimp,
                    "notes": notes
                }

                response = supabase_client.table("training_sessions").insert(data).execute()

                if hasattr(response, 'error') and response.error:
                    st.error(f"Erro ao salvar: {response.error.message}")
                else:
                    st.success("Análise salva com sucesso!")

                    # Buscar avaliação de prontidão do mesmo dia
                    readiness = get_readiness_for_date(user_id, date)

                    display_training_analysis(trimp, pse, duration, readiness)
            except Exception as e:
                st.error(f"Erro ao salvar: {str(e)}")

def calculate_trimp(pse, duration):
    """Calcula o TRIMP (Training Impulse) com base na PSE e duração."""
    # Fórmula simplificada: TRIMP = PSE * Duração (em minutos)
    return round(pse * duration / 10, 1)

def get_readiness_for_date(user_id, date):
    """Obtém a avaliação de prontidão para uma data específica."""
    supabase_client = init_connection()

    try:
        response = supabase_client.table("readiness_assessments")             .select("*")             .eq("user_id", user_id)             .eq("date", date.isoformat())             .execute()

        if hasattr(response, 'data') and response.data:
            return response.data[0]
    except Exception as e:
        st.error(f"Erro ao buscar avaliação de prontidão: {str(e)}")

    return None

def display_training_analysis(trimp, pse, duration, readiness=None):
    """Exibe a análise do treino."""
    st.subheader("Análise do Treino")

    col1, col2 = st.columns(2)

    with col1:
        # Gráfico de TRIMP
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=trimp,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "TRIMP (Carga de Treino)"},
            gauge={
                'axis': {'range': [0, 200]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgreen"},
                    {'range': [50, 100], 'color': "yellow"},
                    {'range': [100, 150], 'color': "orange"},
                    {'range': [150, 200], 'color': "red"}
                ],
                'threshold': {
                    'line': {'color': "black", 'width': 4},
                    'thickness': 0.75,
                    'value': trimp
                }
            }
        ))

        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Interpretação do TRIMP
        st.subheader("Interpretação da Carga")
        if trimp < 50:
            st.info("Carga baixa (< 50): Treino leve ou recuperativo.")
        elif trimp < 100:
            st.success("Carga moderada (50-100): Treino de intensidade moderada.")
        elif trimp < 150:
            st.warning("Carga alta (100-150): Treino intenso, monitore a recuperação.")
        else:
            st.error("Carga muito alta (> 150): Treino extremamente intenso, priorize a recuperação.")

    # Se tiver dados de prontidão, mostrar relação
    if readiness:
        st.subheader("Relação Prontidão vs. Carga")

        readiness_index = readiness["readiness_index"]

        # Criar dataframe para o gráfico
        df = pd.DataFrame({
            'Métrica': ['Índice de Prontidão', 'TRIMP Normalizado'],
            'Valor': [readiness_index, min(trimp/20, 10)]  # Normalizar TRIMP para escala de 0-10
        })

        fig = px.bar(df, x='Métrica', y='Valor', color='Métrica',
                    color_discrete_map={'Índice de Prontidão': 'blue', 'TRIMP Normalizado': 'orange'},
                    range_y=[0, 10])

        st.plotly_chart(fig, use_container_width=True)

        # Análise da relação
        ratio = readiness_index / (trimp/20)

        st.subheader("Análise da Relação")
        if ratio < 0.8:
            st.warning("A carga de treino foi significativamente maior que sua prontidão. Isso pode levar a recuperação inadequada e maior risco de overtraining.")
        elif ratio > 1.2:
            st.info("Sua prontidão era maior que a carga de treino aplicada. Você poderia ter realizado um treino mais intenso.")
        else:
            st.success("Boa correspondência entre prontidão e carga de treino. Equilíbrio adequado.")

def history_view():
    """Visualização do histórico de avaliações e treinos."""
    st.subheader("Histórico")

    user_id = get_user_id()
    if not user_id:
        st.error("Usuário não logado.")
        return

    # Período de análise
    period = st.selectbox(
        "Período de Análise",
        ["Última Semana", "Últimos 14 dias", "Último Mês", "Últimos 3 Meses"]
    )

    # Determinar data inicial com base no período
    end_date = datetime.now().date()
    if period == "Última Semana":
        start_date = end_date - timedelta(days=7)
    elif period == "Últimos 14 dias":
        start_date = end_date - timedelta(days=14)
    elif period == "Último Mês":
        start_date = end_date - timedelta(days=30)
    else:  # Últimos 3 Meses
        start_date = end_date - timedelta(days=90)

    # Buscar dados
    readiness_data = get_readiness_history(user_id, start_date, end_date)
    training_data = get_training_history(user_id, start_date, end_date)

    if not readiness_data and not training_data:
        st.info("Nenhum dado encontrado para o período selecionado.")
        return

    # Exibir gráficos
    if readiness_data:
        display_readiness_history(readiness_data)

    if training_data:
        display_training_history(training_data)

    if readiness_data and training_data:
        display_combined_analysis(readiness_data, training_data)

def get_readiness_history(user_id, start_date, end_date):
    """Obtém o histórico de avaliações de prontidão."""
    supabase_client = init_connection()

    try:
        response = supabase_client.table("readiness_assessments")             .select("*")             .eq("user_id", user_id)             .gte("date", start_date.isoformat())             .lte("date", end_date.isoformat())             .order("date")             .execute()

        if hasattr(response, 'data') and response.data:
            return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Erro ao buscar histórico de prontidão: {str(e)}")

    return None

def get_training_history(user_id, start_date, end_date):
    """Obtém o histórico de sessões de treino."""
    supabase_client = init_connection()

    try:
        response = supabase_client.table("training_sessions")             .select("*")             .eq("user_id", user_id)             .gte("date", start_date.isoformat())             .lte("date", end_date.isoformat())             .order("date")             .execute()

        if hasattr(response, 'data') and response.data:
            return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Erro ao buscar histórico de treinos: {str(e)}")

    return None

def display_readiness_history(df):
    """Exibe o histórico de avaliações de prontidão."""
    st.subheader("Histórico de Prontidão")

    # Converter coluna de data para datetime
    df['date'] = pd.to_datetime(df['date'])

    # Gráfico de linha para índice de prontidão
    fig = px.line(df, x='date', y='readiness_index', 
                 title='Índice de Prontidão ao Longo do Tempo',
                 labels={'date': 'Data', 'readiness_index': 'Índice de Prontidão'})

    fig.update_layout(yaxis_range=[0, 10])
    st.plotly_chart(fig, use_container_width=True)

    # Gráfico de componentes
    components_df = df[['date', 'sleep_quality', 'sleep_duration', 'psr', 'waking_sensation', 'stress_level']]
    components_df['sleep_duration'] = components_df['sleep_duration'] / 1.2  # Normalizar para escala de 0-10

    # Melt para formato longo
    components_long = pd.melt(
        components_df, 
        id_vars=['date'], 
        value_vars=['sleep_quality', 'sleep_duration', 'psr', 'waking_sensation', 'stress_level'],
        var_name='Componente', 
        value_name='Valor'
    )

    # Renomear componentes para exibição
    component_names = {
        'sleep_quality': 'Qualidade do Sono',
        'sleep_duration': 'Duração do Sono',
        'psr': 'PSR',
        'waking_sensation': 'Sensação ao Acordar',
        'stress_level': 'Nível de Estresse'
    }

    components_long['Componente'] = components_long['Componente'].map(component_names)

    fig = px.line(components_long, x='date', y='Valor', color='Componente',
                 title='Componentes de Prontidão ao Longo do Tempo',
                 labels={'date': 'Data', 'Valor': 'Valor (0-10)'})

    fig.update_layout(yaxis_range=[0, 10])
    st.plotly_chart(fig, use_container_width=True)

def display_training_history(df):
    """Exibe o histórico de sessões de treino."""
    st.subheader("Histórico de Treinos")

    # Converter coluna de data para datetime
    df['date'] = pd.to_datetime(df['date'])

    # Gráfico de barras para TRIMP
    fig = px.bar(df, x='date', y='trimp', color='training_type',
                title='Carga de Treino (TRIMP) ao Longo do Tempo',
                labels={'date': 'Data', 'trimp': 'TRIMP', 'training_type': 'Tipo de Treino'})

    st.plotly_chart(fig, use_container_width=True)

    # Gráfico de linha para PSE
    fig = px.line(df, x='date', y='pse',
                 title='Percepção Subjetiva de Esforço ao Longo do Tempo',
                 labels={'date': 'Data', 'pse': 'PSE (1-10)'})

    fig.update_layout(yaxis_range=[0, 10])
    st.plotly_chart(fig, use_container_width=True)

    # Carga acumulada por semana
    df['week'] = df['date'].dt.isocalendar().week
    df['year'] = df['date'].dt.isocalendar().year

    weekly_load = df.groupby(['year', 'week'])['trimp'].sum().reset_index()
    weekly_load['week_label'] = weekly_load['year'].astype(str) + '-W' + weekly_load['week'].astype(str)

    fig = px.bar(weekly_load, x='week_label', y='trimp',
                title='Carga Semanal Acumulada',
                labels={'week_label': 'Semana', 'trimp': 'TRIMP Total'})

    st.plotly_chart(fig, use_container_width=True)

def display_combined_analysis(readiness_df, training_df):
    """Exibe análise combinada de prontidão e treino."""
    st.subheader("Análise Combinada")

    # Converter colunas de data para datetime
    readiness_df['date'] = pd.to_datetime(readiness_df['date'])
    training_df['date'] = pd.to_datetime(training_df['date'])

    # Mesclar dataframes pela data
    combined_df = pd.merge(
        readiness_df[['date', 'readiness_index']],
        training_df[['date', 'trimp']],
        on='date',
        how='inner'
    )

    if combined_df.empty:
        st.info("Não há dados suficientes para análise combinada (dias com avaliação de prontidão e treino).")
        return

    # Normalizar TRIMP para escala de 0-10 para comparação
    combined_df['trimp_normalized'] = combined_df['trimp'] / 20
    combined_df['trimp_normalized'] = combined_df['trimp_normalized'].clip(upper=10)

    # Calcular diferença
    combined_df['difference'] = combined_df['readiness_index'] - combined_df['trimp_normalized']

    # Gráfico de barras duplas
    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=combined_df['date'],
        y=combined_df['readiness_index'],
        name='Índice de Prontidão',
        marker_color='blue'
    ))

    fig.add_trace(go.Bar(
        x=combined_df['date'],
        y=combined_df['trimp_normalized'],
        name='TRIMP Normalizado',
        marker_color='orange'
    ))

    fig.update_layout(
        title='Comparação: Prontidão vs. Carga de Treino',
        xaxis_title='Data',
        yaxis_title='Valor (0-10)',
        barmode='group',
        yaxis_range=[0, 10]
    )

    st.plotly_chart(fig, use_container_width=True)

    # Gráfico de diferença
    fig = px.bar(
        combined_df, 
        x='date', 
        y='difference',
        title='Diferença: Prontidão - Carga Normalizada',
        labels={'date': 'Data', 'difference': 'Diferença'},
        color='difference',
        color_continuous_scale=['red', 'yellow', 'green'],
        range_color=[-5, 5]
    )

    fig.add_hline(y=0, line_dash="dash", line_color="gray")

    st.plotly_chart(fig, use_container_width=True)

    # Análise de correlação
    correlation = combined_df['readiness_index'].corr(combined_df['trimp_normalized'])

    st.subheader("Correlação")
    st.write(f"Correlação entre Prontidão e Carga de Treino: {correlation:.2f}")

    if correlation > 0.7:
        st.success("Forte correlação positiva: Você tende a treinar mais intensamente quando está bem recuperado.")
    elif correlation > 0.3:
        st.info("Correlação positiva moderada: Há alguma relação entre sua prontidão e intensidade de treino.")
    elif correlation > -0.3:
        st.warning("Correlação fraca: Não há um padrão claro entre sua prontidão e intensidade de treino.")
    else:
        st.error("Correlação negativa: Você tende a treinar mais intensamente quando está menos recuperado, o que pode aumentar o risco de overtraining.")
