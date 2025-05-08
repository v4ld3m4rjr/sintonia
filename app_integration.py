
import streamlit as st
from mental_assessment import mental_assessment_module

# Configuração da página
st.set_page_config(
    page_title="Sintonia",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para autenticação
def authenticate():
    """Função de autenticação de usuários."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_id = None

    if not st.session_state.authenticated:
        with st.form("login_form"):
            st.subheader("Login")
            username = st.text_input("Usuário")
            password = st.text_input("Senha", type="password")
            submit = st.form_submit_button("Entrar")

            if submit:
                # Aqui você implementaria a verificação real de credenciais
                # Exemplo simplificado:
                if username == "demo" and password == "demo123":
                    st.session_state.authenticated = True
                    st.session_state.user_id = "demo_user_id"
                    st.session_state.username = username
                    st.experimental_rerun()
                else:
                    st.error("Credenciais inválidas")

        # Opção para criar conta
        with st.expander("Criar nova conta"):
            with st.form("signup_form"):
                st.subheader("Cadastro")
                new_username = st.text_input("Novo Usuário")
                new_password = st.text_input("Nova Senha", type="password")
                confirm_password = st.text_input("Confirmar Senha", type="password")
                submit = st.form_submit_button("Cadastrar")

                if submit:
                    # Implementar lógica de cadastro
                    if new_password != confirm_password:
                        st.error("As senhas não coincidem")
                    else:
                        # Aqui você implementaria o cadastro real
                        st.success("Conta criada com sucesso! Faça login.")

        return False
    return True

# Função principal do aplicativo
def main():
    # Verificar autenticação
    if not authenticate():
        return

    # Sidebar para navegação
    with st.sidebar:
        st.title("Sintonia")
        st.write(f"Olá, {st.session_state.username}!")

        # Menu de navegação
        page = st.radio(
            "Navegação",
            ["Início", "Avaliação Mental", "Configurações", "Sair"]
        )

        # Botão de logout
        if st.button("Logout"):
            st.session_state.authenticated = False
            st.session_state.user_id = None
            st.experimental_rerun()

    # Conteúdo principal
    if page == "Início":
        st.title("Bem-vindo ao Sintonia")
        st.write("Selecione uma opção no menu lateral para começar.")

        # Cards informativos
        col1, col2 = st.columns(2)

        with col1:
            st.info("**Avaliação Mental**  
Registre sua prontidão para treino e analise seus resultados.")

        with col2:
            st.info("**Configurações**  
Personalize sua experiência no aplicativo.")

    elif page == "Avaliação Mental":
        # Integração com o módulo de avaliação mental
        mental_assessment_module()

    elif page == "Configurações":
        st.title("Configurações")

        # Preferências do usuário
        st.subheader("Preferências")

        # Tema
        theme = st.selectbox(
            "Tema",
            ["Claro", "Escuro", "Sistema"],
            index=2
        )

        # Notificações
        notifications = st.checkbox("Ativar notificações", value=True)

        # Botão para salvar configurações
        if st.button("Salvar Configurações"):
            st.success("Configurações salvas com sucesso!")

    elif page == "Sair":
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.experimental_rerun()

# Executar o aplicativo
if __name__ == "__main__":
    main()
