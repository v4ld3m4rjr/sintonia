
# mental_assessment.py
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from datetime import datetime
import supabase
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração do Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Inicializar cliente Supabase
supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)

# Definição dos questionários
questionnaires = {
    "anxiety": {
        "title": "Avaliação de Ansiedade (GAD-7)",
        "questions": [
            "Sentir-se nervoso, ansioso ou muito tenso",
            "Não ser capaz de impedir ou de controlar as preocupações",
            "Preocupar-se muito com diversas coisas",
            "Dificuldade para relaxar",
            "Ficar tão agitado que se torna difícil permanecer sentado",
            "Ficar facilmente aborrecido ou irritado",
            "Sentir medo como se algo terrível fosse acontecer"
        ],
        "options": ["Nunca", "Vários dias", "Mais da metade dos dias", "Quase todos os dias"],
        "scores": [0, 1, 2, 3]
    },
    "stress": {
        "title": "Escala de Estresse Percebido (PSS-10)",
        "questions": [
            "Você tem ficado triste por causa de algo que aconteceu inesperadamente?",
            "Você tem se sentido incapaz de controlar as coisas importantes em sua vida?",
            "Você tem se sentido nervoso e estressado?",
            "Você tem tratado com sucesso dos problemas difíceis da vida?",
            "Você tem sentido que está lidando bem com as mudanças importantes que estão ocorrendo em sua vida?",
            "Você tem se sentido confiante na sua habilidade de resolver problemas pessoais?",
            "Você tem sentido que as coisas estão acontecendo de acordo com a sua vontade?",
            "Você tem achado que não conseguiria lidar com todas as coisas que você tem que fazer?",
            "Você tem conseguido controlar as irritações em sua vida?",
            "Você tem sentido que as coisas estão sob o seu controle?"
        ],
        "options": ["Nunca", "Quase nunca", "Às vezes", "Frequentemente", "Muito frequentemente"],
        "scores": [0, 1, 2, 3, 4],
        "reverse_items": [3, 4, 5, 6, 9]  # 0-indexed items that need reverse scoring
    },
    "mental_fatigue": {
        "title": "Escala de Fadiga Mental (MFS)",
        "questions": [
            "Fadiga em geral",
            "Necessidade de mais sono/descanso",
            "Sonolência/torpor",
            "Irritabilidade",
            "Sensibilidade ao estresse",
            "Diminuição da concentração",
            "Diminuição da memória",
            "Tempo de recuperação prolongado",
            "Diminuição da tolerância a ruídos",
            "Diminuição da tolerância à luz",
            "Diminuição da tolerância a situações sociais",
            "Diminuição da iniciativa/capacidade de começar atividades",
            "Diminuição da resistência/capacidade de lidar com situações estressantes",
            "Diminuição da capacidade de realizar várias tarefas simultaneamente"
        ],
        "options": ["Nunca presente", "Presente, mas não perturbador", "Presente, perturbador mas não severo", "Presente e severo"],
        "scores": [0, 1, 2, 3]
    }
}

def interpret_score(assessment_type, score):
    """Interpreta a pontuação com base no tipo de avaliação"""
    if assessment_type == "anxiety":
        if score < 5:
            return "Mínima"
        elif score < 10:
            return "Leve"
        elif score < 15:
            return "Moderada"
        else:
            return "Severa"

    elif assessment_type == "stress":
        if score < 14:
            return "Baixo"
        elif score < 27:
            return "Moderado"
        else:
            return "Alto"

    elif assessment_type == "mental_fatigue":
        if score < 10.5:
            return "Baixa"
        elif score < 21:
            return "Moderada"
        else:
            return "Alta"

    return "Não interpretado"

def get_recommendations(assessment_type, interpretation):
    """Retorna recomendações com base no tipo de avaliação e interpretação"""
    recommendations = []

    if assessment_type == "anxiety":
        if interpretation in ["Mínima", "Leve"]:
            recommendations = [
                "Pratique técnicas de respiração profunda diariamente",
                "Mantenha uma rotina regular de exercícios físicos",
                "Considere a prática de mindfulness ou meditação"
            ]
        else:  # Moderada ou Severa
            recommendations = [
                "Considere consultar um profissional de saúde mental",
                "Pratique técnicas de respiração e relaxamento regularmente",
                "Estabeleça uma rotina de sono saudável",
                "Limite o consumo de cafeína e álcool",
                "Pratique exercícios físicos regularmente"
            ]

    elif assessment_type == "stress":
        if interpretation == "Baixo":
            recommendations = [
                "Continue com suas práticas atuais de gerenciamento de estresse",
                "Mantenha um equilíbrio saudável entre trabalho e vida pessoal",
                "Pratique atividades que você goste regularmente"
            ]
        elif interpretation == "Moderado":
            recommendations = [
                "Incorpore técnicas de relaxamento em sua rotina diária",
                "Considere limitar o tempo em mídias sociais e notícias",
                "Priorize o autocuidado e o descanso adequado",
                "Pratique exercícios físicos regularmente"
            ]
        else:  # Alto
            recommendations = [
                "Considere consultar um profissional de saúde mental",
                "Identifique e tente reduzir as principais fontes de estresse",
                "Pratique técnicas de relaxamento diariamente",
                "Estabeleça limites claros entre trabalho e vida pessoal",
                "Priorize o sono e a alimentação saudável"
            ]

    elif assessment_type == "mental_fatigue":
        if interpretation == "Baixa":
            recommendations = [
                "Mantenha uma rotina regular de sono",
                "Continue com pausas regulares durante atividades mentalmente exigentes",
                "Pratique exercícios físicos regularmente"
            ]
        elif interpretation == "Moderada":
            recommendations = [
                "Aumente a frequência de pausas durante o trabalho mental",
                "Considere técnicas de gerenciamento de energia",
                "Priorize o sono de qualidade",
                "Limite o tempo de tela, especialmente antes de dormir"
            ]
        else:  # Alta
            recommendations = [
                "Considere consultar um profissional de saúde",
                "Implemente pausas frequentes e regulares durante atividades mentais",
                "Pratique técnicas de recuperação cognitiva",
                "Priorize o sono e o descanso adequado",
                "Considere reduzir temporariamente a carga de trabalho mental"
            ]

    return recommendations

def save_result_to_supabase(user_id, assessment_type, score, interpretation, date):
    """Salva o resultado da avaliação no Supabase"""
    try:
        data = {
            "user_id": user_id,
            "assessment_type": assessment_type,
            "score": score,
            "interpretation": interpretation,
            "date": date
        }

        # Inserir dados na tabela mental_assessments
        response = supabase_client.table("mental_assessments").insert(data).execute()

        if hasattr(response, 'error') and response.error:
            st.error(f"Erro ao salvar dados: {response.error.message}")
            return False

        return True
    except Exception as e:
        st.error(f"Erro ao salvar dados: {str(e)}")
        return False

def get_user_assessment_history(user_id, assessment_type=None):
    """Obtém o histórico de avaliações do usuário do Supabase"""
    try:
        query = supabase_client.table("mental_assessments").select("*").eq("user_id", user_id)

        if assessment_type:
            query = query.eq("assessment_type", assessment_type)

        response = query.order("date", desc=False).execute()

        if hasattr(response, 'error') and response.error:
            st.error(f"Erro ao buscar dados: {response.error.message}")
            return []

        return response.data
    except Exception as e:
        st.error(f"Erro ao buscar dados: {str(e)}")
        return []

def plot_assessment_history(history, assessment_type):
    """Cria um gráfico do histórico de avaliações"""
    if not history:
        return None

    # Filtrar apenas o tipo de avaliação desejado
    filtered_history = [item for item in history if item['assessment_type'] == assessment_type]

    if not filtered_history:
        return None

    # Preparar dados para o gráfico
    dates = [item['date'] for item in filtered_history]
    scores = [item['score'] for item in filtered_history]

    # Criar figura
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(dates, scores, marker='o', linestyle='-', color='#1f77b4')

    # Adicionar título e rótulos
    title = f"Histórico de {questionnaires[assessment_type]['title']}"
    ax.set_title(title)
    ax.set_xlabel("Data")
    ax.set_ylabel("Pontuação")

    # Adicionar grade
    ax.grid(True, linestyle='--', alpha=0.7)

    # Rotacionar datas no eixo x para melhor legibilidade
    plt.xticks(rotation=45)

    # Ajustar layout
    plt.tight_layout()

    return fig

def mental_assessment_page():
    """Página principal de avaliação mental"""
    st.title("Avaliação Mental")

    # Verificar se o usuário está logado
    if 'user_id' not in st.session_state:
        st.warning("Por favor, faça login para acessar as avaliações mentais.")
        return

    user_id = st.session_state['user_id']

    # Tabs para diferentes seções
    tab1, tab2 = st.tabs(["Nova Avaliação", "Histórico"])

    with tab1:
        st.header("Nova Avaliação")
        st.write("Selecione uma avaliação para começar:")

        # Seleção do tipo de avaliação
        assessment_options = {
            "anxiety": "Ansiedade (GAD-7)",
            "stress": "Estresse (PSS-10)",
            "mental_fatigue": "Fadiga Mental (MFS)"
        }

        assessment_type = st.selectbox(
            "Tipo de Avaliação:",
            options=list(assessment_options.keys()),
            format_func=lambda x: assessment_options[x]
        )

        # Inicializar ou resetar as respostas se necessário
        if 'current_assessment' not in st.session_state or st.session_state.current_assessment != assessment_type:
            st.session_state.current_assessment = assessment_type
            st.session_state.answers = []
            st.session_state.current_question = 0
            st.session_state.assessment_complete = False

        # Mostrar questionário
        if not st.session_state.assessment_complete:
            questionnaire = questionnaires[assessment_type]

            # Mostrar progresso
            progress = st.progress((st.session_state.current_question) / len(questionnaire["questions"]))

            # Mostrar questão atual
            st.subheader(f"Questão {st.session_state.current_question + 1}/{len(questionnaire['questions'])}")
            st.write(questionnaire["questions"][st.session_state.current_question])

            # Opções de resposta
            answer = st.radio(
                "Sua resposta:",
                options=questionnaire["options"],
                key=f"q_{st.session_state.current_question}"
            )

            # Botões de navegação
            col1, col2 = st.columns(2)

            with col1:
                if st.session_state.current_question > 0:
                    if st.button("Anterior"):
                        st.session_state.current_question -= 1
                        st.experimental_rerun()

            with col2:
                if st.button("Próximo" if st.session_state.current_question < len(questionnaire["questions"]) - 1 else "Finalizar"):
                    # Salvar resposta atual
                    answer_index = questionnaire["options"].index(answer)

                    if len(st.session_state.answers) <= st.session_state.current_question:
                        st.session_state.answers.append(answer_index)
                    else:
                        st.session_state.answers[st.session_state.current_question] = answer_index

                    # Avançar para próxima questão ou finalizar
                    if st.session_state.current_question < len(questionnaire["questions"]) - 1:
                        st.session_state.current_question += 1
                    else:
                        # Calcular resultado
                        total_score = 0
                        for i, answer_index in enumerate(st.session_state.answers):
                            score = questionnaire["scores"][answer_index]

                            # Lidar com pontuação reversa para PSS-10
                            if assessment_type == "stress" and i in questionnaire.get("reverse_items", []):
                                score = 4 - score  # Reverter a pontuação (0->4, 1->3, 2->2, 3->1, 4->0)

                            total_score += score

                        # Interpretar pontuação
                        interpretation = interpret_score(assessment_type, total_score)

                        # Salvar resultado no Supabase
                        current_date = datetime.now().isoformat()
                        save_result_to_supabase(user_id, assessment_type, total_score, interpretation, current_date)

                        # Armazenar resultado na sessão
                        st.session_state.result = {
                            "score": total_score,
                            "interpretation": interpretation,
                            "date": current_date
                        }

                        st.session_state.assessment_complete = True

                    st.experimental_rerun()

        # Mostrar resultados se a avaliação estiver completa
        if st.session_state.get('assessment_complete', False):
            st.subheader("Resultados")

            result = st.session_state.result
            questionnaire = questionnaires[assessment_type]

            # Mostrar pontuação e interpretação
            st.write(f"**Pontuação total:** {result['score']}")
            st.write(f"**Interpretação:** {result['interpretation']}")

            # Criar gráfico visual da pontuação
            fig, ax = plt.subplots(figsize=(10, 2))

            # Definir faixas de pontuação com base no tipo de avaliação
            if assessment_type == "anxiety":
                max_score = 21
                ranges = [(0, 4, "Mínima", "#4CAF50"), 
                          (5, 9, "Leve", "#8BC34A"), 
                          (10, 14, "Moderada", "#FFC107"), 
                          (15, 21, "Severa", "#F44336")]
            elif assessment_type == "stress":
                max_score = 40
                ranges = [(0, 13, "Baixo", "#4CAF50"), 
                          (14, 26, "Moderado", "#FFC107"), 
                          (27, 40, "Alto", "#F44336")]
            else:  # mental_fatigue
                max_score = 42
                ranges = [(0, 10.5, "Baixa", "#4CAF50"), 
                          (10.5, 21, "Moderada", "#FFC107"), 
                          (21, 42, "Alta", "#F44336")]

            # Criar barras para cada faixa
            for start, end, label, color in ranges:
                ax.barh([0], [end-start], left=[start], height=0.5, color=color, alpha=0.7)
                ax.text((start+end)/2, 0, label, ha='center', va='center', color='black')

            # Marcar a pontuação do usuário
            ax.plot([result['score'], result['score']], [-0.5, 0.5], 'k-', linewidth=2)
            ax.plot(result['score'], 0, 'ko', markersize=10)

            # Configurar eixos
            ax.set_xlim(0, max_score)
            ax.set_ylim(-0.5, 0.5)
            ax.set_yticks([])
            ax.set_xlabel("Pontuação")
            ax.set_title(f"Sua pontuação: {result['score']} - {result['interpretation']}")

            # Mostrar gráfico
            st.pyplot(fig)

            # Mostrar recomendações
            st.subheader("Recomendações")
            recommendations = get_recommendations(assessment_type, result['interpretation'])
            for rec in recommendations:
                st.write(f"• {rec}")

            # Botão para nova avaliação
            if st.button("Iniciar Nova Avaliação"):
                st.session_state.pop('current_assessment', None)
                st.session_state.pop('answers', None)
                st.session_state.pop('current_question', None)
                st.session_state.pop('assessment_complete', None)
                st.session_state.pop('result', None)
                st.experimental_rerun()

    with tab2:
        st.header("Histórico de Avaliações")

        # Filtro de tipo de avaliação
        history_assessment_type = st.selectbox(
            "Filtrar por tipo:",
            options=list(assessment_options.keys()) + ["todos"],
            format_func=lambda x: assessment_options.get(x, "Todos os tipos"),
            key="history_filter"
        )

        # Buscar histórico do usuário
        if history_assessment_type == "todos":
            history = get_user_assessment_history(user_id)
        else:
            history = get_user_assessment_history(user_id, history_assessment_type)

        if not history:
            st.info("Nenhuma avaliação encontrada no histórico.")
        else:
            # Mostrar tabela de histórico
            history_df = pd.DataFrame(history)
            history_df['date'] = pd.to_datetime(history_df['date']).dt.strftime('%d/%m/%Y %H:%M')
            history_df['assessment_type'] = history_df['assessment_type'].map({
                'anxiety': 'Ansiedade',
                'stress': 'Estresse',
                'mental_fatigue': 'Fadiga Mental'
            })

            # Renomear colunas para português
            history_df = history_df.rename(columns={
                'assessment_type': 'Tipo',
                'score': 'Pontuação',
                'interpretation': 'Interpretação',
                'date': 'Data'
            })

            # Selecionar e ordenar colunas
            display_df = history_df[['Data', 'Tipo', 'Pontuação', 'Interpretação']].sort_values('Data', ascending=False)

            st.dataframe(display_df)

            # Mostrar gráficos para cada tipo de avaliação
            st.subheader("Gráficos de Progresso")

            if history_assessment_type == "todos":
                # Mostrar gráficos para cada tipo
                for assessment_type in assessment_options.keys():
                    fig = plot_assessment_history(history, assessment_type)
                    if fig:
                        st.write(f"### {assessment_options[assessment_type]}")
                        st.pyplot(fig)
            else:
                # Mostrar gráfico apenas para o tipo selecionado
                fig = plot_assessment_history(history, history_assessment_type)
                if fig:
                    st.pyplot(fig)
