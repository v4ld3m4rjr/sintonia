"""
Módulo de Treino para o Sistema de Monitoramento do Atleta
---------------------------------------------------------
Este módulo permite ao atleta registrar e analisar suas sessões de treino.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
from PIL import Image

# Adiciona os diretórios ao path para importação dos módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importa os módulos de utilidades
from utils.auth import check_authentication
from utils.database import get_training_data, save_training_session, get_readiness_data
from utils.helpers import format_date, get_date_range, get_date_labels, calculate_weekly_trimp

# Importa os componentes reutilizáveis
from components.cards import metric_card, recommendation_card, info_card, goal_progress_card
from components.charts import create_trend_chart, create_bar_chart, create_pie_chart
from components.navigation import create_sidebar, create_tabs, create_breadcrumbs, create_section_header

# Configuração da página
st.set_page_config(
    page_title="Treino - Sistema de Monitoramento do Atleta",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Verifica autenticação
if not check_authentication():
    st.switch_page("app.py")

# Cria a barra lateral
create_sidebar()

# Título da página
st.title("🏋️ Treino")
create_breadcrumbs(["Dashboard", "Treino"])

# Função para obter descrição qualitativa para a escala de Borg adaptada (0-10)
def get_borg_description(value):
    """
    Retorna uma descrição qualitativa para um valor na escala de Borg adaptada (0-10).
    
    Args:
        value: Valor numérico na escala (0-10)
    
    Returns:
        str: Descrição qualitativa
    """
    descriptions = {
        0: "Nenhum esforço - Repouso completo",
        1: "Muito, muito leve - Atividade quase imperceptível",
        2: "Muito leve - Como caminhar lentamente",
        3: "Leve - Atividade confortável, respiração normal",
        4: "Moderado - Começa a sentir algum esforço",
        5: "Um pouco difícil - Respiração mais intensa, ainda confortável",
        6: "Difícil - Respiração mais pesada, conversação ainda possível",
        7: "Muito difícil - Respiração profunda, conversação difícil",
        8: "Muito, muito difícil - Respiração muito pesada, fala limitada",
        9: "Máximo - Quase no limite máximo",
        10: "Extremo máximo - Esforço máximo absoluto"
    }
    
    return descriptions.get(value, "")

# Função para calcular o TRIMP (Training Impulse)
def calculate_trimp(duration, rpe):
    """
    Calcula o TRIMP (Training Impulse) baseado na duração e RPE.
    
    Args:
        duration (float): Duração do treino em minutos
        rpe (int): Percepção de esforço na escala de Borg adaptada (0-10)
    
    Returns:
        float: Valor do TRIMP
    """
    # Fórmula simples: TRIMP = duração (min) × RPE
    return duration * rpe

# Função para recomendar ajuste de volume baseado no score de prontidão
def recommend_volume_adjustment(readiness_score):
    """
    Recomenda ajuste de volume baseado no score de prontidão.
    
    Args:
        readiness_score (int): Score de prontidão (0-100)
    
    Returns:
        dict: Dicionário com percentual de redução e descrição
    """
    # Calcula o percentual de redução (0% para score 100, até 80% para score 0)
    reduction_pct = max(0, int((100 - readiness_score) * 0.8))
    
    # Define a descrição baseada no percentual
    if reduction_pct <= 10:
        description = "Volume normal - Você está em ótima forma para treinar"
    elif reduction_pct <= 30:
        description = "Redução leve - Ajuste o volume para evitar sobrecarga"
    elif reduction_pct <= 50:
        description = "Redução moderada - Diminua o volume e intensidade"
    elif reduction_pct <= 70:
        description = "Redução significativa - Foque em técnica e recuperação"
    else:
        description = "Redução severa - Considere um treino muito leve ou descanso"
    
    return {
        "reduction_pct": reduction_pct,
        "description": description
    }

# Função para exibir o formulário de nova sessão de treino
def show_new_session():
    """Exibe o formulário para registro de nova sessão de treino."""
    create_section_header(
        "Nova Sessão de Treino", 
        "Registre os detalhes da sua sessão de treino para acompanhar sua carga de trabalho.",
        "📝"
    )
    
    # Obtém o último score de prontidão
    readiness_data = get_readiness_data(st.session_state.user_id, 1)
    
    # Se houver dados de prontidão, exibe recomendação de volume
    if readiness_data:
        latest_readiness = readiness_data[0]
        readiness_score = latest_readiness.get('score', 0)
        
        # Obtém recomendação de ajuste de volume
        volume_adjustment = recommend_volume_adjustment(readiness_score)
        
        # Exibe card de recomendação
        st.info(f"**Seu score de prontidão hoje é {readiness_score}/100**")
        
        # Barra de progresso para visualização do ajuste de volume
        remaining_volume = 100 - volume_adjustment["reduction_pct"]
        
        # Estilo CSS para a barra de progresso
        st.markdown(f"""
        <style>
        .volume-container {{
            background-color: #F5F5F5;
            border-radius: 5px;
            height: 20px;
            margin: 10px 0 15px 0;
            overflow: hidden;
        }}
        .volume-bar {{
            background-color: {'#4CAF50' if remaining_volume > 70 else '#FFC107' if remaining_volume > 40 else '#FF9800'};
            height: 100%;
            width: {remaining_volume}%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: {'#000' if remaining_volume > 50 else '#FFF'};
            font-weight: bold;
            font-size: 12px;
        }}
        </style>
        
        <div>
            <p><strong>Recomendação de volume:</strong> {volume_adjustment["description"]}</p>
            <div class="volume-container">
                <div class="volume-bar">{remaining_volume}% do volume normal</div>
            </div>
            <p style="font-size: 14px; color: #757575; font-style: italic;">Reduza o volume do treino em {volume_adjustment["reduction_pct"]}% com base no seu nível de prontidão atual.</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Cria o formulário
    with st.form("training_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            # Data do treino (padrão: hoje)
            training_date = st.date_input(
                "Data do Treino",
                datetime.now().date(),
                max_value=datetime.now().date()
            )
            
            # Tipo de treino
            training_type = st.selectbox(
                "Tipo de Treino",
                [
                    "Resistência", "Força", "Hipertrofia", "Potência", 
                    "Velocidade", "Técnica", "Recuperação", "Competição", "Outro"
                ]
            )
            
            # Duração do treino
            duration = st.number_input(
                "Duração (minutos)",
                min_value=5,
                max_value=300,
                value=60,
                step=5,
                help="Duração total da sessão de treino em minutos"
            )
        
        with col2:
            # Percepção de esforço (RPE) - Escala de Borg adaptada (0-10)
            rpe = st.slider(
                "Percepção de Esforço (RPE)",
                0, 10, 5,
                help="Escala de Borg adaptada (0-10)",
                format="%d"
            )
            st.caption(get_borg_description(rpe))
            
            # Calcula o TRIMP automaticamente
            trimp = calculate_trimp(duration, rpe)
            
            # Exibe o TRIMP calculado
            st.metric(
                "TRIMP (Impulso de Treino)",
                f"{trimp}",
                help="Training Impulse = Duração × RPE"
            )
            
            # Sensação pós-treino
            feeling = st.selectbox(
                "Sensação Pós-Treino",
                [
                    "Excelente", "Muito Boa", "Boa", 
                    "Regular", "Ruim", "Muito Ruim"
                ],
                index=2
            )
        
        # Notas do treino
        notes = st.text_area(
            "Notas do Treino",
            placeholder="Descreva detalhes do treino, exercícios realizados, sensações, etc..."
        )
        
        # Botão de envio
        submit = st.form_submit_button("Registrar Treino", use_container_width=True)
        
        if submit:
            # Coleta os dados do formulário
            training_data = {
                'date': training_date.isoformat(),
                'type': training_type,
                'duration': duration,
                'rpe': rpe,
                'trimp': trimp,
                'feeling': feeling,
                'notes': notes
            }
            
            # Salva no banco de dados
            if save_training_session(st.session_state.user_id, training_data):
                st.success("Sessão de treino registrada com sucesso!")
                
                # Exibe resumo do treino registrado
                st.markdown("### Resumo do Treino Registrado")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    metric_card(
                        title="Tipo de Treino",
                        value=training_type,
                        description=f"Duração: {duration} minutos"
                    )
                
                with col2:
                    metric_card(
                        title="Percepção de Esforço",
                        value=f"{rpe}/10",
                        description=get_borg_description(rpe)
                    )
                
                with col3:
                    metric_card(
                        title="TRIMP",
                        value=str(trimp),
                        description=f"Sensação: {feeling}"
                    )
            else:
                st.error("Erro ao salvar a sessão de treino. Tente novamente.")

# Função para exibir o histórico de treinos
def show_history():
    """Exibe o histórico de sessões de treino com gráficos e análises."""
    create_section_header(
        "Histórico de Treinos", 
        "Acompanhe a evolução da sua carga de treino ao longo do tempo.",
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
    
    # Obtém os dados de treino
    training_data = get_training_data(st.session_state.user_id, days)
    
    if not training_data:
        info_card(
            "Sem dados",
            "Você ainda não possui sessões de treino registradas neste período.",
            "ℹ️"
        )
        return
    
    # Converte para DataFrame para facilitar a manipulação
    df = pd.DataFrame(training_data)
    
    # Formata as datas
    df['date_obj'] = pd.to_datetime(df['date'])
    df['date_formatted'] = df['date_obj'].dt.strftime("%d/%m")
    
    # Ordena por data
    df = df.sort_values('date_obj')
    
    # Gráfico de linha para TRIMP ao longo do tempo
    st.subheader("Evolução do TRIMP")
    
    fig = px.line(
        df, 
        x='date_formatted', 
        y='trimp',
        markers=True,
        line_shape='spline',
        color_discrete_sequence=["#1E88E5"]
    )
    
    fig.update_layout(
        xaxis_title="Data",
        yaxis_title="TRIMP",
        height=400,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Gráfico de barras para distribuição por tipo de treino
    st.subheader("Distribuição por Tipo de Treino")
    
    # Calcula a contagem por tipo de treino
    type_counts = df['type'].value_counts().reset_index()
    type_counts.columns = ['Tipo', 'Contagem']
    
    # Cria o gráfico
    fig = px.bar(
        type_counts,
        x='Tipo',
        y='Contagem',
        color='Contagem',
        color_continuous_scale='Viridis'
    )
    
    fig.update_layout(
        xaxis_title="Tipo de Treino",
        yaxis_title="Número de Sessões",
        height=400,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Gráfico de pizza para distribuição de RPE
    st.subheader("Distribuição de Percepção de Esforço (RPE)")
    
    # Calcula a contagem por RPE
    rpe_counts = df['rpe'].value_counts().reset_index()
    rpe_counts.columns = ['RPE', 'Contagem']
    rpe_counts = rpe_counts.sort_values('RPE')
    
    # Cria o gráfico
    fig = create_pie_chart(
        labels=[f"{rpe} - {get_borg_description(rpe).split(' - ')[0]}" for rpe in rpe_counts['RPE']],
        values=rpe_counts['Contagem'],
        title="Distribuição de RPE"
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Estatísticas do período
    st.subheader("Estatísticas do Período")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        metric_card(
            title="Total de Sessões",
            value=str(len(df)),
            description=f"Em {days} dias"
        )
    
    with col2:
        metric_card(
            title="TRIMP Total",
            value=str(int(df['trimp'].sum())),
            description=f"Média por sessão: {int(df['trimp'].mean())}"
        )
    
    with col3:
        metric_card(
            title="RPE Médio",
            value=f"{df['rpe'].mean():.1f}/10",
            description=f"Duração média: {int(df['duration'].mean())} min"
        )
    
    # Tabela com histórico de treinos
    st.subheader("Registro de Treinos")
    
    # Prepara os dados para a tabela
    table_data = df[['date_formatted', 'type', 'duration', 'rpe', 'trimp', 'feeling']].copy()
    table_data.columns = ['Data', 'Tipo', 'Duração (min)', 'RPE', 'TRIMP', 'Sensação']
    
    # Exibe a tabela
    st.dataframe(
        table_data,
        use_container_width=True,
        hide_index=True
    )

# Função para exibir análises de carga de treino
def show_analysis():
    """Exibe análises avançadas dos dados de treino."""
    create_section_header(
        "Análise de Carga de Treino", 
        "Insights e correlações para entender melhor seus padrões de treino.",
        "🔍"
    )
    
    # Obtém os dados de treino (últimos 90 dias)
    training_data = get_training_data(st.session_state.user_id, 90)
    
    if not training_data or len(training_data) < 7:
        info_card(
            "Dados insuficientes",
            "São necessárias pelo menos 7 sessões de treino para gerar análises. Continue registrando seus treinos regularmente.",
            "ℹ️"
        )
        return
    
    # Converte para DataFrame
    df = pd.DataFrame(training_data)
    df['date_obj'] = pd.to_datetime(df['date'])
    
    # Cria semanas para análise
    df['week_start'] = df['date_obj'].dt.to_period('W').dt.start_time
    df['week_end'] = df['date_obj'].dt.to_period('W').dt.end_time
    df['week_label'] = df['week_start'].dt.strftime('%d/%m') + ' - ' + df['week_end'].dt.strftime('%d/%m')
    
    # Análise de carga semanal
    st.subheader("Carga de Treino Semanal")
    
    # Calcula TRIMP por semana
    weekly_trimp = df.groupby('week_label')['trimp'].sum().reset_index()
    
    # Cria o gráfico
    fig = px.bar(
        weekly_trimp,
        x='week_label',
        y='trimp',
        color='trimp',
        color_continuous_scale='Viridis',
        labels={'trimp': 'TRIMP Total', 'week_label': 'Semana'}
    )
    
    fig.update_layout(
        xaxis_title="Semana",
        yaxis_title="TRIMP Total",
        height=400,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Análise de distribuição de intensidade
    st.subheader("Distribuição de Intensidade")
    
    # Define categorias de intensidade baseadas no RPE
    def categorize_intensity(rpe):
        if rpe <= 3:
            return "Baixa (RPE 0-3)"
        elif rpe <= 6:
            return "Moderada (RPE 4-6)"
        else:
            return "Alta (RPE 7-10)"
    
    df['intensity'] = df['rpe'].apply(categorize_intensity)
    
    # Calcula a distribuição de intensidade
    intensity_dist = df.groupby('intensity')['duration'].sum().reset_index()
    intensity_dist.columns = ['Intensidade', 'Duração Total (min)']
    
    # Ordena as categorias
    intensity_order = ["Baixa (RPE 0-3)", "Moderada (RPE 4-6)", "Alta (RPE 7-10)"]
    intensity_dist['Intensidade'] = pd.Categorical(
        intensity_dist['Intensidade'], 
        categories=intensity_order, 
        ordered=True
    )
    intensity_dist = intensity_dist.sort_values('Intensidade')
    
    # Cria o gráfico
    fig = px.pie(
        intensity_dist,
        values='Duração Total (min)',
        names='Intensidade',
        color='Intensidade',
        color_discrete_map={
            "Baixa (RPE 0-3)": "#4CAF50",
            "Moderada (RPE 4-6)": "#FFC107",
            "Alta (RPE 7-10)": "#F44336"
        }
    )
    
    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Análise de relação entre RPE e sensação pós-treino
    st.subheader("Relação entre RPE e Sensação Pós-Treino")
    
    # Mapeia sensações para valores numéricos
    feeling_map = {
        "Excelente": 5,
        "Muito Boa": 4,
        "Boa": 3,
        "Regular": 2,
        "Ruim": 1,
        "Muito Ruim": 0
    }
    
    df['feeling_value'] = df['feeling'].map(feeling_map)
    
    # Calcula a média de sensação para cada valor de RPE
    rpe_feeling = df.groupby('rpe')['feeling_value'].mean().reset_index()
    
    # Cria o gráfico
    fig = px.scatter(
        rpe_feeling,
        x='rpe',
        y='feeling_value',
        size=[10] * len(rpe_feeling),
        color='feeling_value',
        color_continuous_scale='RdYlGn',
        labels={'rpe': 'RPE', 'feeling_value': 'Sensação Média'}
    )
    
    # Adiciona linha de tendência
    fig.add_traces(
        px.scatter(
            rpe_feeling, x='rpe', y='feeling_value', trendline='ols'
        ).data[1]
    )
    
    fig.update_layout(
        xaxis_title="RPE",
        yaxis_title="Sensação Pós-Treino",
        yaxis=dict(
            tickmode='array',
            tickvals=list(feeling_map.values()),
            ticktext=list(feeling_map.keys())
        ),
        height=400,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Insights automáticos
    st.subheader("Insights Automáticos")
    
    insights = []
    
    # Insight sobre distribuição de intensidade
    intensity_pcts = intensity_dist.set_index('Intensidade')['Duração Total (min)']
    total_duration = intensity_pcts.sum()
    intensity_pcts = (intensity_pcts / total_duration * 100).to_dict()
    
    # Verifica se há desequilíbrio na distribuição de intensidade
    if intensity_pcts.get("Alta (RPE 7-10)", 0) > 40:
        insights.append("Sua distribuição de intensidade mostra um volume elevado de treinos de alta intensidade. Considere aumentar os treinos de baixa intensidade para melhorar a recuperação.")
    elif intensity_pcts.get("Baixa (RPE 0-3)", 0) > 70:
        insights.append("Sua distribuição de intensidade mostra um volume muito elevado de treinos de baixa intensidade. Considere incluir mais treinos de intensidade moderada a alta para estimular adaptações.")
    else:
        insights.append("Sua distribuição de intensidade parece equilibrada, com uma boa mistura de treinos de diferentes intensidades.")
    
    # Insight sobre variação semanal
    if len(weekly_trimp) >= 2:
        weekly_variation = weekly_trimp['trimp'].pct_change().abs().mean() * 100
        if weekly_variation > 30:
            insights.append(f"Sua carga de treino varia significativamente entre as semanas (média de {weekly_variation:.1f}% de variação). Considere uma progressão mais gradual para reduzir o risco de lesões.")
        else:
            insights.append(f"Sua progressão de carga semanal é consistente, com variação média de {weekly_variation:.1f}% entre semanas.")
    
    # Insight sobre relação RPE e sensação
    if len(rpe_feeling) >= 3:
        correlation = df['rpe'].corr(df['feeling_value'])
        if correlation < -0.5:
            insights.append(f"Existe uma forte correlação negativa (r={correlation:.2f}) entre a intensidade do treino (RPE) e sua sensação pós-treino. Treinos mais intensos tendem a resultar em sensações piores.")
        elif correlation > 0.3:
            insights.append(f"Curiosamente, você tende a se sentir melhor após treinos mais intensos (correlação positiva r={correlation:.2f}). Isso pode indicar boa adaptação a cargas elevadas.")
    
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
    tabs = create_tabs(["Nova Sessão", "Histórico", "Análise"])
    
    # Aba de Nova Sessão
    with tabs[0]:
        show_new_session()
    
    # Aba de Histórico
    with tabs[1]:
        show_history()
    
    # Aba de Análise
    with tabs[2]:
        show_analysis()

# Executa a função principal
if __name__ == "__main__":
    main()
