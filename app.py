
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import os
import json

# Configuração da página
st.set_page_config(
    page_title="Questionário de Prontidão para Treinamento",
    page_icon="🏋️",
    layout="wide"
)

# Inicialização de variáveis de sessão
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'is_admin' not in st.session_state:
    st.session_state.is_admin = False
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'show_admin' not in st.session_state:
    st.session_state.show_admin = False
if 'users' not in st.session_state:
    st.session_state.users = []
if 'assessments' not in st.session_state:
    st.session_state.assessments = []

# Funções de utilidade
def calculate_score(responses):
    '''Calcula a pontuação total com base nas respostas do questionário.'''
    return sum(responses)

def calculate_adjustment(score):
    '''Calcula o ajuste percentual da carga de treinamento.'''
    max_score = 40  # 8 perguntas * 5 pontos cada
    adjustment = (score / max_score) * 100
    return adjustment

# Funções de banco de dados
def init_supabase():
    try:
        from supabase import create_client

        # Tentar obter credenciais de st.secrets primeiro (para Streamlit Cloud)
        try:
            url = st.secrets["SUPABASE_URL"]
            key = st.secrets["SUPABASE_KEY"]
        except:
            # Caso contrário, usar variáveis de ambiente (para Render)
            url = os.environ.get("SUPABASE_URL")
            key = os.environ.get("SUPABASE_KEY")

        if not url or not key:
            st.error("Credenciais do Supabase não encontradas.")
            return None

        return create_client(url, key)
    except Exception as e:
        st.error(f"Erro ao conectar com Supabase: {e}")
        return None

def create_user(username, password, email, is_admin=False):
    try:
        supabase = init_supabase()
        if not supabase:
            return False, "Erro de conexão com o banco de dados"

        # Verificar se o usuário já existe
        response = supabase.table('users').select('*').eq('username', username).execute()
        if len(response.data) > 0:
            return False, "Nome de usuário já existe"

        response = supabase.table('users').select('*').eq('email', email).execute()
        if len(response.data) > 0:
            return False, "Email já está em uso"

        # Criar novo usuário
        user_data = {
            'username': username,
            'password': password,
            'email': email,
            'is_admin': is_admin
        }

        response = supabase.table('users').insert(user_data).execute()
        return True, response.data[0]['id']
    except Exception as e:
        st.error(f"Erro ao criar usuário: {e}")
        return False, str(e)

def authenticate_user(username, password):
    try:
        supabase = init_supabase()
        if not supabase:
            return False, None

        response = supabase.table('users').select('*').eq('username', username).eq('password', password).execute()

        if len(response.data) > 0:
            return True, response.data[0]
        return False, None
    except Exception as e:
        st.error(f"Erro ao autenticar: {e}")
        return False, None

def save_assessment(user_id, score, adjustment_percentage, responses):
    try:
        supabase = init_supabase()
        if not supabase:
            return None

        assessment_data = {
            'user_id': user_id,
            'score': score,
            'adjustment_percentage': adjustment_percentage,
            'sleep_quality': responses[0],
            'muscle_soreness': responses[1],
            'fatigue_level': responses[2],
            'stress_level': responses[3],
            'mood': responses[4],
            'appetite': responses[5],
            'motivation': responses[6],
            'recovery_perception': responses[7]
        }

        response = supabase.table('assessments').insert(assessment_data).execute()
        return response.data[0]['id']
    except Exception as e:
        st.error(f"Erro ao salvar avaliação: {e}")
        return None

def get_user_assessments(user_id, days=30):
    try:
        supabase = init_supabase()
        if not supabase:
            return []

        # Calcular a data de início com base nos dias
        start_date = (datetime.now() - timedelta(days=days)).isoformat()

        response = supabase.table('assessments')             .select('*')             .eq('user_id', user_id)             .gte('created_at', start_date)             .order('created_at', desc=False)             .execute()

        return response.data
    except Exception as e:
        st.error(f"Erro ao buscar avaliações: {e}")
        return []

def get_all_users():
    try:
        supabase = init_supabase()
        if not supabase:
            return []

        response = supabase.table('users').select('*').execute()
        return response.data
    except Exception as e:
        st.error(f"Erro ao buscar usuários: {e}")
        return []

def get_all_assessments(days=30):
    try:
        supabase = init_supabase()
        if not supabase:
            return []

        # Calcular a data de início com base nos dias
        start_date = (datetime.now() - timedelta(days=days)).isoformat()

        response = supabase.table('assessments')             .select('*, users(username)')             .gte('created_at', start_date)             .order('created_at', desc=True)             .execute()

        return response.data
    except Exception as e:
        st.error(f"Erro ao buscar todas as avaliações: {e}")
        return []

def get_recent_registrations(days=7):
    try:
        supabase = init_supabase()
        if not supabase:
            return []

        # Calcular a data de início com base nos dias
        start_date = (datetime.now() - timedelta(days=days)).isoformat()

        response = supabase.table('users')             .select('*')             .gte('created_at', start_date)             .order('created_at', desc=True)             .execute()

        return response.data
    except Exception as e:
        st.error(f"Erro ao buscar registros recentes: {e}")
        return []

# Função para fazer logout
def logout():
    st.session_state.logged_in = False
    st.session_state.user_id = None
    st.session_state.is_admin = False
    st.session_state.username = ""
    st.session_state.show_admin = False
    st.experimental_rerun()

# Função para exibir o formulário de login
def login_form():
    st.title("Questionário de Prontidão para Treinamento")

    tab1, tab2 = st.tabs(["Login", "Cadastro"])

    with tab1:
        with st.form("login_form"):
            username = st.text_input("Nome de usuário")
            password = st.text_input("Senha", type="password")
            submit = st.form_submit_button("Entrar")

            if submit:
                if username and password:
                    success, user = authenticate_user(username, password)
                    if success:
                        st.session_state.logged_in = True
                        st.session_state.user_id = user['id']
                        st.session_state.is_admin = user['is_admin']
                        st.session_state.username = user['username']
                        st.experimental_rerun()
                    else:
                        st.error("Nome de usuário ou senha incorretos.")
                else:
                    st.error("Por favor, preencha todos os campos.")

    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("Nome de usuário")
            new_email = st.text_input("Email")
            new_password = st.text_input("Senha", type="password")
            confirm_password = st.text_input("Confirmar senha", type="password")
            submit = st.form_submit_button("Cadastrar")

            if submit:
                if new_username and new_email and new_password:
                    if new_password != confirm_password:
                        st.error("As senhas não coincidem.")
                    else:
                        success, message = create_user(new_username, new_password, new_email)
                        if success:
                            st.success("Cadastro realizado com sucesso! Faça login para continuar.")
                        else:
                            st.error(f"Erro ao cadastrar: {message}")
                else:
                    st.error("Por favor, preencha todos os campos.")

# Função para exibir o questionário
def show_questionnaire():
    st.title(f"Olá, {st.session_state.username}! 👋")

    if st.session_state.is_admin:
        if st.sidebar.button("Painel de Administração"):
            st.session_state.show_admin = True
            st.experimental_rerun()

    if st.sidebar.button("Logout"):
        logout()

    # Mostrar histórico de avaliações
    st.sidebar.header("Histórico de Avaliações")
    period = st.sidebar.selectbox("Período", [7, 14, 30], format_func=lambda x: f"Últimos {x} dias")

    # Buscar avaliações do usuário
    assessments = get_user_assessments(st.session_state.user_id, days=period)

    if assessments:
        # Preparar dados para o gráfico
        df = pd.DataFrame(assessments)
        df['created_at'] = pd.to_datetime(df['created_at'])
        df = df.sort_values('created_at')

        # Criar gráfico na barra lateral
        fig, ax = plt.subplots(figsize=(8, 4))
        ax.plot(df['created_at'], df['adjustment_percentage'], marker='o', linestyle='-', color='blue')
        ax.set_title('Ajuste de Carga ao Longo do Tempo')
        ax.set_ylabel('Ajuste de Carga (%)')
        ax.set_ylim([0, 100])
        ax.grid(True)
        plt.xticks(rotation=45)
        plt.tight_layout()
        st.sidebar.pyplot(fig)
    else:
        st.sidebar.info("Nenhuma avaliação encontrada para o período selecionado.")

    # Questionário
    st.header("Questionário de Prontidão para Treinamento")
    st.write("Avalie como você se sente hoje em uma escala de 1 a 5:")

    with st.form("readiness_form"):
        # Perguntas do questionário
        questions = [
            "Qualidade do sono (1 = muito ruim, 5 = excelente)",
            "Dor muscular (1 = muita dor, 5 = sem dor)",
            "Nível de fadiga (1 = muito fatigado, 5 = sem fadiga)",
            "Nível de estresse (1 = muito estressado, 5 = relaxado)",
            "Humor (1 = muito irritado, 5 = muito feliz)",
            "Apetite (1 = sem apetite, 5 = apetite normal)",
            "Motivação para treinar (1 = desmotivado, 5 = muito motivado)",
            "Percepção de recuperação (1 = não recuperado, 5 = totalmente recuperado)"
        ]

        responses = []
        for i, question in enumerate(questions):
            response = st.slider(question, 1, 5, 3)
            responses.append(response)

        submit = st.form_submit_button("Calcular Prontidão")

        if submit:
            # Calcular pontuação e ajuste
            score = calculate_score(responses)
            adjustment = calculate_adjustment(score)

            # Salvar avaliação
            assessment_id = save_assessment(st.session_state.user_id, score, adjustment, responses)

            # Exibir resultados
            if assessment_id:
                st.success(f"Avaliação concluída! ID: {assessment_id}")
            else:
                st.warning("Avaliação calculada, mas não foi possível salvar no banco de dados.")

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Pontuação de Prontidão", f"{score:.1f}/40", f"{score/40*100:.1f}%")
            with col2:
                st.metric("Ajuste de Carga", f"{adjustment:.1f}%")

            # Gráfico de radar para visualizar as respostas
            categories = ['Sono', 'Dor Muscular', 'Fadiga', 'Estresse', 
                         'Humor', 'Apetite', 'Motivação', 'Recuperação']

            values = responses.copy()
            values += values[:1]  # Fechar o gráfico

            angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False).tolist()
            angles += angles[:1]  # Fechar o gráfico

            fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
            ax.plot(angles, values, linewidth=2, linestyle='solid')
            ax.fill(angles, values, alpha=0.25)
            ax.set_thetagrids(np.degrees(angles[:-1]), categories)
            ax.set_ylim(0, 5)
            ax.grid(True)
            ax.set_title("Perfil de Prontidão", size=20, y=1.05)

            st.pyplot(fig)

            # Recomendações baseadas na pontuação
            st.subheader("Recomendações")
            if adjustment < 70:
                st.warning("Sua prontidão está baixa. Considere reduzir significativamente a intensidade do treino hoje.")
            elif adjustment < 85:
                st.info("Sua prontidão está moderada. Reduza um pouco a intensidade do treino hoje.")
            else:
                st.success("Sua prontidão está boa. Você pode realizar o treino conforme planejado.")

# Função para exibir o painel de administração
def admin_dashboard():
    st.title("Painel de Administração")

    # Botão para voltar ao questionário
    if st.sidebar.button("Voltar ao Questionário"):
        st.session_state.show_admin = False
        st.experimental_rerun()

    # Botão de logout
    if st.sidebar.button("Logout"):
        logout()

    # Tabs para diferentes seções do painel
    tab1, tab2, tab3 = st.tabs(["Usuários", "Avaliações", "Notificações"])

    with tab1:
        st.header("Usuários Registrados")
        users = get_all_users()

        if users:
            users_df = pd.DataFrame(users)
            users_df['created_at'] = pd.to_datetime(users_df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
            users_df = users_df[['id', 'username', 'email', 'is_admin', 'created_at']]
            users_df.columns = ['ID', 'Usuário', 'Email', 'Admin', 'Data de Registro']

            st.dataframe(users_df)
            st.write(f"Total de usuários: {len(users)}")
        else:
            st.info("Nenhum usuário registrado ou erro ao buscar usuários.")

    with tab2:
        st.header("Avaliações Recentes")

        # Seletor de período
        period = st.selectbox("Período", [7, 14, 30, 90], format_func=lambda x: f"Últimos {x} dias", key="assessment_period")

        assessments = get_all_assessments(days=period)

        if assessments:
            try:
                # Processar dados para exibição
                assessments_df = pd.DataFrame(assessments)

                # Extrair username da coluna aninhada
                assessments_df['username'] = assessments_df['users'].apply(lambda x: x['username'] if x else 'Desconhecido')

                # Formatar data
                assessments_df['created_at'] = pd.to_datetime(assessments_df['created_at']).dt.strftime('%Y-%m-%d %H:%M')

                # Selecionar e renomear colunas para exibição
                display_df = assessments_df[[
                    'id', 'username', 'score', 'adjustment_percentage', 
                    'sleep_quality', 'muscle_soreness', 'fatigue_level', 
                    'stress_level', 'mood', 'appetite', 'motivation', 
                    'recovery_perception', 'created_at'
                ]]

                display_df.columns = [
                    'ID', 'Usuário', 'Pontuação', 'Ajuste (%)', 
                    'Sono', 'Dor Muscular', 'Fadiga', 
                    'Estresse', 'Humor', 'Apetite', 'Motivação', 
                    'Recuperação', 'Data'
                ]

                st.dataframe(display_df)

                # Gráfico de média de ajuste por dia
                st.subheader("Média de Ajuste por Dia")

                # Converter de volta para processamento
                assessments_df['created_at'] = pd.to_datetime(assessments_df['created_at'])
                assessments_df['date'] = assessments_df['created_at'].dt.date

                # Calcular média por dia
                daily_avg = assessments_df.groupby('date')['adjustment_percentage'].mean().reset_index()

                fig, ax = plt.subplots(figsize=(10, 6))
                ax.plot(daily_avg['date'], daily_avg['adjustment_percentage'], marker='o', linestyle='-')
                ax.set_title('Média de Ajuste de Carga por Dia')
                ax.set_xlabel('Data')
                ax.set_ylabel('Ajuste Médio (%)')
                ax.set_ylim([0, 100])
                ax.grid(True)
                plt.xticks(rotation=45)
                plt.tight_layout()

                st.pyplot(fig)

                # Estatísticas gerais
                st.subheader("Estatísticas Gerais")
                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric("Total de Avaliações", len(assessments_df))

                with col2:
                    avg_score = assessments_df['score'].mean()
                    st.metric("Pontuação Média", f"{avg_score:.1f}")

                with col3:
                    avg_adjustment = assessments_df['adjustment_percentage'].mean()
                    st.metric("Ajuste Médio", f"{avg_adjustment:.1f}%")
            except Exception as e:
                st.error(f"Erro ao processar dados de avaliações: {e}")
        else:
            st.info("Nenhuma avaliação encontrada para o período selecionado.")

    with tab3:
        st.header("Notificações")

        # Novos registros
        st.subheader("Novos Usuários Registrados")
        new_users = get_recent_registrations(days=7)

        if new_users:
            try:
                new_users_df = pd.DataFrame(new_users)
                new_users_df['created_at'] = pd.to_datetime(new_users_df['created_at']).dt.strftime('%Y-%m-%d %H:%M')
                new_users_df = new_users_df[['username', 'email', 'created_at']]
                new_users_df.columns = ['Usuário', 'Email', 'Data de Registro']

                st.dataframe(new_users_df)
                st.success(f"{len(new_users)} novos usuários nos últimos 7 dias")
            except Exception as e:
                st.error(f"Erro ao processar dados de novos usuários: {e}")
        else:
            st.info("Nenhum novo usuário registrado nos últimos 7 dias.")

# Função principal
def main():
    try:
        # Verificar conexão com Supabase
        supabase = init_supabase()
        if not supabase:
            st.warning("Não foi possível conectar ao banco de dados. Algumas funcionalidades podem não estar disponíveis.")
            st.info("Verifique se as variáveis de ambiente SUPABASE_URL e SUPABASE_KEY estão configuradas corretamente.")

            # Exibir informações de depuração
            st.write("Informações de depuração:")
            try:
                st.write(f"SUPABASE_URL em variáveis de ambiente: {'Sim' if os.environ.get('SUPABASE_URL') else 'Não'}")
                st.write(f"SUPABASE_KEY em variáveis de ambiente: {'Sim' if os.environ.get('SUPABASE_KEY') else 'Não'}")
            except:
                st.write("Não foi possível verificar variáveis de ambiente")

        if not st.session_state.logged_in:
            login_form()
        elif st.session_state.is_admin and st.session_state.show_admin:
            admin_dashboard()
        else:
            show_questionnaire()
    except Exception as e:
        st.error(f"Erro na aplicação: {e}")
        st.info("Tente recarregar a página ou entre em contato com o administrador.")

if __name__ == "__main__":
    main()
