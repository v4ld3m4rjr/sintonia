import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import sqlite3
import os
from utils import calculate_score, ajuste_carga
from database import save_assessment, get_historico, create_tables

# Configuração da página
st.set_page_config(
    page_title="Avaliação de Prontidão para Treino",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Verificar se o banco de dados existe e inicializá-lo
try:
    # Inicialização do banco de dados
    create_tables()
    st.sidebar.success("Banco de dados inicializado com sucesso!")
except Exception as e:
    st.sidebar.error(f"Erro ao inicializar o banco de dados: {e}")
    st.stop()

# Sidebar para navegação
st.sidebar.title("Navegação")
page = st.sidebar.radio("Ir para:", ["Formulário de Avaliação", "Histórico", "Painel Admin"])

# Página do formulário
if page == "Formulário de Avaliação":
    st.title("Avaliação de Prontidão para Treino")
    st.subheader("Preencha o formulário abaixo para avaliar sua condição atual")

    # Em um ambiente real, o ID do usuário viria do sistema de login
    usuario_id = st.sidebar.number_input("ID do Usuário (simulação)", min_value=1, value=1)

    with st.form("assessment_form"):
        col1, col2 = st.columns(2)

        with col1:
            sono = st.slider("Qualidade do Sono", 1, 5, 3, 
                            help="1 = Muito ruim, 5 = Excelente")
            fadiga = st.slider("Nível de Fadiga", 1, 5, 3, 
                              help="1 = Extremamente fatigado, 5 = Sem fadiga")
            dor = st.slider("Dor Muscular", 1, 5, 3, 
                           help="1 = Dor intensa, 5 = Sem dor")
            estresse = st.slider("Nível de Estresse", 1, 5, 3, 
                                help="1 = Muito estressado, 5 = Relaxado")

        with col2:
            vigor = st.slider("Disposição/Vigor", 1, 5, 3, 
                             help="1 = Sem energia, 5 = Cheio de energia")
            tensao = st.slider("Tensão/Ansiedade", 1, 5, 3, 
                              help="1 = Muito tenso, 5 = Tranquilo")
            apetite = st.slider("Apetite", 1, 5, 3, 
                               help="1 = Sem apetite, 5 = Apetite normal")
            prontidao = st.slider("Prontidão para Treinar", 1, 5, 3, 
                                 help="1 = Não me sinto pronto, 5 = Totalmente pronto")

        periodo = st.selectbox("Período do gráfico", [7, 14, 30], index=0)
        submit = st.form_submit_button("Enviar Avaliação")

    if submit:
        try:
            # Calcular score e ajuste
            score = calculate_score(sono, fadiga, dor, estresse, vigor, tensao, apetite, prontidao)
            ajuste = ajuste_carga(score)
            data = datetime.now().strftime('%Y-%m-%d')

            # Salvar no banco de dados
            save_assessment(usuario_id, data, sono, fadiga, dor, estresse, vigor, tensao, apetite, prontidao)

            # Exibir resultados
            st.success(f"Seu score de prontidão: {score}/40")

            # Criar colunas para exibir o resultado e recomendação
            col1, col2 = st.columns(2)

            with col1:
                st.metric("Score de Prontidão", f"{score}/40", delta=None)

                # Classificação do score
                if score >= 32:
                    st.success("Status: ÓTIMO - Pronto para treino completo")
                elif score >= 24:
                    st.info("Status: BOM - Pronto para treino moderado")
                elif score >= 16:
                    st.warning("Status: REGULAR - Treino com cautela")
                else:
                    st.error("Status: BAIXO - Considere descanso ou treino leve")

            with col2:
                st.metric("Ajuste na Carga de Treino", f"{ajuste:.1f}%", delta=None)
                st.info(f"Recomendação: Ajuste sua carga de treino para {ajuste:.1f}% do seu volume normal")

            # Buscar histórico e exibir gráfico
            try:
                historico = get_historico(usuario_id, dias=periodo)

                if not historico.empty:
                    # Adicionar o registro atual ao histórico para visualização imediata
                    novo_registro = pd.DataFrame({
                        'Data': [datetime.now()],
                        'Score': [score],
                        'Ajuste': [ajuste]
                    })

                    historico_completo = pd.concat([historico, novo_registro]).reset_index(drop=True)

                    # Criar gráfico com Plotly
                    fig = px.line(historico_completo, x='Data', y=['Score', 'Ajuste'], 
                                 title=f'Evolução nos últimos {periodo} dias',
                                 labels={'value': 'Valor', 'variable': 'Métrica'},
                                 color_discrete_map={'Score': 'blue', 'Ajuste': 'green'})

                    fig.update_layout(
                        xaxis_title='Data',
                        yaxis_title='Valor',
                        legend_title='Métrica',
                        hovermode='x unified'
                    )

                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Este é seu primeiro registro. O gráfico será exibido após múltiplas avaliações.")
            except Exception as e:
                st.error(f"Erro ao buscar histórico: {e}")
        except Exception as e:
            st.error(f"Erro ao processar avaliação: {e}")

# Página de histórico
elif page == "Histórico":
    st.title("Histórico de Avaliações")

    # Em um ambiente real, o ID do usuário viria do sistema de login
    usuario_id = st.sidebar.number_input("ID do Usuário (simulação)", min_value=1, value=1)
    periodo = st.slider("Período (dias)", min_value=7, max_value=90, value=30)

    try:
        historico = get_historico(usuario_id, dias=periodo)

        if not historico.empty:
            # Exibir tabela de histórico
            st.subheader("Registros de Avaliação")
            st.dataframe(historico)

            # Criar gráfico com Plotly
            fig = px.line(historico, x='Data', y=['Score', 'Ajuste'], 
                         title=f'Evolução nos últimos {periodo} dias',
                         labels={'value': 'Valor', 'variable': 'Métrica'},
                         color_discrete_map={'Score': 'blue', 'Ajuste': 'green'})

            fig.update_layout(
                xaxis_title='Data',
                yaxis_title='Valor',
                legend_title='Métrica',
                hovermode='x unified'
            )

            st.plotly_chart(fig, use_container_width=True)

            # Opção para download dos dados
            csv = historico.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"historico_usuario_{usuario_id}.csv",
                mime="text/csv"
            )
        else:
            st.info("Não há registros para este usuário no período selecionado.")
    except Exception as e:
        st.error(f"Erro ao buscar histórico: {e}")

# Página de admin
elif page == "Painel Admin":
    st.title("Painel de Administração")

    # Em um ambiente real, verificaríamos se o usuário tem permissões de admin
    st.warning("Esta é uma simulação do painel de administração. Em um ambiente real, seria protegido por login.")

    try:
        # Conectar ao banco de dados
        conn = sqlite3.connect('prontidao.db')

        # Buscar todos os registros
        query = "SELECT * FROM assessments ORDER BY data DESC"
        df = pd.read_sql_query(query, conn)

        if not df.empty:
            # Calcular score para cada registro
            df['Score'] = df[['sono', 'fadiga', 'dor', 'estresse', 'vigor', 'tensao', 'apetite', 'prontidao']].sum(axis=1)
            df['Ajuste'] = df['Score'].apply(ajuste_carga)

            # Exibir estatísticas
            st.subheader("Estatísticas Gerais")
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total de Avaliações", len(df))

            with col2:
                st.metric("Score Médio", f"{df['Score'].mean():.1f}")

            with col3:
                st.metric("Usuários Únicos", df['usuario_id'].nunique())

            # Filtros
            st.subheader("Filtros")
            col1, col2 = st.columns(2)

            with col1:
                usuario_filtro = st.multiselect("Filtrar por Usuário", options=sorted(df['usuario_id'].unique()))

            with col2:
                data_inicio = st.date_input("Data Inicial", value=pd.to_datetime(df['data']).min())
                data_fim = st.date_input("Data Final", value=pd.to_datetime(df['data']).max())

            # Aplicar filtros
            df_filtrado = df.copy()

            if usuario_filtro:
                df_filtrado = df_filtrado[df_filtrado['usuario_id'].isin(usuario_filtro)]

            df_filtrado = df_filtrado[
                (pd.to_datetime(df_filtrado['data']) >= pd.to_datetime(data_inicio)) & 
                (pd.to_datetime(df_filtrado['data']) <= pd.to_datetime(data_fim))
            ]

            # Exibir dados filtrados
            st.subheader("Registros de Avaliação")
            st.dataframe(df_filtrado)

            # Gráfico de evolução por usuário
            if usuario_filtro and len(usuario_filtro) > 0:
                st.subheader("Evolução por Usuário")

                fig = px.line(df_filtrado, x='data', y='Score', color='usuario_id',
                             title='Evolução do Score por Usuário',
                             labels={'data': 'Data', 'Score': 'Score', 'usuario_id': 'ID do Usuário'})

                st.plotly_chart(fig, use_container_width=True)

            # Opção para download dos dados
            csv = df_filtrado.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="relatorio_admin.csv",
                mime="text/csv"
            )
        else:
            st.info("Não há registros no banco de dados.")

        conn.close()
    except Exception as e:
        st.error(f"Erro ao acessar o banco de dados: {e}")
