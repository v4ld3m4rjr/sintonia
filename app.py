import os
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import sys

# Importar funções utilitárias
from utils import init_supabase, get_user_assessments, get_psychological_assessments, get_user_training_assessments

# Importar módulos
from readiness_assessment import show_readiness_assessment
from training_assessment import show_training_assessment
from psychological_assessment import show_psychological_assessment

# Configuração da página
st.set_page_config(
    page_title="Sistema de Monitoramento do Atleta",
    page_icon="🏃",
    layout="wide"
)

# Inicializar variáveis de sessão
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'show_admin' not in st.session_state:
    st.session_state.show_admin = False
if 'readiness_history' not in st.session_state:
    st.session_state.readiness_history = []
if 'training_history' not in st.session_state:
    st.session_state.training_history = []
if 'psychological_history' not in st.session_state:
    st.session_state.psychological_history = []

# Função para adicionar logo
def add_logo():
    st.sidebar.image("logo.png", width=200)

# Função de logout
def logout():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.experimental_rerun()

# Dashboard
def show_dashboard():
    st.header("Dashboard Geral")
    if not st.session_state.get('user_id'):
        st.warning("Faça login para ver o dashboard")
        return
        
    # Período de análise
    period = st.selectbox(
        "Período de Análise",
        [7, 14, 30],
        format_func=lambda x: f"Últimos {x} dias"
    )
    
    # Buscar dados
    readiness_data = get_user_assessments(st.session_state.user_id, days=period)
    training_data = get_user_training_assessments(st.session_state.user_id, days=period)
    psych_data = get_psychological_assessments(st.session_state.user_id, days=period)
    
    # Métricas principais
    col1, col2, col3 = st.columns(3)
    with col1:
        if readiness_data:
            df_readiness = pd.DataFrame(readiness_data)
            avg_readiness = df_readiness['readiness'].mean()
            st.metric("Prontidão Média", f"{avg_readiness:.1f}%")
        else:
            st.metric("Prontidão Média", "N/A")
            
    with col2:
        if training_data:
            df_training = pd.DataFrame(training_data)
            avg_load = df_training['training_load'].mean()
            st.metric("Carga Média", f"{avg_load:.1f}")
        else:
            st.metric("Carga Média", "N/A")
            
    with col3:
        if psych_data:
            df_psych = pd.DataFrame(psych_data)
            avg_stress = df_psych['stress_score'].mean()
            st.metric("Estresse Médio", f"{avg_stress:.1f}")
        else:
            st.metric("Estresse Médio", "N/A")
    
    # Gráficos de tendência
    st.subheader("Tendências")
    if readiness_data or training_data or psych_data:
        fig, ax = plt.subplots(figsize=(12, 6))
        
        if readiness_data:
            df_readiness['created_at'] = pd.to_datetime(df_readiness['created_at'])
            ax.plot(df_readiness['created_at'], 
                   df_readiness['readiness'],
                   label='Prontidão', marker='o')
                   
        if training_data:
            df_training['created_at'] = pd.to_datetime(df_training['created_at'])
            ax.plot(df_training['created_at'],
                   df_training['training_load'],
                   label='Carga', marker='s')
                   
        if psych_data:
            df_psych['created_at'] = pd.to_datetime(df_psych['created_at'])
            ax.plot(df_psych['created_at'],
                   df_psych['stress_score'],
                   label='Estresse', marker='^')
        
        ax.set_title('Tendências Integradas')
        ax.set_xlabel('Data')
        ax.set_ylabel('Valores')
        ax.legend()
        ax.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.pyplot(fig)
        
        # Correlações
        if readiness_data and training_data and psych_data:
            st.subheader("Matriz de Correlações")
            
            # Preparar dados para correlação
            df_corr = pd.DataFrame({
                'Prontidão': df_readiness['readiness'],
                'Carga': df_training['training_load'],
                'Estresse': df_psych['stress_score']
            })
            
            # Calcular correlações
            corr_matrix = df_corr.corr()
            
            # Plotar heatmap
            fig, ax = plt.subplots(figsize=(8, 6))
            sns.heatmap(corr_matrix,
                       annot=True,
                       cmap='RdYlBu_r',
                       vmin=-1,
                       vmax=1,
                       center=0)
            plt.title("Correlações entre Métricas")
            st.pyplot(fig)
    else:
        st.info("Nenhum dado disponível para o período selecionado.")

# Sistema de login/registro
def show_login_form():
    st.title("Bem-vindo ao Sistema de Monitoramento do Atleta")
    add_logo()
    
    tab1, tab2 = st.tabs(["Login", "Registro"])
    
    with tab1:
        email = st.text_input("Email", key="login_email")
        password = st.text_input("Senha", type="password", key="login_password")
        
        if st.button("Login"):
            if not email or not password:
                st.error("Preencha todos os campos")
                return
                
            supabase = init_supabase()
            if not supabase:
                return
                
            response = supabase.auth.sign_in_with_password({"email": email, "password": password})
            
            if response.user:
                st.session_state.user_id = response.user.id
                
                # Buscar dados do usuário
                user_response = supabase.table("users").select("*").eq("id", response.user.id).execute()
                
                if user_response.data:
                    st.session_state.username = user_response.data[0].get('name', email)
                    st.session_state.is_admin = user_response.data[0].get('is_admin', False)
                else:
                    st.session_state.username = email
                
                st.success("Login realizado com sucesso!")
                st.experimental_rerun()
            else:
                st.error("Credenciais inválidas")
    
    with tab2:
        name = st.text_input("Nome", key="reg_name")
        email = st.text_input("Email", key="reg_email")
        password = st.text_input("Senha", type="password", key="reg_password")
        confirm_password = st.text_input("Confirmar Senha", type="password", key="reg_confirm")
        gender = st.selectbox("Sexo", ["Masculino", "Feminino", "Outro"])
        age = st.number_input("Idade", min_value=10, max_value=100, value=30)
        
        if st.button("Registrar"):
            if not name or not email or not password or not confirm_password:
                st.error("Preencha todos os campos")
                return
                
            if password != confirm_password:
                st.error("As senhas não conferem")
                return
                
            supabase = init_supabase()
            if not supabase:
                return
                
            try:
                # Registrar usuário no Auth
                auth_response = supabase.auth.sign_up({
                    "email": email,
                    "password": password
                })
                
                if auth_response.user:
                    # Salvar dados adicionais na tabela Users
                    supabase.table("users").insert({
                        "id": auth_response.user.id,
                        "name": name,
                        "email": email,
                        "gender": gender,
                        "age": age,
                        "is_admin": False
                    }).execute()
                    
                    st.success("Registro realizado com sucesso! Faça login.")
                else:
                    st.error("Erro ao registrar usuário")
            except Exception as e:
                st.error(f"Erro ao registrar: {str(e)}")

# Função principal para exibir o questionário
def show_questionnaire():
    add_logo()
    st.title(f"Olá, {st.session_state.username}!")
    
    if st.session_state.is_admin:
        if st.sidebar.button("Painel de Administração"):
            st.session_state.show_admin = True
            st.experimental_rerun()
            
    if st.sidebar.button("Logout"):
        logout()
    
    # Abas principais
    tab1, tab2, tab3, tab4 = st.tabs([
        "Avaliação de Prontidão",
        "Estado de Treino",
        "Avaliação Psicoemocional",
        "Dashboard"
    ])
    
    with tab1:
        show_readiness_assessment()
        
    with tab2:
        show_training_assessment()
        
    with tab3:
        show_psychological_assessment()
        
    with tab4:
        show_dashboard()

# Painel de administração
def show_admin_panel():
    add_logo()
    st.title("Painel de Administração")
    
    if st.sidebar.button("Voltar"):
        st.session_state.show_admin = False
        st.experimental_rerun()
    
    supabase = init_supabase()
    if not supabase:
        return
    
    # Listagem de usuários
    st.header("Usuários")
    users_response = supabase.table("users").select("*").execute()
    
    if users_response.data:
        df_users = pd.DataFrame(users_response.data)
        st.dataframe(df_users)
    else:
        st.info("Nenhum usuário encontrado")
    
    # Estatísticas gerais
    st.header("Estatísticas")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        readiness_count = supabase.table("readiness_assessments").select("count", count="exact").execute()
        st.metric("Total de Avaliações de Prontidão", readiness_count.count)
    
    with col2:
        training_count = supabase.table("training_assessments").select("count", count="exact").execute()
        st.metric("Total de Avaliações de Treino", training_count.count)
    
    with col3:
        psych_count = supabase.table("psychological_assessments").select("count", count="exact").execute()
        st.metric("Total de Avaliações Psicológicas", psych_count.count)

# Fluxo principal do aplicativo
def main():
    if st.session_state.user_id is None:
        show_login_form()
    elif st.session_state.show_admin and st.session_state.is_admin:
        show_admin_panel()
    else:
        show_questionnaire()

if __name__ == "__main__":
    main()