
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

class ReadinessAssessment:
    def __init__(self):
        self.questions = {
            'sleep_quality': 'Qualidade do sono (1 = muito ruim, 5 = excelente)',
            'muscle_soreness': 'Dor muscular (1 = muita dor, 5 = sem dor)',
            'fatigue_level': 'Nível de fadiga (1 = muito fatigado, 5 = sem fadiga)',
            'stress_level': 'Nível de estresse (1 = muito estressado, 5 = relaxado)',
            'mood': 'Humor (1 = muito irritado, 5 = muito feliz)',
            'appetite': 'Apetite (1 = sem apetite, 5 = apetite normal)',
            'motivation': 'Motivação para treinar (1 = desmotivado, 5 = muito motivado)',
            'recovery_perception': 'Percepção de recuperação (1 = não recuperado, 5 = totalmente recuperado)'
        }

    def calculate_score(self, responses):
        return sum(responses)

    def calculate_adjustment(self, score):
        max_score = 40  # 8 perguntas * 5 pontos cada
        return (score / max_score) * 100

    def get_recommendation(self, adjustment):
        if adjustment < 70:
            return "🔴 Sua prontidão está baixa. Considere reduzir significativamente a intensidade do treino hoje."
        elif adjustment < 85:
            return "🟡 Sua prontidão está moderada. Reduza um pouco a intensidade do treino hoje."
        else:
            return "🟢 Sua prontidão está boa. Você pode realizar o treino conforme planejado."

    def create_radar_chart(self, responses):
        categories = list(self.questions.keys())
        values = responses.copy()
        values += values[:1]

        angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False).tolist()
        angles += angles[:1]

        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
        ax.plot(angles, values, linewidth=2, linestyle='solid')
        ax.fill(angles, values, alpha=0.25)
        ax.set_thetagrids(np.degrees(angles[:-1]), categories)
        ax.set_ylim(0, 5)
        ax.grid(True)
        ax.set_title("Perfil de Prontidão", size=20, y=1.05)

        return fig

def show_readiness_assessment():
    st.header("Avaliação de Prontidão")

    assessment = ReadinessAssessment()

    with st.form("readiness_form"):
        responses = []
        for key, question in assessment.questions.items():
            response = st.slider(question, 1, 5, 3, key=f"readiness_{key}")
            responses.append(response)

        submit = st.form_submit_button("Calcular Prontidão")

    if submit:
        score = assessment.calculate_score(responses)
        adjustment = assessment.calculate_adjustment(score)

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Pontuação de Prontidão", f"{score}/40", f"{score/40*100:.1f}%")
        with col2:
            st.metric("Ajuste de Carga", f"{adjustment:.1f}%")

        st.markdown("---")

        # Gráfico de radar
        fig = assessment.create_radar_chart(responses)
        st.pyplot(fig)

        # Recomendação
        st.subheader("Recomendação")
        st.markdown(assessment.get_recommendation(adjustment))

        # Salvar no banco de dados
        if st.session_state.get('user_id'):
            saved = save_assessment(
                st.session_state.user_id,
                score,
                adjustment,
                responses
            )
            if saved:
                st.success("Avaliação salva com sucesso!")
            else:
                st.error("Erro ao salvar a avaliação.")

    # Histórico
    st.markdown("---")
    st.subheader("Histórico de Avaliações")

    if st.session_state.get('user_id'):
        period = st.selectbox("Período", [7, 14, 30], format_func=lambda x: f"Últimos {x} dias")
        assessments = get_user_assessments(st.session_state.user_id, days=period)

        if assessments:
            df = pd.DataFrame(assessments)
            df['created_at'] = pd.to_datetime(df['created_at'])
            df = df.sort_values('created_at')

            # Gráfico de tendência
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(df['created_at'], df['adjustment_percentage'], 
                   marker='o', linestyle='-', color='blue')
            ax.set_title('Tendência de Prontidão')
            ax.set_ylabel('Ajuste de Carga (%)')
            ax.set_ylim([0, 100])
            ax.grid(True)
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)

            # Estatísticas
            st.subheader("Estatísticas do Período")
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Média de Prontidão", 
                         f"{df['score'].mean():.1f}")
            with col2:
                st.metric("Ajuste Médio", 
                         f"{df['adjustment_percentage'].mean():.1f}%")
            with col3:
                st.metric("Total de Avaliações", 
                         len(df))
        else:
            st.info("Nenhuma avaliação encontrada para o período selecionado.")
