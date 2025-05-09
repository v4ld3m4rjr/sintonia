import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# Importar função do arquivo utils
from utils import init_supabase, get_psychological_assessments, save_psychological_assessment

def show_psychological_assessment():
    st.header("Avaliação Psicoemocional")
    st.markdown("""
    Esta avaliação utiliza questionários validados cientificamente para avaliar seu estado psicoemocional:
    * **DASS-21 (Depression Anxiety Stress Scale)**: Avalia ansiedade, depressão e estresse
    * **PSS-10 (Perceived Stress Scale)**: Avalia a percepção de estresse
    * **FANTASTIC (Lifestyle Assessment)**: Avalia estilo de vida
    """)
    
    # Criar tabs para cada questionário
    tab1, tab2, tab3 = st.tabs(["Ansiedade (DASS-21)", "Estresse (PSS-10)", "Estilo de Vida (FANTASTIC)"])
    
    # Inicializar variáveis
    anxiety_score = 0
    anxiety_responses = {}
    stress_score = 0
    stress_responses = {}
    lifestyle_score = 0
    lifestyle_responses = {}
    
    # Tab de Ansiedade (DASS-21 - apenas subescala de ansiedade)
    with tab1:
        st.subheader("Escala de Ansiedade DASS-21")
        st.markdown("Por favor, indique quanto cada afirmação se aplicou a você na última semana:")
        
        # Questões da subescala de ansiedade do DASS-21
        anxiety_questions = [
            "Senti minha boca seca",
            "Senti dificuldade em respirar",
            "Senti tremores (ex. nas mãos)",
            "Preocupei-me com situações em que eu pudesse entrar em pânico",
            "Senti que estava prestes a entrar em pânico",
            "Senti meu coração alterado mesmo não tendo feito esforço físico",
            "Senti medo sem motivo aparente"
        ]
        
        anxiety_options = {
            0: "Não se aplicou de maneira alguma",
            1: "Aplicou-se um pouco",
            2: "Aplicou-se de forma considerável",
            3: "Aplicou-se muito"
        }
        
        for i, question in enumerate(anxiety_questions):
            response = st.select_slider(
                question,
                options=[0, 1, 2, 3],
                format_func=lambda x: anxiety_options[x],
                key=f"anxiety_{i}"
            )
            anxiety_responses[question] = response
            anxiety_score += response
        
        # Interpretação do score de ansiedade
        st.metric("Score de Ansiedade", anxiety_score)
        
        if anxiety_score <= 7:
            st.success("Normal")
        elif anxiety_score <= 9:
            st.info("Leve")
        elif anxiety_score <= 14:
            st.warning("Moderado")
        elif anxiety_score <= 19:
            st.error("Severo")
        else:
            st.error("Extremamente Severo")
    
    # Tab de Estresse (PSS-10)
    with tab2:
        st.subheader("Escala de Estresse Percebido (PSS-10)")
        st.markdown("Indique com que frequência você se sentiu ou pensou de determinada maneira durante o último mês:")
        
        stress_questions = [
            "Você tem ficado triste por causa de algo que aconteceu inesperadamente?",
            "Você tem se sentido incapaz de controlar as coisas importantes em sua vida?",
            "Você tem se sentido nervoso e estressado?",
            "Você tem se sentido confiante na sua habilidade de resolver problemas pessoais?",
            "Você tem sentido que as coisas estão acontecendo de acordo com a sua vontade?",
            "Você tem achado que não conseguiria lidar com todas as coisas que você tem que fazer?",
            "Você tem conseguido controlar as irritações em sua vida?",
            "Você tem sentido que as coisas estão sob o seu controle?",
            "Você tem ficado irritado porque as coisas que acontecem estão fora do seu controle?",
            "Você tem sentido que as dificuldades se acumulam a ponto de você acreditar que não pode superá-las?"
        ]
        
        # Itens reversos (4, 5, 7, 8)
        reverse_items = [3, 4, 6, 7]
        
        stress_options = {
            0: "Nunca",
            1: "Quase nunca",
            2: "Às vezes",
            3: "Com alguma frequência",
            4: "Muito frequentemente"
        }
        
        for i, question in enumerate(stress_questions):
            response = st.select_slider(
                question,
                options=[0, 1, 2, 3, 4],
                format_func=lambda x: stress_options[x],
                key=f"stress_{i}"
            )
            
            # Inverter scores para itens reversos
            if i in reverse_items:
                score = 4 - response
            else:
                score = response
                
            stress_responses[question] = response
            stress_score += score
        
        # Interpretação do PSS
        st.metric("Score de Estresse", stress_score)
        
        if stress_score <= 13:
            st.success("Baixo Estresse")
        elif stress_score <= 26:
            st.info("Estresse Moderado")
        else:
            st.error("Estresse Alto")
    
    # Tab de Estilo de Vida (FANTASTIC)
    with tab3:
        st.subheader("Questionário de Estilo de Vida (FANTASTIC)")
        st.markdown("Responda às questões pensando no seu comportamento no último mês:")
        
        lifestyle_categories = {
            "F - Família e Amigos": [
                "Tenho alguém para conversar as coisas que são importantes para mim",
                "Dou e recebo afeto"
            ],
            "A - Atividade Física": [
                "Sou vigorosamente ativo pelo menos durante 30 minutos por dia",
                "Sou moderadamente ativo (jardinagem, caminhada, trabalho de casa)"
            ],
            "N - Nutrição": [
                "Como uma dieta balanceada",
                "Consumo alimentos com alto teor de açúcar ou sal",
                "Estou no intervalo de ___ kg do meu peso considerado saudável"
            ],
            "T - Tabaco e Tóxicos": [
                "Fumo cigarro",
                "Uso drogas como maconha e cocaína",
                "Abuso de remédios ou exagero"
            ],
            "A - Álcool": [
                "Minha ingestão média por semana de álcool é: ___ doses",
                "Dirijo após beber"
            ],
            "S - Sono, Cinto de segurança, Stress, Sexo seguro": [
                "Durmo bem e me sinto descansado",
                "Uso cinto de segurança",
                "Sou capaz de lidar com o estresse do meu dia-a-dia",
                "Relaxo e desfruto do meu tempo de lazer",
                "Pratico sexo seguro"
            ],
            "T - Tipo de comportamento": [
                "Aparento estar com pressa",
                "Sinto-me com raiva ou hostil"
            ],
            "I - Introspecção": [
                "Penso de forma positiva",
                "Sinto-me tenso ou desapontado",
                "Sinto-me triste ou deprimido"
            ],
            "C - Carreira": [
                "Estou satisfeito com meu trabalho ou função",
                "Uso adequadamente os recursos disponíveis no meu tempo e ambiente"
            ]
        }
        
        # Opções genéricas para a maioria das perguntas
        generic_options = {
            0: "Quase nunca",
            1: "Raramente",
            2: "Algumas vezes",
            3: "Com relativa frequência",
            4: "Quase sempre"
        }
        
        # Processar cada categoria e perguntas
        for category, questions in lifestyle_categories.items():
            st.markdown(f"**{category}**")
            
            for question in questions:
                response = st.select_slider(
                    question,
                    options=[0, 1, 2, 3, 4],
                    format_func=lambda x: generic_options[x],
                    key=f"lifestyle_{question}"
                )
                
                # Inverter score para perguntas negativos
                if "Fumo" in question or "drogas" in question or "Abuso" in question or "após beber" in question or "com pressa" in question or "raiva" in question or "tenso" in question or "triste" in question:
                    score = 4 - response
                else:
                    score = response
                    
                lifestyle_responses[question] = response
                lifestyle_score += score
        
        # Calcular porcentagem
        total_questions = sum(len(questions) for questions in lifestyle_categories.values())
        lifestyle_percentage = (lifestyle_score / (total_questions * 4)) * 100
        
        # Interpretação
        st.metric("Score de Estilo de Vida", f"{lifestyle_percentage:.1f}%")
        
        if lifestyle_percentage >= 85:
            st.success("Excelente - Continue assim!")
        elif lifestyle_percentage >= 70:
            st.info("Muito bom - Está no caminho certo")
        elif lifestyle_percentage >= 55:
            st.warning("Regular - Pode melhorar")
        elif lifestyle_percentage >= 35:
            st.error("Ruim - Atenção, mudar é preciso")
        else:
            st.error("Muito ruim - Necessita mudança urgente")
    
    # Análise e visualização para quem já tem histórico
    if st.session_state.get('user_id'):
        psych_history = get_psychological_assessments(st.session_state.user_id, days=7)
        
        if psych_history:
            st.subheader("Análise dos Últimos 7 Dias")
            
            # Preparar dados
            df = pd.DataFrame(psych_history)
            df['created_at'] = pd.to_datetime(df['created_at'])
            
            # Gráfico de linhas para todas as métricas
            fig, ax = plt.subplots(figsize=(10, 6))
            
            if 'anxiety_score' in df.columns:
                ax.plot(df['created_at'], df['anxiety_score'], 'o-', label='Ansiedade')
            
            if 'stress_score' in df.columns:
                ax.plot(df['created_at'], df['stress_score'], 's-', label='Estresse')
            
            if 'lifestyle_score' in df.columns:
                # Normalizar para mesma escala
                lifestyle_norm = df['lifestyle_score'] / df['lifestyle_score'].max() * 40  # 40 é o máximo da escala de estresse
                ax.plot(df['created_at'], lifestyle_norm, '^-', label='Estilo de Vida (normalizado)')
            
            ax.set_title('Tendências Psicológicas')
            ax.set_ylabel('Score')
            ax.set_xlabel('Data')
            ax.grid(True, alpha=0.3)
            ax.legend()
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            st.pyplot(fig)
            
            # Matriz de correlação
            if len(df) >= 3 and 'anxiety_score' in df.columns and 'stress_score' in df.columns and 'lifestyle_score' in df.columns:
                st.subheader("Correlações entre Variáveis")
                
                # Preparar dados para correlação
                corr_data = {
                    'Ansiedade': df['anxiety_score'],
                    'Estresse': df['stress_score'],
                    'Estilo de Vida': df['lifestyle_score']
                }
                
                df_corr = pd.DataFrame(corr_data)
                corr_matrix = df_corr.corr()
                
                # Plotar heatmap
                fig, ax = plt.subplots(figsize=(8, 6))
                sns.heatmap(corr_matrix,
                           annot=True,
                           cmap='RdYlBu_r',
                           vmin=-1,
                           vmax=1,
                           center=0)
                plt.title("Correlações Psicológicas")
                
                st.pyplot(fig)
                
                # Interpretação das correlações
                anxiety_stress_corr = corr_matrix.loc['Ansiedade', 'Estresse']
                anxiety_lifestyle_corr = corr_matrix.loc['Ansiedade', 'Estilo de Vida']
                stress_lifestyle_corr = corr_matrix.loc['Estresse', 'Estilo de Vida']
                
                st.markdown("#### Interpretação das Correlações")
                
                if anxiety_stress_corr > 0.5:
                    st.info("Forte correlação positiva entre ansiedade e estresse - Eles tendem a aumentar juntos.")
                elif anxiety_stress_corr < -0.5:
                    st.info("Forte correlação negativa entre ansiedade e estresse - Quando um aumenta, o outro tende a diminuir.")
                
                if anxiety_lifestyle_corr < -0.5:
                    st.success("Seu estilo de vida parece ajudar a reduzir a ansiedade!")
                elif anxiety_lifestyle_corr > 0.5:
                    st.warning("Seu estilo de vida pode estar contribuindo para a ansiedade.")
                
                if stress_lifestyle_corr < -0.5:
                    st.success("Seu estilo de vida parece ajudar a reduzir o estresse!")
                elif stress_lifestyle_corr > 0.5:
                    st.warning("Seu estilo de vida pode estar contribuindo para o estresse.")
    
    # Botão para salvar
    if st.button("Salvar Avaliação Psicoemocional"):
        if not st.session_state.get('user_id'):
            st.error("Faça login para salvar avaliações")
            return
            
        try:
            assessment_id = save_psychological_assessment(
                st.session_state.user_id,
                anxiety_score,
                stress_score,
                lifestyle_score,
                anxiety_responses,
                stress_responses,
                lifestyle_responses
            )
            
            if assessment_id:
                st.success("Avaliação psicoemocional salva com sucesso!")
                
                # Atualizar histórico na sessão
                new_entry = {
                    "id": assessment_id,
                    "date": datetime.now(),
                    "anxiety_score": anxiety_score,
                    "stress_score": stress_score,
                    "lifestyle_score": lifestyle_score
                }
                
                if 'psychological_history' not in st.session_state:
                    st.session_state.psychological_history = []
                    
                st.session_state.psychological_history.append(new_entry)
            else:
                st.error("Erro ao salvar avaliação")
        except Exception as e:
            st.error(f"Erro: {str(e)}")