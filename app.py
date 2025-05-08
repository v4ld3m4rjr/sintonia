
import streamlit as st

# Configuração da página
st.set_page_config(
    page_title="Sintonia",
    page_icon="🧠",
    layout="wide"
)

# Inicializar estado da sessão
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.username = None

# Usuários de demonstração (em memória)
DEMO_USERS = {
    "demo": {"password": "demo123", "email": "demo@example.com", "age": 30, "gender": "Masculino"}
}

# Interface de login/registro
if not st.session_state.authenticated:
    st.title("Sintonia")

    tab1, tab2 = st.tabs(["Login", "Registro"])

    with tab1:
        with st.form("login_form"):
            st.subheader("Login")
            username = st.text_input("Usuário")
            password = st.text_input("Senha", type="password")
            submit = st.form_submit_button("Entrar")

            if submit:
                if username in DEMO_USERS and DEMO_USERS[username]["password"] == password:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.rerun()
                else:
                    st.error("Credenciais inválidas")

    with tab2:
        with st.form("signup_form"):
            st.subheader("Criar nova conta")
            new_username = st.text_input("Novo Usuário")
            new_email = st.text_input("Email")
            new_age = st.number_input("Idade", min_value=10, max_value=100, value=30)
            new_gender = st.selectbox("Sexo", ["Masculino", "Feminino", "Outro", "Prefiro não informar"])
            new_password = st.text_input("Nova Senha", type="password")
            confirm_password = st.text_input("Confirmar Senha", type="password")
            submit = st.form_submit_button("Cadastrar")

            if submit:
                if not new_username or not new_email or not new_password:
                    st.error("Todos os campos são obrigatórios")
                elif new_username in DEMO_USERS:
                    st.error("Nome de usuário já existe")
                elif new_password != confirm_password:
                    st.error("As senhas não coincidem")
                else:
                    # Adicionar novo usuário (apenas para a sessão atual)
                    DEMO_USERS[new_username] = {
                        "password": new_password,
                        "email": new_email,
                        "age": new_age,
                        "gender": new_gender
                    }
                    st.success("Conta criada com sucesso! Faça login.")
                    # Fazer login automaticamente
                    st.session_state.authenticated = True
                    st.session_state.username = new_username
                    st.rerun()
else:
    # Interface principal
    st.sidebar.title("Sintonia")
    st.sidebar.write(f"Olá, {st.session_state.username}!")

    # Menu de navegação
    page = st.sidebar.radio(
        "Navegação",
        ["Início", "Avaliação Mental", "Configurações", "Sair"]
    )

    # Botão de logout
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()

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
        st.title("Avaliação Mental")

        # Abas para diferentes funcionalidades
        tabs = st.tabs(["Avaliação de Prontidão", "Análise Pós-Treino", "Histórico"])

        with tabs[0]:
            st.subheader("Avaliação de Prontidão")

            with st.form("readiness_form"):
                col1, col2 = st.columns(2)

                with col1:
                    date = st.date_input("Data", st.session_state.get("date", None))
                    sleep_quality = st.slider("Qualidade do Sono (1-10)", 1, 10, 5)
                    sleep_duration = st.number_input("Duração do Sono (horas)", 0.0, 12.0, 7.0, 0.5)

                with col2:
                    psr = st.slider("Percepção de Status de Recuperação (1-10)", 1, 10, 5)
                    waking_sensation = st.slider("Sensação ao Acordar (1-10)", 1, 10, 5)
                    stress_level = st.slider("Nível de Estresse (1-10, 10=baixo)", 1, 10, 5)

                submit = st.form_submit_button("Calcular Prontidão")

                if submit:
                    # Calcular índice de prontidão
                    weights = {
                        "sleep_quality": 0.25,
                        "sleep_duration": 0.15,
                        "psr": 0.30,
                        "waking_sensation": 0.20,
                        "stress_level": 0.10
                    }

                    # Normalizar duração do sono (considerando 8h como ideal)
                    normalized_sleep = min(sleep_duration / 8.0, 1.0) * 10

                    # Calcular índice ponderado
                    readiness_index = (
                        weights["sleep_quality"] * sleep_quality +
                        weights["sleep_duration"] * normalized_sleep +
                        weights["psr"] * psr +
                        weights["waking_sensation"] * waking_sensation +
                        weights["stress_level"] * stress_level
                    )

                    readiness_index = round(readiness_index, 1)

                    # Exibir resultado
                    st.subheader(f"Índice de Prontidão: {readiness_index}/10")

                    # Interpretação
                    if readiness_index < 4:
                        st.warning("Baixa prontidão (< 4): Considere um treino leve ou recuperativo, ou até mesmo descanso.")
                    elif readiness_index < 7:
                        st.info("Prontidão moderada (4-7): Treino de intensidade moderada recomendado.")
                    else:
                        st.success("Alta prontidão (> 7): Você está bem recuperado e pronto para um treino de alta intensidade.")

        with tabs[1]:
            st.subheader("Análise Pós-Treino")

            with st.form("post_training_form"):
                col1, col2 = st.columns(2)

                with col1:
                    training_date = st.date_input("Data do Treino")
                    training_type = st.selectbox(
                        "Tipo de Treino",
                        ["Corrida", "Ciclismo", "Natação", "Musculação", "Funcional", "Outro"]
                    )
                    pse = st.slider("Percepção Subjetiva de Esforço (1-10)", 1, 10, 5)

                with col2:
                    duration = st.number_input("Duração (minutos)", 5, 300, 60, 5)
                    notes = st.text_area("Observações", height=100)

                submit = st.form_submit_button("Calcular TRIMP")

                if submit:
                    # Calcular TRIMP
                    trimp = round(pse * duration / 10, 1)

                    # Exibir resultado
                    st.subheader(f"TRIMP (Carga de Treino): {trimp}")

                    # Interpretação
                    if trimp < 50:
                        st.info("Carga baixa (< 50): Treino leve ou recuperativo.")
                    elif trimp < 100:
                        st.success("Carga moderada (50-100): Treino de intensidade moderada.")
                    elif trimp < 150:
                        st.warning("Carga alta (100-150): Treino intenso, monitore a recuperação.")
                    else:
                        st.error("Carga muito alta (> 150): Treino extremamente intenso, priorize a recuperação.")

        with tabs[2]:
            st.subheader("Histórico")
            st.info("O histórico será implementado em uma versão futura.")

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

        user_data = DEMO_USERS.get(st.session_state.username, {})

        email = st.text_input("Email", value=user_data.get("email", ""))
        age = st.number_input("Idade", min_value=10, max_value=100, value=user_data.get("age", 30))
        gender = st.selectbox("Sexo", ["Masculino", "Feminino", "Outro", "Prefiro não informar"], 
                             index=["Masculino", "Feminino", "Outro", "Prefiro não informar"].index(user_data.get("gender", "Prefiro não informar")))

        # Botão para salvar configurações
        if st.button("Salvar Configurações"):
            # Atualizar dados do usuário (apenas para a sessão atual)
            DEMO_USERS[st.session_state.username] = {
                **user_data,
                "email": email,
                "age": age,
                "gender": gender
            }
            st.success("Configurações salvas com sucesso!")

    elif page == "Sair":
        st.session_state.authenticated = False
        st.session_state.username = None
        st.rerun()
