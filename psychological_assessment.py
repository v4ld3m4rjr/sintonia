
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

class PsychologicalAssessment:
    def __init__(self):
        self.dass21_questions = {
            'anxiety': [
                "Senti minha boca seca",
                "Tive dificuldade em respirar",
                "Senti tremores (ex: nas mãos)",
                "Preocupei-me com situações em que eu pudesse entrar em pânico",
                "Senti que estava prestes a entrar em pânico",
                "Senti meu coração alterado mesmo sem fazer exercício físico",
                "Senti medo sem motivo aparente"
            ],
            'stress': [
                "Tive dificuldade para me acalmar",
                "Tendi a reagir de forma exagerada às situações",
                "Senti que estava muito nervoso",
                "Senti-me agitado",
                "Achei difícil relaxar",
                "Fui intolerante com as coisas que me impediam de continuar o que eu estava fazendo",
                "Senti que estava muito irritável"
            ]
        }

        self.lifestyle_questions = {
            'physical': [
                "Pratico atividade física regularmente",
                "Mantenho uma alimentação saudável",
                "Tenho um sono regular e restaurador"
            ],
            'social': [
                "Mantenho boas relações sociais",
                "Tenho tempo para lazer",
                "Sinto-me apoiado por amigos/família"
            ],
            'mental': [
                "Consigo manter o foco nas tarefas",
                "Lido bem com o estresse",
                "Sinto-me satisfeito com minha vida"
            ]
        }

    def calculate_dass21_scores(self, anxiety_responses, stress_responses):
        anxiety_score = sum(anxiety_responses)
        stress_score = sum(stress_responses)

        return {
            'anxiety': {
                'score': anxiety_score,
                'level': self.get_anxiety_level(anxiety_score)
            },
            'stress': {
                'score': stress_score,
                'level': self.get_stress_level(stress_score)
            }
        }

    def calculate_lifestyle_score(self, responses):
        return sum(responses) / len(responses) * 100

    def get_anxiety_level(self, score):
        if score <= 7:
            return "Normal", "🟢"
        elif score <= 9:
            return "Leve", "🟡"
        elif score <= 14:
            return "Moderado", "🟠"
        else:
            return "Severo", "🔴"

    def get_stress_level(self, score):
        if score <= 14:
            return "Normal", "🟢"
        elif score <= 18:
            return "Leve", "🟡"
        elif score <= 25:
            return "Moderado", "🟠"
        else:
            return "Severo", "🔴"

    def get_lifestyle_recommendation(self, score):
        if score >= 80:
            return "✨ Excelente estilo de vida! Continue mantendo esses hábitos saudáveis."
        elif score >= 60:
            return "👍 Bom estilo de vida. Considere pequenas melhorias nas áreas mais fracas."
        else:
            return "💪 Há espaço para melhorias. Foque em desenvolver hábitos mais saudáveis gradualmente."

def show_psychological_assessment():
    st.header("Avaliação Psicoemocional")

    assessment = PsychologicalAssessment()

    tabs = st.tabs(["DASS-21", "Estilo de Vida", "Histórico"])

    with tabs[0]:
        st.subheader("Escala de Ansiedade e Estresse (DASS-21)")

        with st.form("dass21_form"):
            st.write("Indique como você tem se sentido na última semana:")

            anxiety_responses = []
            stress_responses = []

            st.write("**Ansiedade**")
            for question in assessment.dass21_questions['anxiety']:
                response = st.slider(
                    question,
                    min_value=0,
                    max_value=3,
                    value=0,
                    help="0 = Não se aplicou; 3 = Aplicou-se muito"
                )
                anxiety_responses.append(response)

            st.write("**Estresse**")
            for question in assessment.dass21_questions['stress']:
                response = st.slider(
                    question,
                    min_value=0,
                    max_value=3,
                    value=0,
                    help="0 = Não se aplicou; 3 = Aplicou-se muito"
                )
                stress_responses.append(response)

            submit_dass = st.form_submit_button("Calcular Resultados")

        if submit_dass:
            scores = assessment.calculate_dass21_scores(
                anxiety_responses,
                stress_responses
            )

            col1, col2 = st.columns(2)

            with col1:
                anxiety_level, anxiety_icon = scores['anxiety']['level']
                st.metric(
                    "Nível de Ansiedade",
                    f"{anxiety_level} {anxiety_icon}",
                    f"Score: {scores['anxiety']['score']}"
                )

            with col2:
                stress_level, stress_icon = scores['stress']['level']
                st.metric(
                    "Nível de Estresse",
                    f"{stress_level} {stress_icon}",
                    f"Score: {scores['stress']['score']}"
                )

            # Salvar no banco de dados
            if st.session_state.get('user_id'):
                saved = save_psychological_assessment(
                    st.session_state.user_id,
                    scores['anxiety']['score'],
                    scores['stress']['score'],
                    0,  # lifestyle_score será atualizado depois
                    anxiety_responses,
                    stress_responses,
                    []  # lifestyle_responses será atualizado depois
                )
                if saved:
                    st.success("Avaliação DASS-21 salva com sucesso!")
                else:
                    st.error("Erro ao salvar a avaliação DASS-21.")

    with tabs[1]:
        st.subheader("Avaliação de Estilo de Vida")

        with st.form("lifestyle_form"):
            lifestyle_responses = []

            for category, questions in assessment.lifestyle_questions.items():
                st.write(f"**{category.title()}**")
                for question in questions:
                    response = st.slider(
                        question,
                        min_value=1,
                        max_value=5,
                        value=3,
                        help="1 = Nunca; 5 = Sempre"
                    )
                    lifestyle_responses.append(response)

            submit_lifestyle = st.form_submit_button("Calcular Resultado")

        if submit_lifestyle:
            lifestyle_score = assessment.calculate_lifestyle_score(lifestyle_responses)

            st.metric(
                "Pontuação de Estilo de Vida",
                f"{lifestyle_score:.1f}%"
            )

            st.info(assessment.get_lifestyle_recommendation(lifestyle_score))

            # Gráfico radar para categorias
            categories = list(assessment.lifestyle_questions.keys())
            values = []

            start_idx = 0
            for category in categories:
                category_questions = assessment.lifestyle_questions[category]
                category_responses = lifestyle_responses[start_idx:start_idx + len(category_questions)]
                values.append(np.mean(category_responses))
                start_idx += len(category_questions)

            # Criar gráfico radar
            angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False)
            values = np.concatenate((values, [values[0]]))  # Fechar o polígono
            angles = np.concatenate((angles, [angles[0]]))  # Fechar o polígono

            fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
            ax.plot(angles, values)
            ax.fill(angles, values, alpha=0.25)
            ax.set_xticks(angles[:-1])
            ax.set_xticklabels(categories)
            ax.set_ylim(0, 5)
            plt.title("Perfil de Estilo de Vida")
            st.pyplot(fig)

    with tabs[2]:
        st.subheader("Histórico de Avaliações")

        if st.session_state.get('user_id'):
            period = st.selectbox(
                "Período de Análise",
                [7, 14, 30, 90],
                format_func=lambda x: f"Últimos {x} dias"
            )

            # Buscar dados históricos
            psych_data = get_psychological_assessments(st.session_state.user_id, days=period)

            if psych_data:
                df = pd.DataFrame(psych_data)
                df['created_at'] = pd.to_datetime(df['created_at'])
                df = df.sort_values('created_at')

                # Gráfico de tendências
                fig, ax = plt.subplots(figsize=(12, 6))
                ax.plot(df['created_at'], df['anxiety_score'],
                       label='Ansiedade', marker='o')
                ax.plot(df['created_at'], df['stress_score'],
                       label='Estresse', marker='s')
                ax.set_title('Evolução dos Níveis de Ansiedade e Estresse')
                ax.set_ylabel('Score')
                ax.legend()
                ax.grid(True)
                plt.xticks(rotation=45)
                plt.tight_layout()
                st.pyplot(fig)

                # Estatísticas do período
                st.subheader("Estatísticas do Período")
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Ansiedade Média",
                        f"{df['anxiety_score'].mean():.1f}"
                    )
                with col2:
                    st.metric(
                        "Estresse Médio",
                        f"{df['stress_score'].mean():.1f}"
                    )
                with col3:
                    st.metric(
                        "Estilo de Vida Médio",
                        f"{df['lifestyle_score'].mean():.1f}%"
                    )

            else:
                st.info("Nenhuma avaliação encontrada para o período selecionado.")
