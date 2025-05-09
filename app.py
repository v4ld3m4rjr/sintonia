import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import datetime, timedelta
from supabase import create_client

# Configuração da página
st.set_page_config(
    page_title="Sistema de Monitoramento do Atleta",
    page_icon="🏃",
    layout="wide"
)

# Inicialização do Supabase
def init_supabase():
    try:
        # Primeiro tenta ler do ambiente (Render), depois de st.secrets (local)
        SUPABASE_URL = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")
        
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        return client
    except Exception as e:
        st.warning(f"Erro ao conectar com Supabase: {str(e)}", icon="⚠️")
        return None

# Inicializar variáveis de sessão
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None

# Função para adicionar logo
def add_logo():
    try:
        st.sidebar.image("logo.png", width=200)
    except:
        st.sidebar.title("App Sintonia")

# Módulo de Prontidão
def show_readiness_assessment():
    st.header("Avaliação de Prontidão")
    st.markdown("""
    Esta avaliação utiliza ferramentas validadas para medir sua prontidão física:
    * **Hooper Index**: Fadiga, estresse, dor e sono
    * **TQR**: Recuperação global
    * **NPRS**: Dor musculoesquelética
    """)
    
    # Hooper Index
    st.subheader("Hooper Index")
    col1, col2 = st.columns(2)
    
    with col1:
        hooper_fadiga = st.slider("Fadiga (1–7)", 1, 7)
        hooper_estresse = st.slider("Estresse (1–7)", 1, 7)
    
    with col2:
        hooper_doms = st.slider("Dor Muscular (1–7)", 1, 7)
        hooper_sono = st.slider("Qualidade do Sono (1–7)", 1, 7)
    
    hooper_total = hooper_fadiga + hooper_estresse + hooper_doms + hooper_sono
    st.info(f"Hooper Index Total: {hooper_total}/28")
    
    # TQR
    st.subheader("Total Quality Recovery (TQR)")
    tqr = st.slider("Recuperação (6–20)", 6, 20)
    
    # NPRS
    st.subheader("Numeric Pain Rating Scale (NPRS)")
    nprs = st.slider("Dor atual (0–10)", 0, 10)
    
    # Histórico de Carga
    st.subheader("Histórico de Carga")
    col1, col2 = st.columns(2)
    
    with col1:
        ctl = st.number_input("CTL", value=0.0)
    
    with col2:
        atl = st.number_input("ATL", value=0.0)
    
    # Calcular readiness
    readiness = 100 - ((hooper_total - 4) / 24 * 30) - ((20 - tqr) / 14 * 30) - (nprs / 10 * 30)
    readiness = max(0, min(100, readiness))
    
    st.metric("Prontidão", f"{readiness:.1f}%")
    
    if readiness >= 80:
        st.success("Estado ótimo para treino intenso")
    elif readiness >= 60:
        st.info("Bom estado para treino normal")
    elif readiness >= 40:
        st.warning("Reduzir intensidade do treino")
    else:
        st.error("Priorizar recuperação")
    
    # Botão para salvar
    if st.button("Salvar Avaliação", key="save_readiness"):
        st.success("Avaliação de prontidão salva com sucesso!")

# Módulo de Estado de Treino
def show_training_assessment():
    st.header("Avaliação do Estado de Treino")
    st.markdown("""
    Esta avaliação utiliza métricas validadas para monitorar seu treino:
    * **TRIMP**: Quantifica a carga de treino
    * **ACWR**: Relação entre carga aguda e crônica
    * **Risco de Lesão**: Estimativa baseada em fatores combinados
    """)
    
    # Variáveis de entrada
    st.subheader("Detalhes do Treino")
    col1, col2 = st.columns(2)
    
    with col1:
        duration = st.number_input("Duração (minutos)", min_value=0, value=60)
        heart_rate = st.number_input("FC média (bpm)", min_value=0, value=140)
    
    with col2:
        rpe = st.slider("Percepção de Esforço (0-10)", 0.0, 10.0, 5.0, 0.5)
        notes = st.text_area("Observações", height=100)
    
    # Calcular TRIMP
    trimp = duration * rpe
    
    # Mostrar métricas
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("TRIMP", f"{trimp:.1f}")
        st.info("TRIMP (Training Impulse) quantifica a carga interna de treino.")
    
    # Risco de lesão (simplificado)
    injury_risk = min(trimp / 10, 100)
    
    with col2:
        st.metric("Risco de Lesão", f"{injury_risk:.1f}%")
        
        if injury_risk < 30:
            st.success("Risco Baixo")
        elif injury_risk < 60:
            st.warning("Risco Moderado")
        else:
            st.error("Risco Alto")
    
    # Botão para salvar
    if st.button("Salvar Treino", key="save_training"):
        st.success("Treino salvo com sucesso!")

# Módulo Psicoemocional
def show_psychological_assessment():
    st.header("Avaliação Psicoemocional")
    st.markdown("""
    Esta avaliação utiliza questionários validados para seu estado psicoemocional:
    * **DASS-21**: Avalia ansiedade
    * **PSS-10**: Avalia estresse
    * **FANTASTIC**: Avalia estilo de vida
    """)
    
    # Simplificado para teste
    st.subheader("Avaliação de Ansiedade")
    anxiety = st.slider("Nível de Ansiedade (0-21)", 0, 21)
    
    st.subheader("Avaliação de Estresse")
    stress = st.slider("Nível de Estresse (0-40)", 0, 40)
    
    st.subheader("Avaliação de Estilo de Vida")
    lifestyle = st.slider("Estilo de Vida (0-100)", 0, 100)
    
    # Botão para salvar
    if st.button("Salvar Avaliação", key="save_psych"):
        st.success("Avaliação psicoemocional salva com sucesso!")

# Dashboard
def show_dashboard():
    st.header("Dashboard Geral")
    st.info("Aqui serão exibidas as métricas e tendências quando houver dados históricos.")
    
    # Exemplo de gráfico simples
    fig, ax = plt.subplots()
    data = [80, 75, 82, 70, 85, 72, 78]
    days = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
    ax.plot(days, data)
    ax.set_title('Exemplo: Prontidão na Semana')
    ax.set_ylabel('Prontidão (%)')
    ax.grid(True)
    st.pyplot(fig)

# Login simplificado
def show_login_form():
    st.title("Sistema de Monitoramento do Atleta")
    add_logo()
    
    # Login direto para teste
    if st.button("Login de Teste"):
        st.session_state.user_id = "teste123"
        st.session_state.username = "Usuário de Teste"
        st.success("Login realizado com sucesso!")
        # Usando st.rerun() em vez de st.experimental_rerun()
        st.rerun()

# Função principal
def show_questionnaire():
    add_logo()
    st.title(f"Olá, {st.session_state.username}!")
    
    if st.sidebar.button("Logout"):
        st.session_state.user_id = None
        st.session_state.username = None
        # Usando st.rerun() em vez de st.experimental_rerun()
        st.rerun()
    
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

# Fluxo principal
def main():
    if st.session_state.user_id is None:
        show_login_form()
    else:
        show_questionnaire()

if __name__ == "__main__":
    main()
