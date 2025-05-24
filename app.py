"""
Sistema de Monitoramento do Atleta - Aplicativo Principal
---------------------------------------------------------
Este é o arquivo principal do aplicativo Streamlit para monitoramento de atletas.
Ele gerencia a autenticação de usuários e exibe o dashboard principal quando o usuário está logado.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import os
import sys

# Adiciona os diretórios ao path para importação dos módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importa os módulos de utilidades
from utils.auth import check_authentication, login_user, create_account, reset_password
from utils.database import init_connection
from utils.helpers import format_date, get_trend_icon

# Importa os componentes reutilizáveis
from components.cards import metric_card
from components.charts import create_trend_chart
from components.navigation import create_sidebar

# Configuração da página
st.set_page_config(
    page_title="Sistema de Monitoramento do Atleta",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inicialização da conexão com o banco
conn = init_connection()

# Função para exibir o dashboard principal
def show_dashboard():
    """Exibe o dashboard principal com métricas e gráficos."""
    st.title("Dashboard")
    st.subheader(f"Bem-vindo, {st.session_state.user_name}")
    
    # Métricas principais em cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Exemplo de card de prontidão
        # Na implementação real, esses valores viriam do banco de dados
        metric_card(
            title="Prontidão", 
            value="85", 
            delta="5%", 
            is_positive=True,
            description="Seu nível de prontidão está ótimo hoje!"
        )
    
    with col2:
        # Exemplo de card de TRIMP semanal
        metric_card(
            title="TRIMP Semanal", 
            value="450", 
            delta="-10%", 
            is_positive=False,
            description="Carga de treino menor que a semana anterior"
        )
    
    with col3:
        # Exemplo de card de estresse
        metric_card(
            title="Estresse", 
            value="Baixo", 
            delta="", 
            neutral=True,
            description="Seus níveis de estresse estão controlados"
        )
    
    # Gráfico de tendência semanal
    st.subheader("Tendência Semanal")
    
    # Dados de exemplo para o gráfico
    # Na implementação real, esses dados viriam do banco de dados
    dates = [datetime.now() - timedelta(days=i) for i in range(7, 0, -1)]
    dates_str = [d.strftime("%d/%m") for d in dates]
    
    readiness_data = [78, 82, 75, 80, 85, 83, 85]
    trimp_data = [420, 380, 450, 400, 420, 380, 450]
    stress_data = [25, 30, 35, 28, 22, 20, 18]
    
    # Criação do gráfico de tendência
    fig = create_trend_chart(
        dates=dates_str,
        readiness=readiness_data,
        trimp=trimp_data,
        stress=stress_data
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Botões de ação rápida
    st.subheader("Ações Rápidas")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("📝 Nova Avaliação de Prontidão", use_container_width=True):
            st.switch_page("pages/1_Prontidao.py")
    
    with col2:
        if st.button("🏋️ Registrar Treino", use_container_width=True):
            st.switch_page("pages/2_Treino.py")
    
    # Metas atuais (gamificação)
    st.subheader("Suas Metas Atuais")
    
    # Dados de exemplo para as metas
    # Na implementação real, esses dados viriam do banco de dados
    goals_data = {
        "Meta": ["Prontidão média", "TRIMP semanal", "Horas de sono", "Nível de estresse"],
        "Atual": [83, 450, 7.2, 22],
        "Objetivo": [85, 500, 8.0, 20],
        "Progresso": [83/85*100, 450/500*100, 7.2/8.0*100, (30-22)/(30-20)*100]
    }
    
    goals_df = pd.DataFrame(goals_data)
    
    # Exibição das metas com barras de progresso
    for i, row in goals_df.iterrows():
        col1, col2, col3 = st.columns([2, 6, 2])
        
        with col1:
            st.write(f"**{row['Meta']}**")
        
        with col2:
            progress = min(100, max(0, row['Progresso']))
            st.progress(progress / 100)
        
        with col3:
            st.write(f"{row['Atual']} / {row['Objetivo']}")

# Função para exibir o formulário de login
def show_login():
    """Exibe o formulário de login e opções de registro/recuperação de senha."""
    st.title("Sistema de Monitoramento do Atleta")
    st.markdown("### Entre com sua conta para acessar o sistema")
    
    # Formulário de login
    with st.form("login_form"):
        email = st.text_input("Email")
        password = st.text_input("Senha", type="password")
        submit = st.form_submit_button("Entrar", use_container_width=True)
        
        if submit:
            if login_user(email, password):
                st.rerun()
            else:
                st.error("Email ou senha incorretos. Tente novamente.")
    
    # Opções adicionais
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Criar nova conta", use_container_width=True):
            st.session_state.show_create_account = True
            st.session_state.show_reset_password = False
    
    with col2:
        if st.button("Esqueci minha senha", use_container_width=True):
            st.session_state.show_reset_password = True
            st.session_state.show_create_account = False

# Função para exibir o formulário de criação de conta
def show_create_account():
    """Exibe o formulário para criação de nova conta."""
    st.title("Criar Nova Conta")
    
    with st.form("create_account_form"):
        name = st.text_input("Nome completo")
        email = st.text_input("Email")
        password = st.text_input("Senha", type="password", 
                               help="A senha deve ter pelo menos 8 caracteres, incluindo letras maiúsculas, minúsculas e números")
        password_confirm = st.text_input("Confirme a senha", type="password")
        
        submit = st.form_submit_button("Criar Conta", use_container_width=True)
        
        if submit:
            if password != password_confirm:
                st.error("As senhas não coincidem. Tente novamente.")
            elif len(password) < 8:
                st.error("A senha deve ter pelo menos 8 caracteres.")
            else:
                # Aqui seria chamada a função para criar a conta
                if create_account(name, email, password):
                    st.success("Conta criada com sucesso! Faça login para continuar.")
                    st.session_state.show_create_account = False
                else:
                    st.error("Não foi possível criar a conta. O email já pode estar em uso.")
    
    if st.button("Voltar para o login", use_container_width=True):
        st.session_state.show_create_account = False
        st.rerun()

# Função para exibir o formulário de recuperação de senha
def show_reset_password():
    """Exibe o formulário para recuperação de senha."""
    st.title("Recuperar Senha")
    
    with st.form("reset_password_form"):
        email = st.text_input("Email")
        submit = st.form_submit_button("Enviar link de recuperação", use_container_width=True)
        
        if submit:
            # Aqui seria chamada a função para enviar o email de recuperação
            if reset_password(email):
                st.success("Um link de recuperação foi enviado para o seu email.")
                st.session_state.show_reset_password = False
            else:
                st.error("Email não encontrado. Verifique se digitou corretamente.")
    
    if st.button("Voltar para o login", use_container_width=True):
        st.session_state.show_reset_password = False
        st.rerun()

# Função principal
def main():
    """Função principal que controla o fluxo do aplicativo."""
    # Inicializa variáveis de estado se não existirem
    if 'show_create_account' not in st.session_state:
        st.session_state.show_create_account = False
    
    if 'show_reset_password' not in st.session_state:
        st.session_state.show_reset_password = False
    
    # Verifica se o usuário está autenticado
    if check_authentication():
        # Cria a barra lateral de navegação
        create_sidebar()
        # Exibe o dashboard principal
        show_dashboard()
    else:
        # Exibe os formulários de acordo com o estado atual
        if st.session_state.show_create_account:
            show_create_account()
        elif st.session_state.show_reset_password:
            show_reset_password()
        else:
            show_login()

# Executa a função principal quando o script é executado diretamente
if __name__ == "__main__":
    main()
