
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
import os
from datetime import datetime
import supabase
from dotenv import load_dotenv

# Importar os módulos de avaliação
from mental_assessment import mental_assessment_page
# Assumindo que estes módulos existem no seu projeto
# from readiness_assessment import readiness_assessment_page
# from trimp_evaluation import trimp_evaluation_page

# Carregar variáveis de ambiente
load_dotenv()

# Configuração do Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Inicializar cliente Supabase
supabase_client = supabase.create_client(SUPABASE_URL, SUPABASE_KEY)

# Configuração da página
st.set_page_config(
    page_title="Sintonia - Análise de Treinamento",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para verificar login
def check_login():
    if 'user_id' not in st.session_state:
        st.session_state.user_id = "user123"  # Temporário para teste - substitua pela sua lógica de autenticação
        # Na versão real, você deve verificar se o usuário está autenticado
        # e redirecionar para a página de login se não estiver

# Página inicial
def home_page():
    st.title("Bem-vindo ao Sintonia")
    st.subheader("Sua plataforma completa de análise de treinamento")

    st.write("""
    O Sintonia oferece ferramentas avançadas para monitorar e analisar seu treinamento:

    - **Avaliação de Prontidão**: Avalie sua disposição para treinar
    - **Avaliação TRIMP**: Analise a carga de treinamento
    - **Avaliação Mental**: Monitore ansiedade, estresse e fadiga mental

    Selecione uma opção no menu lateral para começar.
    """)

    # Mostrar estatísticas ou gráficos recentes
    st.subheader("Resumo das suas avaliações recentes")

    # Exemplo de gráfico (substitua por dados reais)
    data = {
        'Categoria': ['Prontidão', 'TRIMP', 'Ansiedade', 'Estresse', 'Fadiga Mental'],
        'Valor': [7, 120, 5, 15, 8]
    }
    df = pd.DataFrame(data)

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(df['Categoria'], df['Valor'], color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])
    ax.set_title('Últimas Avaliações')
    ax.set_ylabel('Pontuação')
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    st.pyplot(fig)

# Página de configurações
def settings_page():
    st.title("Configurações")

    st.subheader("Perfil do Usuário")
    col1, col2 = st.columns(2)

    with col1:
        st.text_input("Nome", value="Usuário Exemplo")
        st.text_input("Email", value="usuario@exemplo.com")

    with col2:
        st.number_input("Idade", min_value=10, max_value=100, value=30)
        st.selectbox("Sexo", options=["Masculino", "Feminino", "Outro"])

    st.subheader("Preferências")
    st.checkbox("Receber notificações por email")
    st.checkbox("Modo escuro", value=True)

    if st.button("Salvar Configurações"):
        st.success("Configurações salvas com sucesso!")

# Função principal
def main():
    # Verificar login
    check_login()

    # Sidebar
    st.sidebar.title("Sintonia")
    st.sidebar.image("https://via.placeholder.com/150", width=150)

    # Menu de navegação
    menu = ["Início", "Avaliação de Prontidão", "Avaliação TRIMP", "Avaliação Mental", "Configurações"]
    choice = st.sidebar.selectbox("Menu", menu)

    # Exibir página selecionada
    if choice == "Início":
        home_page()
    elif choice == "Avaliação de Prontidão":
        # Substitua pelo seu código real
        st.title("Avaliação de Prontidão")
        st.write("Esta funcionalidade será implementada em breve.")
        # readiness_assessment_page()  # Descomente quando o módulo estiver disponível
    elif choice == "Avaliação TRIMP":
        # Substitua pelo seu código real
        st.title("Avaliação TRIMP")
        st.write("Esta funcionalidade será implementada em breve.")
        # trimp_evaluation_page()  # Descomente quando o módulo estiver disponível
    elif choice == "Avaliação Mental":
        # Nova funcionalidade de avaliação mental
        mental_assessment_page()
    elif choice == "Configurações":
        settings_page()

    # Footer
    st.sidebar.markdown("---")
    st.sidebar.info("© 2023 Sintonia - Todos os direitos reservados")

if __name__ == "__main__":
    main()
