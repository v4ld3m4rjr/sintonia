import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from utils import ajuste_carga

def admin_dashboard():
    # Painel de administração para visualizar todos os dados de avaliação
    st.title("Painel de Administração")

    # Em um ambiente real, verificaríamos se o usuário tem permissões de admin
    st.warning("Esta é uma simulação do painel de administração. Em um ambiente real, seria protegido por login.")

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

if __name__ == "__main__":
    admin_dashboard()
