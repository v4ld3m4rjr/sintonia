
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Sintonia - Teste",
    page_icon="🧠",
    layout="wide"
)

# Inicializar estado da sessão
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = None

# Interface de login simples
if not st.session_state.authenticated:
    st.title("Login")

    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        # Verificação simples
        if username == "demo" and password == "demo123":
            st.session_state.authenticated = True
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Credenciais inválidas")
else:
    # Interface principal
    st.title(f"Bem-vindo, {st.session_state.username}!")

    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()

    st.write("Esta é uma versão simplificada para teste.")
