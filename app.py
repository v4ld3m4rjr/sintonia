
import streamlit as st
from mental_assessment import mental_assessment_module
import json
import os

# Configuração da página
st.set_page_config(
    page_title="Sintonia",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Função para carregar usuários do arquivo (simulando banco de dados)
def load_users():
    if os.path.exists("users.json"):
        with open("users.json", "r") as file:
            return json.load(file)
    # Usuário demo padrão
    return {"demo": {"password": "demo123", "email": "demo@example.com", "age": 30, "gender": "Masculino"}}

# Função para salvar usuários no arquivo
def save_users(users):
    with open("users.json", "w") as file:
        json.dump(users, file)

# Função para autenticação
def authenticate():
    """Função de autenticação de usuários."""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.user_id = None

    # Carregar usuários
    users = load_users()

    if not st.session_state.authenticated:
        with st.form("login_form"):
            st.subheader("Login")
            username = st.text_input("Usuário")
            password = st.text_input("Senha", type="password")
            submit = st.form_submit_button("Entrar")

            if submit:
                # Verificar credenciais
                if username in users and users[username]["password"] == password:
                    st.session_state.authenticated = True
                    st.session_state.user_id = username
                    st.session_state.username = username
                    st.experimental_rerun()
                else:
                    st.error("Credenciais inválidas")

        # Opção para criar conta
        with st.expander("Criar nova conta"):
            with st.form("signup_form"):
                st.subheader("Cadastro")
                new_username = st.text_input("Novo Usuário")
                new_email = st.text_input("Email")
                new_age = st.number_input("Idade", min_value=10, max_value=100, value=30)
                new_gender = st.selectbox("Sexo", ["Masculino", "Feminino", "Outro", "Prefiro não informar"])
                new_password = st.text_input("Nova Senha", type="password")
                confirm_password = st.text_input("Confirmar Senha", type="password")
                submit = st.form_submit_button("Cadastrar")

                if submit:
                    # Validar dados
                    if not new_username or not new_email or not new_password:
                        st.error("Todos os campos são obrigatórios")
                    elif new_username in users:
                        st.error("Nome de usuário já existe")
                    elif new_password != confirm_password:
                        st.error("As senhas não coincidem")
                    else:
                        # Adicionar novo usuário
                        users[new_username] = {
                            "password": new_password,
                            "email": new_email,
                            "age": new_age,
                            "gender": new_gender
                        }
                        save_users(users)
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
            st.info("**Avaliação Mental**  \nRegistre sua prontidão para treino e analise seus resultados.")

        with col2:
            st.info("**Configurações**  \nPersonalize sua experiência no aplicativo.")

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

        # Informações do perfil
        st.subheader("Perfil")
        users = load_users()
        user_data = users[st.session_state.username]

        email = st.text_input("Email", value=user_data["email"])
        age = st.number_input("Idade", min_value=10, max_value=100, value=user_data["age"])
        gender = st.selectbox("Sexo", ["Masculino", "Feminino", "Outro", "Prefiro não informar"], 
                             index=["Masculino", "Feminino", "Outro", "Prefiro não informar"].index(user_data["gender"]))

        # Botão para salvar configurações
        if st.button("Salvar Configurações"):
            # Atualizar dados do usuário
            users[st.session_state.username]["email"] = email
            users[st.session_state.username]["age"] = age
            users[st.session_state.username]["gender"] = gender
            save_users(users)
            st.success("Configurações salvas com sucesso!")

    elif page == "Sair":
        st.session_state.authenticated = False
        st.session_state.user_id = None
        st.experimental_rerun()

# Executar o aplicativo
if __name__ == "__main__":
    main()
