
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

class TrainingAssessment:
    def __init__(self):
        self.rpe_scale = {
            0: "Repouso",
            1: "Muito, muito leve",
            2: "Muito leve",
            3: "Leve",
            4: "Moderado",
            5: "Um pouco pesado",
            6: "Pesado",
            7: "Muito pesado",
            8: "Muito, muito pesado",
            9: "Máximo",
            10: "Extremamente máximo"
        }

    def calculate_trimp(self, duration, heart_rate, rpe):
        """Calcula o TRIMP usando o método de Foster"""
        return duration * rpe

    def calculate_training_load(self, trimp, previous_loads):
        """Calcula carga aguda (7 dias) e crônica (28 dias)"""
        acute_load = np.mean([trimp] + previous_loads[:6]) if previous_loads else trimp
        chronic_load = np.mean([trimp] + previous_loads[:27]) if previous_loads else trimp

        # Cálculo do ratio acute:chronic (ACWR)
        acwr = acute_load / chronic_load if chronic_load > 0 else 1

        return {
            'acute_load': acute_load,
            'chronic_load': chronic_load,
            'acwr': acwr
        }

    def calculate_injury_risk(self, acwr):
        """Calcula o risco de lesão baseado no ACWR"""
        if acwr < 0.8:
            return "Baixo", "🟢"
        elif 0.8 <= acwr <= 1.3:
            return "Moderado", "🟡"
        else:
            return "Alto", "🔴"

    def get_recommendation(self, acwr, rpe):
        """Gera recomendações baseadas no ACWR e RPE"""
        risk_level, _ = self.calculate_injury_risk(acwr)

        if risk_level == "Alto":
            return "⚠️ Risco elevado de lesão. Considere reduzir a carga de treino e aumentar recuperação."
        elif risk_level == "Moderado":
            return "✅ Carga de treino adequada. Continue monitorando as respostas ao treino."
        else:
            return "📈 Carga de treino pode ser aumentada progressivamente se houver boa recuperação."

def show_training_assessment():
    st.header("Avaliação do Estado de Treino")

    assessment = TrainingAssessment()

    with st.form("training_form"):
        col1, col2 = st.columns(2)

        with col1:
            duration = st.number_input("Duração do treino (minutos)", 
                                     min_value=0, max_value=300, value=60)
            heart_rate = st.number_input("Frequência cardíaca média", 
                                       min_value=40, max_value=220, value=140)

        with col2:
            rpe = st.slider("Percepção de Esforço (RPE)", 
                          min_value=0, max_value=10, value=5,
                          help="Escala de Borg CR-10")
            st.write(f"Descrição: {assessment.rpe_scale[rpe]}")

        notes = st.text_area("Observações do treino", 
                           help="Adicione notas sobre o treino realizado")

        submit = st.form_submit_button("Calcular Métricas")

    if submit:
        # Calcular TRIMP
        trimp = assessment.calculate_trimp(duration, heart_rate, rpe)

        # Buscar cargas anteriores
        previous_loads = []  # Aqui você deve buscar do banco de dados

        # Calcular métricas de carga
        load_metrics = assessment.calculate_training_load(trimp, previous_loads)

        # Calcular risco de lesão
        risk_level, risk_icon = assessment.calculate_injury_risk(load_metrics['acwr'])

        # Exibir métricas
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("TRIMP", f"{trimp:.1f}")
        with col2:
            st.metric("Carga Aguda (7d)", f"{load_metrics['acute_load']:.1f}")
        with col3:
            st.metric("Carga Crônica (28d)", f"{load_metrics['chronic_load']:.1f}")
        with col4:
            st.metric("ACWR", f"{load_metrics['acwr']:.2f}")

        # Exibir risco e recomendações
        st.subheader(f"Risco de Lesão: {risk_icon} {risk_level}")
        st.info(assessment.get_recommendation(load_metrics['acwr'], rpe))

        # Salvar no banco de dados
        if st.session_state.get('user_id'):
            saved = save_training_assessment(
                st.session_state.user_id,
                duration,
                rpe,
                heart_rate,
                trimp,
                load_metrics['acute_load'],
                notes
            )
            if saved:
                st.success("Avaliação salva com sucesso!")
            else:
                st.error("Erro ao salvar a avaliação.")

    # Histórico e Análises
    st.markdown("---")
    st.subheader("Análise de Cargas de Treino")

    if st.session_state.get('user_id'):
        period = st.selectbox("Período de Análise", 
                            [7, 14, 28, 90], 
                            format_func=lambda x: f"Últimos {x} dias")

        # Buscar dados históricos
        training_data = get_user_training_assessments(st.session_state.user_id, days=period)

        if training_data:
            df = pd.DataFrame(training_data)
            df['created_at'] = pd.to_datetime(df['created_at'])
            df = df.sort_values('created_at')

            # Gráfico de cargas
            fig, ax = plt.subplots(figsize=(12, 6))
            ax.plot(df['created_at'], df['acute_load'], 
                   label='Carga Aguda', marker='o')
            ax.plot(df['created_at'], df['chronic_load'], 
                   label='Carga Crônica', marker='s')
            ax.set_title('Evolução das Cargas de Treino')
            ax.set_ylabel('Carga (UA)')
            ax.legend()
            ax.grid(True)
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)

            # Estatísticas do período
            st.subheader("Estatísticas do Período")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("TRIMP Médio", 
                         f"{df['trimp'].mean():.1f}")
            with col2:
                st.metric("RPE Médio", 
                         f"{df['rpe'].mean():.1f}")
            with col3:
                st.metric("Duração Média", 
                         f"{df['duration'].mean():.0f} min")

            # Distribuição de intensidade
            st.subheader("Distribuição de Intensidade")
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.histplot(data=df, x='rpe', bins=10)
            ax.set_title('Distribuição de RPE')
            ax.set_xlabel('RPE')
            ax.set_ylabel('Frequência')
            st.pyplot(fig)

        else:
            st.info("Nenhum dado de treino encontrado para o período selecionado.")
