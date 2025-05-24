"""
Módulo de Prontidão para o Sistema de Monitoramento do Atleta
------------------------------------------------------------
Este módulo permite ao atleta registrar e analisar sua prontidão diária.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import sys
import os

# Adiciona os diretórios ao path para importação dos módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importa os módulos de utilidades
from utils.auth import check_authentication
from utils.database import get_readiness_data, save_readiness_assessment
from utils.helpers import format_date, calculate_readiness_score, get_date_range, get_date_labels

# Importa os componentes reutilizáveis
from components.cards import metric_card, recommendation_card, info_card
from components.charts import create_trend_chart, create_radar_chart, create_bar_chart
from components.navigation import create_sidebar, create_tabs, create_breadcrumbs, create_section_header

# Configuração da página
st.set_page_config(
    page_title="Prontidão - Sistema de Monitoramento do Atleta",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Verifica autenticação
if not check_authentication():
    st.switch_page("app.py")

# Cria a barra lateral
create_sidebar()

# Título da página
st.title("🔋 Prontidão")
create_breadcrumbs(["Dashboard", "Prontidão"])

# Função para obter descrição qualitativa para cada valor da escala
def get_scale_description(value, scale_type):
    """
    Retorna uma descrição qualitativa para um valor em uma escala específica.
    
    Args:
        value: Valor numérico na escala
        scale_type: Tipo de escala (sleep_quality, stress_level, etc.)
    
    Returns:
        str: Descrição qualitativa
    """
    descriptions = {
        "sleep_quality": {
            1: "Muito ruim - Sono extremamente fragmentado, insônia severa",
            2: "Ruim - Dificuldade para dormir, despertares frequentes",
            3: "Regular - Sono razoável com alguns despertares",
            4: "Bom - Sono contínuo com poucos despertares",
            5: "Excelente - Sono profundo e reparador"
        },
        "stress_level": {
            1: "Muito estressado - Sensação de sobrecarga, ansiedade intensa",
            2: "Estressado - Tensão constante, dificuldade para relaxar",
            3: "Moderado - Alguma tensão, mas gerenciável",
            4: "Relaxado - Sensação de calma na maior parte do tempo",
            5: "Muito relaxado - Completamente tranquilo e em paz"
        },
        "muscle_soreness": {
            1: "Dor severa - Dor limitante, afeta movimentos básicos",
            2: "Dor moderada - Desconforto constante, afeta alguns movimentos",
            3: "Dor leve - Sensação de desconforto ocasional",
            4: "Mínima dor - Leve sensibilidade em alguns músculos",
            5: "Sem dor - Nenhuma sensação de dor ou desconforto"
        },
        "energy_level": {
            1: "Exausto - Sem energia para atividades básicas",
            2: "Cansado - Energia limitada, necessidade de esforço extra",
            3: "Moderado - Energia suficiente para o dia",
            4: "Energizado - Boa disposição para atividades",
            5: "Muito energizado - Energia abundante, vitalidade máxima"
        },
        "motivation": {
            1: "Desmotivado - Sem vontade de treinar ou se exercitar",
            2: "Pouco motivado - Precisa de esforço para iniciar atividades",
            3: "Motivação moderada - Disposição razoável para treinar",
            4: "Motivado - Boa vontade e entusiasmo para treinar",
            5: "Muito motivado - Extremamente entusiasmado e ansioso para treinar"
        },
        "nutrition_quality": {
            1: "Muito ruim - Alimentação inadequada, processados, fast food",
            2: "Ruim - Poucas refeições balanceadas, excesso de processados",
            3: "Regular - Algumas refeições balanceadas, algumas escolhas ruins",
            4: "Boa - Maioria das refeições balanceadas e nutritivas",
            5: "Excelente - Alimentação ideal, balanceada e nutritiva"
        },
        "hydration": {
            1: "Desidratado - Sede constante, urina escura, boca seca",
            2: "Pouco hidratado - Alguma sede, hidratação insuficiente",
            3: "Moderadamente hidratado - Hidratação razoável",
            4: "Bem hidratado - Boa ingestão de líquidos durante o dia",
            5: "Perfeitamente hidratado - Ingestão ideal de água e líquidos"
        },
        "sleep_duration": {
            # Para duração do sono, usamos faixas
            0: "Crítico - Menos de 4 horas",
            1: "Crítico - Menos de 4 horas",
            2: "Crítico - Menos de 4 horas",
            3: "Crítico - Menos de 4 horas",
            4: "Muito pouco - 4 horas",
            5: "Insuficiente - 5 horas",
            6: "Abaixo do ideal - 6 horas",
            7: "Adequado - 7 horas",
            8: "Ideal - 8 horas",
            9: "Excelente - 9 horas",
            10: "Abundante - 10 horas",
            11: "Abundante - 11 horas",
            12: "Abundante - 12 horas"
        }
    }
    
    # Para valores decimais na duração do sono
    if scale_type == "sleep_duration" and isinstance(value, float):
        # Arredonda para o inteiro mais próximo para buscar a descrição
        return descriptions[scale_type].get(round(value), "")
    
    return descriptions.get(scale_type, {}).get(value, "")

# Função para exibir o formulário de nova avaliação
def show_new_assessment():
    """Exibe o formulário para registro de nova avaliação de prontidão."""
    create_section_header(
        "Nova Avaliação de Prontidão", 
        "Registre como você está se sentindo hoje para calcular seu nível de prontidão para treinar.",
        "📝"
    )
    
    # Cria o formulário
    with st.form("readiness_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            sleep_quality = st.slider(
                "Qualidade do Sono", 
                1, 5, 3, 
                help="1 = Muito ruim, 5 = Excelente",
                format="%d"
            )
            st.caption(get_scale_description(sleep_quality, "sleep_quality"))
            
            sleep_duration = st.number_input(
                "Duração do Sono (horas)", 
                min_value=0.0, max_value=12.0, value=7.0, step=0.5,
                help="Quantidade de horas dormidas"
            )
            st.caption(get_scale_description(round(sleep_duration), "sleep_duration"))
            
            stress_level = st.slider(
                "Nível de Estresse", 
                1, 5, 3, 
                help="1 = Muito estressado, 5 = Muito relaxado",
                format="%d"
            )
            st.caption(get_scale_description(stress_level, "stress_level"))
            
            muscle_soreness = st.slider(
                "Dor Muscular", 
                1, 5, 3, 
                help="1 = Muita dor, 5 = Sem dor",
                format="%d"
            )
            st.caption(get_scale_description(muscle_soreness, "muscle_soreness"))
        
        with col2:
            energy_level = st.slider(
                "Nível de Energia", 
                1, 5, 3, 
                help="1 = Sem energia, 5 = Muito energizado",
                format="%d"
            )
            st.caption(get_scale_description(energy_level, "energy_level"))
            
            motivation = st.slider(
                "Motivação", 
                1, 5, 3, 
                help="1 = Desmotivado, 5 = Muito motivado",
                format="%d"
            )
            st.caption(get_scale_description(motivation, "motivation"))
            
            nutrition_quality = st.slider(
                "Qualidade da Nutrição", 
                1, 5, 3, 
                help="1 = Muito ruim, 5 = Excelente",
                format="%d"
            )
            st.caption(get_scale_description(nutrition_quality, "nutrition_quality"))
            
            hydration = st.slider(
                "Hidratação", 
                1, 5, 3, 
                help="1 = Desidratado, 5 = Bem hidratado",
                format="%d"
            )
            st.caption(get_scale_description(hydration, "hydration"))
        
        notes = st.text_area("Notas Adicionais", 
                           placeholder="Observações sobre como você está se sentindo hoje...")
        
        submit = st.form_submit_button("Calcular Prontidão", use_container_width=True)
        
        if submit:
            # Coleta os dados do formulário
            assessment_data = {
                'date': datetime.now().isoformat(),
                'sleep_quality': sleep_quality,
                'sleep_duration': sleep_duration,
                'stress_level': stress_level,
                'muscle_soreness': muscle_soreness,
                'energy_level': energy_level,
                'motivation': motivation,
                'nutrition_quality': nutrition_quality,
                'hydration': hydration,
                'notes': notes
            }
            
            # Calcula o score de prontidão
            score = calculate_readiness_score(assessment_data)
            assessment_data['score'] = score
            
            # Salva no banco de dados
            if save_readiness_assessment(st.session_state.user_id, assessment_data):
                st.success("Avaliação de prontidão registrada com sucesso!")
                
                # Exibe o resultado
                show_assessment_result(score, assessment_data)
            else:
                st.error("Erro ao salvar a avaliação. Tente novamente.")

# Função para exibir o resultado da avaliação
def show_assessment_result(score, assessment_data):
    """
    Exibe o resultado da avaliação de prontidão com interpretação e recomendações.
    
    Args:
        score (int): Score de prontidão (0-100)
        assessment_data (dict): Dados da avaliação
    """
    st.markdown("---")
    create_section_header("Resultado da Avaliação", "Seu nível de prontidão para hoje", "📊")
    
    # Exibe o score em um card grande
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Determina a cor e mensagem com base no score
        if score >= 80:
            color = "#4CAF50"  # Verde
            status = "Excelente"
            message = "Você está em ótima forma para treinar hoje!"
        elif score >= 60:
            color = "#8BC34A"  # Verde claro
            status = "Bom"
            message = "Você está bem para treinar hoje."
        elif score >= 40:
            color = "#FFC107"  # Amarelo
            status = "Moderado"
            message = "Você pode treinar, mas considere reduzir a intensidade."
        elif score >= 20:
            color = "#FF9800"  # Laranja
            status = "Baixo"
            message = "Considere um treino leve ou recuperação ativa hoje."
        else:
            color = "#F44336"  # Vermelho
            status = "Muito Baixo"
            message = "Recomendamos descanso ou recuperação passiva hoje."
        
        # Estilo CSS para o card de resultado
        st.markdown(f"""
        <style>
        .result-card {{
            background-color: white;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            margin-bottom: 20px;
        }}
        .result-score {{
            font-size: 72px;
            font-weight: 700;
            color: {color};
            margin: 10px 0;
        }}
        .result-status {{
            font-size: 24px;
            font-weight: 600;
            color: {color};
            margin-bottom: 15px;
        }}
        .result-message {{
            font-size: 18px;
            color: #424242;
            margin-bottom: 10px;
        }}
        </style>
        
        <div class="result-card">
            <div class="result-score">{score}</div>
            <div class="result-status">{status}</div>
            <div class="result-message">{message}</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Exibe recomendações baseadas nos componentes mais fracos
    st.subheader("Recomendações")
    
    # Identifica os componentes mais fracos
    components = {
        'sleep_quality': ('Qualidade do Sono', assessment_data['sleep_quality']),
        'sleep_duration': ('Duração do Sono', assessment_data['sleep_duration'] / 2.4),  # Normaliza para escala 1-5
        'stress_level': ('Nível de Estresse', assessment_data['stress_level']),
        'muscle_soreness': ('Dor Muscular', assessment_data['muscle_soreness']),
        'energy_level': ('Nível de Energia', assessment_data['energy_level']),
        'motivation': ('Motivação', assessment_data['motivation']),
        'nutrition_quality': ('Qualidade da Nutrição', assessment_data['nutrition_quality']),
        'hydration': ('Hidratação', assessment_data['hydration'])
    }
    
    # Ordena os componentes por valor (do menor para o maior)
    sorted_components = sorted(components.items(), key=lambda x: x[1][1])
    
    # Gera recomendações para os 3 componentes mais fracos
    recommendations = []
    
    for component, (name, value) in sorted_components[:3]:
        if component == 'sleep_quality' or component == 'sleep_duration':
            recommendations.append(f"Melhore seu sono: tente dormir mais cedo, evite telas antes de dormir e mantenha um ambiente calmo.")
        elif component == 'stress_level':
            recommendations.append(f"Reduza o estresse: pratique técnicas de respiração, meditação ou atividades relaxantes.")
        elif component == 'muscle_soreness':
            recommendations.append(f"Cuide da recuperação muscular: considere massagem, alongamento, banho de contraste ou crioterapia.")
        elif component == 'energy_level':
            recommendations.append(f"Aumente seu nível de energia: verifique sua alimentação, hidratação e considere uma pequena caminhada ao ar livre.")
        elif component == 'motivation':
            recommendations.append(f"Trabalhe sua motivação: defina metas claras, varie seus treinos ou treine com um parceiro.")
        elif component == 'nutrition_quality':
            recommendations.append(f"Melhore sua nutrição: aumente o consumo de alimentos integrais, frutas, vegetais e proteínas magras.")
        elif component == 'hydration':
            recommendations.append(f"Melhore sua hidratação: beba água regularmente ao longo do dia, não apenas durante os treinos.")
    
    # Adiciona recomendação baseada no score geral
    if score < 40:
        recommendations.append(f"Considere um dia de descanso ou recuperação ativa com atividades de baixa intensidade.")
    elif score < 60:
        recommendations.append(f"Reduza a intensidade do treino hoje e foque em técnica ou treino de baixo impacto.")
    
    # Calcula a recomendação de redução de volume com base no score
    volume_reduction = max(0, int((100 - score) * 0.8))  # 0% de redução para score 100, até 80% para score 0
    if volume_reduction > 0:
        recommendations.append(f"Recomendação de volume: reduza o volume do seu treino em aproximadamente {volume_reduction}% hoje.")
    
    # Exibe as recomendações em um card
    recommendation_card("Recomendações Personalizadas", recommendations)

# Função para exibir o histórico de prontidão
def show_history():
    """Exibe o histórico de avaliações de prontidão com gráficos e análises."""
    create_section_header(
        "Histórico de Prontidão", 
        "Acompanhe a evolução do seu nível de prontidão ao longo do tempo.",
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
    
    # Obtém os dados de prontidão
    readiness_data = get_readiness_data(st.session_state.user_id, days)
    
    if not readiness_data:
        info_card(
            "Sem dados",
            "Você ainda não possui avaliações de prontidão registradas neste período.",
            "ℹ️"
        )
        return
    
    # Converte para DataFrame para facilitar a manipulação
    df = pd.DataFrame(readiness_data)
    
    # Formata as datas
    df['date_formatted'] = df['date'].apply(lambda x: format_date(x, "%d/%m"))
    
    # Gráfico de linha para score ao longo do tempo
    st.subheader("Evolução do Score de Prontidão")
    
    fig = px.line(
        df, 
        x='date_formatted', 
        y='score',
        markers=True,
        line_shape='spline',
        color_discrete_sequence=["#1E88E5"]
    )
    
    fig.update_layout(
        xaxis_title="Data",
        yaxis_title="Score de Prontidão",
        yaxis=dict(range=[0, 100]),
        height=400,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Gráfico de barras para componentes médios
    st.subheader("Componentes Médios")
    
    # Calcula médias dos componentes
    component_means = {
        'Qualidade do Sono': df['sleep_quality'].mean(),
        'Duração do Sono': df['sleep_duration'].mean() / 2.4,  # Normaliza para escala 1-5
        'Nível de Estresse': df['stress_level'].mean(),
        'Dor Muscular': df['muscle_soreness'].mean(),
        'Nível de Energia': df['energy_level'].mean(),
        'Motivação': df['motivation'].mean(),
        'Nutrição': df['nutrition_quality'].mean(),
        'Hidratação': df['hydration'].mean()
    }
    
    # Cria o gráfico de barras
    components_fig = create_bar_chart(
        categories=list(component_means.keys()),
        values=list(component_means.values()),
        color='#8BC34A',
        y_title="Média (1-5)"
    )
    
    components_fig.update_layout(height=400)
    st.plotly_chart(components_fig, use_container_width=True)
    
    # Radar chart para última avaliação vs média
    st.subheader("Última Avaliação vs. Média")
    
    # Obtém a última avaliação
    last_assessment = df.iloc[-1]
    
    # Prepara os dados para o radar chart
    categories = [
        'Qualidade do Sono', 'Duração do Sono', 'Nível de Estresse', 
        'Dor Muscular', 'Nível de Energia', 'Motivação', 
        'Nutrição', 'Hidratação'
    ]
    
    last_values = [
        last_assessment['sleep_quality'],
        last_assessment['sleep_duration'] / 2.4,  # Normaliza para escala 1-5
        last_assessment['stress_level'],
        last_assessment['muscle_soreness'],
        last_assessment['energy_level'],
        last_assessment['motivation'],
        last_assessment['nutrition_quality'],
        last_assessment['hydration']
    ]
    
    mean_values = list(component_means.values())
    
    # Cria o radar chart
    radar_fig = create_radar_chart(
        categories=categories,
        values=last_values,
        reference_values=mean_values,
        title="Comparação de Componentes"
    )
    
    st.plotly_chart(radar_fig, use_container_width=True)
    
    # Estatísticas do período
    st.subheader("Estatísticas do Período")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        metric_card(
            title="Score Médio",
            value=f"{df['score'].mean():.1f}",
            description=f"Média de {len(df)} avaliações"
        )
    
    with col2:
        metric_card(
            title="Score Máximo",
            value=f"{df['score'].max()}",
            description=f"Melhor dia: {format_date(df.loc[df['score'].idxmax()]['date'])}"
        )
    
    with col3:
        metric_card(
            title="Score Mínimo",
            value=f"{df['score'].min()}",
            description=f"Pior dia: {format_date(df.loc[df['score'].idxmin()]['date'])}"
        )

# Função para exibir análises de prontidão
def show_analysis():
    """Exibe análises avançadas dos dados de prontidão."""
    create_section_header(
        "Análise de Prontidão", 
        "Insights e correlações para entender melhor seus padrões.",
        "🔍"
    )
    
    # Obtém os dados de prontidão (últimos 90 dias)
    readiness_data = get_readiness_data(st.session_state.user_id, 90)
    
    if not readiness_data or len(readiness_data) < 7:
        info_card(
            "Dados insuficientes",
            "São necessárias pelo menos 7 avaliações para gerar análises. Continue registrando sua prontidão diariamente.",
            "ℹ️"
        )
        return
    
    # Converte para DataFrame
    df = pd.DataFrame(readiness_data)
    
    # Adiciona dia da semana
    df['date_obj'] = pd.to_datetime(df['date'])
    df['weekday'] = df['date_obj'].dt.day_name()
    
    # Ordem dos dias da semana
    weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday_pt = {
        'Monday': 'Segunda',
        'Tuesday': 'Terça',
        'Wednesday': 'Quarta',
        'Thursday': 'Quinta',
        'Friday': 'Sexta',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo'
    }
    
    df['weekday_pt'] = df['weekday'].map(weekday_pt)
    
    # Análise por dia da semana
    st.subheader("Score de Prontidão por Dia da Semana")
    
    # Calcula média por dia da semana
    weekday_avg = df.groupby('weekday')['score'].mean().reindex(weekday_order).reset_index()
    weekday_avg['weekday_pt'] = weekday_avg['weekday'].map(weekday_pt)
    
    # Cria o gráfico
    fig = px.bar(
        weekday_avg,
        x='weekday_pt',
        y='score',
        color='score',
        color_continuous_scale='Viridis',
        labels={'score': 'Score Médio', 'weekday_pt': 'Dia da Semana'}
    )
    
    fig.update_layout(
        yaxis=dict(range=[0, 100]),
        height=400,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Identifica os melhores e piores dias
    best_day = weekday_avg.loc[weekday_avg['score'].idxmax()]
    worst_day = weekday_avg.loc[weekday_avg['score'].idxmin()]
    
    col1, col2 = st.columns(2)
    
    with col1:
        metric_card(
            title="Melhor Dia da Semana",
            value=best_day['weekday_pt'],
            description=f"Score médio: {best_day['score']:.1f}"
        )
    
    with col2:
        metric_card(
            title="Pior Dia da Semana",
            value=worst_day['weekday_pt'],
            description=f"Score médio: {worst_day['score']:.1f}"
        )
    
    # Correlações entre variáveis
    st.subheader("Correlações entre Componentes")
    
    # Seleciona apenas as colunas numéricas relevantes
    numeric_cols = [
        'sleep_quality', 'sleep_duration', 'stress_level', 'muscle_soreness',
        'energy_level', 'motivation', 'nutrition_quality', 'hydration', 'score'
    ]
    
    # Calcula a matriz de correlação
    corr_matrix = df[numeric_cols].corr()
    
    # Nomes mais amigáveis para os componentes
    component_names = {
        'sleep_quality': 'Qualidade do Sono',
        'sleep_duration': 'Duração do Sono',
        'stress_level': 'Nível de Estresse',
        'muscle_soreness': 'Dor Muscular',
        'energy_level': 'Nível de Energia',
        'motivation': 'Motivação',
        'nutrition_quality': 'Nutrição',
        'hydration': 'Hidratação',
        'score': 'Score Final'
    }
    
    # Renomeia os índices e colunas
    corr_matrix.index = [component_names[col] for col in corr_matrix.index]
    corr_matrix.columns = [component_names[col] for col in corr_matrix.columns]
    
    # Cria o heatmap
    fig = px.imshow(
        corr_matrix,
        text_auto='.2f',
        color_continuous_scale='RdBu_r',
        zmin=-1,
        zmax=1,
        aspect="auto"
    )
    
    fig.update_layout(
        height=500,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Insights automáticos
    st.subheader("Insights Automáticos")
    
    # Encontra os componentes mais correlacionados com o score
    score_corr = corr_matrix['Score Final'].drop('Score Final').sort_values(ascending=False)
    top_components = score_corr.head(3)
    
    insights = [
        f"Os componentes que mais impactam seu score de prontidão são: {', '.join(top_components.index)}.",
        f"Seu nível de prontidão tende a ser melhor às {best_day['weekday_pt']}s e pior às {worst_day['weekday_pt']}s.",
    ]
    
    # Adiciona insights sobre tendências
    if len(df) >= 14:
        recent_trend = df['score'].tail(7).mean() - df['score'].tail(14).head(7).mean()
        if abs(recent_trend) > 5:
            trend_direction = "melhorando" if recent_trend > 0 else "piorando"
            insights.append(f"Sua prontidão está {trend_direction} nas últimas semanas (variação de {abs(recent_trend):.1f} pontos).")
    
    # Exibe os insights
    for insight in insights:
        info_card("Insight", insight, "💡")

# Função principal
def main():
    """Função principal que controla o fluxo da página."""
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
