
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import os
import json
import base64
import sys
import logging
import warnings

# Suprimir todos os avisos
warnings.filterwarnings('ignore')

# Configurar logging para suprimir mensagens de aviso do Streamlit
logging.getLogger("streamlit").setLevel(logging.ERROR)
st.set_option('deprecation.showfileUploaderEncoding', False)
st.set_option('deprecation.showPyplotGlobalUse', False)

# Redirecionar stderr para suprimir mensagens de aviso
class NullWriter:
    def write(self, s):
        pass
    def flush(self):
        pass

# Redirecionar stderr para suprimir mensagens
old_stderr = sys.stderr
sys.stderr = NullWriter()

# Configuração da página
st.set_page_config(
    page_title="Sintonia - Análise de Treino",
    page_icon="🏋️",
    layout="wide"
)

# Restaurar stderr
sys.stderr = old_stderr

# Função para exibir uma imagem como logomarca
def add_logo():
    # URL direta da imagem do Imgur (formato correto)
    logo_url = "https://i.imgur.com/2wnT7zT.png"

    logo_html = f'''
        <div style="display: flex; justify-content: center; margin-bottom: 20px;">
            <img src="{logo_url}" alt="logo" style="max-width: 300px; max-height: 150px;">
        </div>
    '''
    st.markdown(logo_html, unsafe_allow_html=True)

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
if 'app_mode' not in st.session_state:
    st.session_state.app_mode = "Avaliação de Prontidão"

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

        # Redirecionar stderr para suprimir mensagens de aviso
        old_stderr = sys.stderr
        sys.stderr = NullWriter()

        try:
            # Tentar obter credenciais de variáveis de ambiente (para Render)
            url = os.environ.get("SUPABASE_URL")
            key = os.environ.get("SUPABASE_KEY")

            if not url or not key:
                # Criar um cliente dummy para evitar erros
                # Restaurar stderr
                sys.stderr = old_stderr
                st.warning("Credenciais do Supabase não encontradas. Algumas funcionalidades podem não estar disponíveis.", icon="⚠️")
                return None

            client = create_client(url, key)

            # Restaurar stderr
            sys.stderr = old_stderr

            return client
        except Exception as e:
            # Restaurar stderr
            sys.stderr = old_stderr
            st.warning(f"Erro ao conectar com Supabase: {str(e)[:100]}...", icon="⚠️")
            return None
    except Exception as e:
        st.warning(f"Erro ao importar biblioteca Supabase: {str(e)[:100]}...", icon="⚠️")
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
        return []

def get_all_users():
    try:
        supabase = init_supabase()
        if not supabase:
            return []

        response = supabase.table('users').select('*').execute()
        return response.data
    except Exception as e:
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
        return []

# Novas funções para a análise pós-treino
def save_recovery_data(psr, sleep_hours, sleep_quality, waking_feeling, readiness_index):
    try:
        supabase = init_supabase()
        if not supabase:
            return None

        recovery_data = {
            'user_id': st.session_state.user_id,
            'psr': psr,
            'sleep_hours': sleep_hours,
            'sleep_quality': sleep_quality,
            'waking_feeling': waking_feeling,
            'readiness_index': readiness_index
        }

        response = supabase.table('recovery_data').insert(recovery_data).execute()
        return response.data[0]['id']
    except Exception as e:
        st.error(f"Erro ao salvar dados de recuperação: {e}")
        return None

def save_training_data(rpe, duration, training_type, trimp, training_date):
    try:
        supabase = init_supabase()
        if not supabase:
            return None

        training_data = {
            'user_id': st.session_state.user_id,
            'rpe': rpe,
            'duration': duration,
            'training_type': training_type,
            'trimp': trimp,
            'training_date': training_date.isoformat()
        }

        response = supabase.table('training_data').insert(training_data).execute()
        return response.data[0]['id']
    except Exception as e:
        st.error(f"Erro ao salvar dados de treino: {e}")
        return None

def get_latest_recovery_data():
    try:
        supabase = init_supabase()
        if not supabase:
            return None

        response = supabase.table('recovery_data')             .select('*')             .eq('user_id', st.session_state.user_id)             .order('created_at', desc=True)             .limit(1)             .execute()

        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        st.error(f"Erro ao buscar dados de recuperação: {e}")
        return None

def get_latest_training_data():
    try:
        supabase = init_supabase()
        if not supabase:
            return None

        response = supabase.table('training_data')             .select('*')             .eq('user_id', st.session_state.user_id)             .order('created_at', desc=True)             .limit(1)             .execute()

        if response.data:
            return response.data[0]
        return None
    except Exception as e:
        st.error(f"Erro ao buscar dados de treino: {e}")
        return None

def get_training_recovery_history(days=30):
    try:
        supabase = init_supabase()
        if not supabase:
            return []

        # Calcular a data de início com base nos dias
        start_date = (datetime.now() - timedelta(days=days)).isoformat()

        # Buscar dados de recuperação
        recovery_response = supabase.table('recovery_data')             .select('*')             .eq('user_id', st.session_state.user_id)             .gte('created_at', start_date)             .order('created_at', desc=False)             .execute()

        # Buscar dados de treino
        training_response = supabase.table('training_data')             .select('*')             .eq('user_id', st.session_state.user_id)             .gte('created_at', start_date)             .order('created_at', desc=False)             .execute()

        # Processar e combinar os dados
        history = []

        if recovery_response.data and training_response.data:
            recovery_df = pd.DataFrame(recovery_response.data)
            training_df = pd.DataFrame(training_response.data)

            # Converter timestamps para datetime
            recovery_df['created_at'] = pd.to_datetime(recovery_df['created_at'])
            training_df['created_at'] = pd.to_datetime(training_df['created_at'])

            # Extrair data (sem hora)
            recovery_df['date'] = recovery_df['created_at'].dt.date
            training_df['date'] = training_df['created_at'].dt.date

            # Combinar por data
            for date in sorted(set(recovery_df['date'].tolist() + training_df['date'].tolist())):
                day_recovery = recovery_df[recovery_df['date'] == date]
                day_training = training_df[training_df['date'] == date]

                if not day_recovery.empty and not day_training.empty:
                    # Usar o último registro de cada dia
                    recovery = day_recovery.iloc[-1]
                    training = day_training.iloc[-1]

                    # Calcular razão
                    ratio = training['trimp'] / recovery['readiness_index'] if recovery['readiness_index'] > 0 else 0

                    history.append({
                        'date': date,
                        'readiness_index': recovery['readiness_index'],
                        'trimp': training['trimp'],
                        'ratio': ratio,
                        'psr': recovery['psr'],
                        'sleep_hours': recovery['sleep_hours'],
                        'sleep_quality': recovery['sleep_quality'],
                        'waking_feeling': recovery['waking_feeling'],
                        'rpe': training['rpe'],
                        'duration': training['duration'],
                        'training_type': training['training_type']
                    })

        return history
    except Exception as e:
        st.error(f"Erro ao buscar histórico: {e}")
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
    # Adicionar logo no topo
    add_logo()

    st.title("Sintonia - Análise de Treino")

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
    # Adicionar logo no topo
    add_logo()

    st.title(f"Avaliação de Prontidão - Olá, {st.session_state.username}! 👋")

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

# Função para exibir a análise pós-treino
def show_post_training_analysis():
    # Adicionar logo no topo
    add_logo()

    st.title(f"Análise Pós-Treino - Olá, {st.session_state.username}! 👋")

    # Botões de navegação no sidebar
    if st.session_state.is_admin:
        if st.sidebar.button("Painel de Administração"):
            st.session_state.show_admin = True
            st.experimental_rerun()

    if st.sidebar.button("Logout"):
        logout()

    # Tabs para diferentes partes da análise
    tab1, tab2, tab3 = st.tabs(["Registrar Dados", "Visualizar Resultados", "Histórico"])

    with tab1:
        # Formulários para entrada de dados
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Dados de Recuperação")
            with st.form("recovery_form"):
                # PSR
                st.markdown("##### PSR (Status de Recuperação Percebida)")
                st.markdown("*0-2: Muito mal recuperado, 3-4: Mal recuperado, 5-6: Razoavelmente recuperado, 7-8: Bem recuperado, 9-10: Completamente recuperado*")
                st.markdown("*Evidência: Laurent et al. (2011)*")
                psr = st.slider("Como você avalia seu estado de recuperação?", 0, 10, 5)

                # Horas de sono
                st.markdown("##### Horas de Sono")
                st.markdown("*Evidência: Mah et al. (2011) - 7-9h é o ideal para atletas*")
                sleep_hours = st.number_input("Quantas horas você dormiu?", min_value=0.0, max_value=24.0, value=7.0, step=0.5)

                # Qualidade do sono
                st.markdown("##### Qualidade do Sono")
                st.markdown("*1: Muito ruim, 2: Ruim, 3: Regular, 4: Boa, 5: Excelente*")
                st.markdown("*Evidência: Fullagar et al. (2015)*")
                sleep_quality = st.slider("Como você avalia a qualidade do seu sono?", 1, 5, 3)

                # Sensação ao acordar
                st.markdown("##### Sensação ao Acordar")
                st.markdown("*1: Muito cansado, 2: Cansado, 3: Neutro, 4: Disposto, 5: Muito disposto*")
                st.markdown("*Evidência: Saw et al. (2016)*")
                waking_feeling = st.slider("Como você se sentiu ao acordar?", 1, 5, 3)

                recovery_submit = st.form_submit_button("Salvar Dados de Recuperação")

        with col2:
            st.subheader("Dados do Treino")
            with st.form("training_form"):
                # PSE
                st.markdown("##### PSE (Percepção Subjetiva de Esforço)")
                st.markdown("*0: Repouso, 1-2: Muito fácil, 3-4: Fácil, 5-6: Moderado, 7-8: Difícil, 9-10: Máximo*")
                st.markdown("*Evidência: Foster et al. (2001)*")
                rpe = st.slider("Como você avalia o esforço do seu treino?", 0, 10, 5)

                # Duração
                st.markdown("##### Duração do Treino")
                duration = st.number_input("Duração do treino (minutos)", min_value=0, max_value=600, value=60)

                # Tipo de treino
                st.markdown("##### Tipo de Treino")
                st.markdown("*Evidência: Impellizzeri et al. (2004)*")
                training_type = st.selectbox(
                    "Qual foi o tipo principal do treino?",
                    ["Resistência", "Força", "Velocidade/Potência", "Técnico", "Misto"]
                )

                # Data do treino
                training_date = st.date_input("Data do treino", value=datetime.now())

                training_submit = st.form_submit_button("Salvar Dados do Treino")

        # Lógica para processar os formulários
        if recovery_submit:
            # Calcular índice de prontidão
            readiness_index = 2 * psr + 1.5 * sleep_hours + sleep_quality + waking_feeling
            st.success(f"Dados de recuperação salvos! Índice de Prontidão: {readiness_index:.1f}")

            # Salvar no banco de dados
            save_recovery_data(psr, sleep_hours, sleep_quality, waking_feeling, readiness_index)

        if training_submit:
            # Calcular TRIMP-PSE
            trimp = rpe * duration
            st.success(f"Dados do treino salvos! TRIMP-PSE: {trimp}")

            # Salvar no banco de dados
            save_training_data(rpe, duration, training_type, trimp, training_date)

    with tab2:
        st.subheader("Resultados da Análise")

        # Buscar dados mais recentes
        recovery_data = get_latest_recovery_data()
        training_data = get_latest_training_data()

        if recovery_data and training_data:
            # Calcular razão de correspondência
            readiness_index = recovery_data['readiness_index']
            trimp = training_data['trimp']
            ratio = trimp / readiness_index

            # Exibir resultados
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Índice de Prontidão", f"{readiness_index:.1f}")
                st.caption("*Baseado em: McLean et al. (2010) e Hooper et al. (1995)*")

            with col2:
                st.metric("TRIMP-PSE", f"{trimp}")
                st.caption("*Baseado em: Foster et al. (1998, 2001)*")

            with col3:
                st.metric("Razão de Correspondência", f"{ratio:.2f}")
                st.caption("*Baseado em: Gabbett (2016) e Halson (2014)*")

            # Interpretação da razão
            st.subheader("Interpretação")

            if ratio < 0.8:
                st.info("📊 **Reserva de capacidade** (Razão < 0.8)")
                st.markdown("O treino poderia ter sido mais intenso considerando seu estado de recuperação. Você tem uma boa reserva de capacidade para aumentar a intensidade ou volume nas próximas sessões.")
            elif ratio <= 1.2:
                st.success("✅ **Carregamento adequado** (Razão entre 0.8 e 1.2)")
                st.markdown("Equilíbrio ideal entre carga e recuperação. Você está treinando em um nível apropriado para seu estado atual de recuperação.")
            else:
                st.warning("⚠️ **Potencial sobrecarga** (Razão > 1.2)")
                st.markdown("A carga de treino foi elevada para seu estado de recuperação atual. Considere priorizar a recuperação antes da próxima sessão intensa.")

            # Gráfico de radar para visualizar componentes
            st.subheader("Componentes da Recuperação")

            # Preparar dados para o gráfico de radar
            categories = ['PSR', 'Sono (h)', 'Qualidade Sono', 'Sensação ao Acordar']

            # Normalizar valores para escala 0-1
            psr_norm = recovery_data['psr'] / 10
            sleep_hours_norm = min(recovery_data['sleep_hours'] / 10, 1)  # Normalizar para máximo de 10h
            sleep_quality_norm = recovery_data['sleep_quality'] / 5
            waking_feeling_norm = recovery_data['waking_feeling'] / 5

            values = [psr_norm, sleep_hours_norm, sleep_quality_norm, waking_feeling_norm]
            values += values[:1]  # Fechar o gráfico

            angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False).tolist()
            angles += angles[:1]  # Fechar o gráfico

            fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
            ax.plot(angles, values, linewidth=2, linestyle='solid')
            ax.fill(angles, values, alpha=0.25)
            ax.set_thetagrids(np.degrees(angles[:-1]), categories)
            ax.set_ylim(0, 1)
            ax.grid(True)
            ax.set_title("Perfil de Recuperação", size=20, y=1.05)

            st.pyplot(fig)
        else:
            st.info("Registre dados de recuperação e treino para visualizar os resultados da análise.")

    with tab3:
        st.subheader("Histórico de Treinos e Recuperação")

        # Seletor de período
        period = st.selectbox("Período", [7, 14, 30], format_func=lambda x: f"Últimos {x} dias")

        # Buscar histórico
        history = get_training_recovery_history(period)

        if history:
            # Criar DataFrame
            df = pd.DataFrame(history)

            # Gráfico de tendências
            st.subheader("Tendências ao Longo do Tempo")
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.plot(df['date'], df['readiness_index'], 'b-o', label='Índice de Prontidão')
            ax.plot(df['date'], df['trimp'], 'r-o', label='TRIMP-PSE')
            ax.set_title('Índice de Prontidão vs TRIMP-PSE')
            ax.set_xlabel('Data')
            ax.legend()
            ax.grid(True)
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig)

            # Gráfico da razão
            st.subheader("Razão de Correspondência")
            fig2, ax2 = plt.subplots(figsize=(10, 6))

            # Adicionar linhas de referência
            ax2.axhline(y=0.8, color='g', linestyle='--', alpha=0.5)
            ax2.axhline(y=1.2, color='r', linestyle='--', alpha=0.5)

            # Plotar razão
            scatter = ax2.scatter(df['date'], df['ratio'], c=df['ratio'].apply(lambda x: 'green' if x < 0.8 else 'red' if x > 1.2 else 'blue'), s=100)

            ax2.set_title('Razão de Correspondência (TRIMP/Prontidão)')
            ax2.set_xlabel('Data')
            ax2.set_ylabel('Razão')
            ax2.grid(True)
            plt.xticks(rotation=45)
            plt.tight_layout()
            st.pyplot(fig2)

            # Tabela de dados
            st.subheader("Dados Detalhados")
            display_df = df[['date', 'readiness_index', 'trimp', 'ratio', 'psr', 'sleep_hours', 'sleep_quality', 'waking_feeling', 'rpe', 'duration', 'training_type']]
            display_df.columns = ['Data', 'Índice de Prontidão', 'TRIMP', 'Razão', 'PSR', 'Horas de Sono', 'Qualidade do Sono', 'Sensação ao Acordar', 'PSE', 'Duração (min)', 'Tipo de Treino']
            st.dataframe(display_df)
        else:
            st.info("Nenhum dado histórico encontrado para o período selecionado.")

# Função para exibir o painel de administração
def admin_dashboard():
    # Adicionar logo no topo
    add_logo()

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
    # Redirecionar stderr para suprimir mensagens de aviso
    old_stderr = sys.stderr
    sys.stderr = NullWriter()

    try:
        # Verificar conexão com Supabase
        supabase = init_supabase()

        if not st.session_state.logged_in:
            login_form()
        else:
            # Adicionar seleção de modo no sidebar
            app_mode = st.sidebar.radio(
                "Selecione o modo:",
                ["Avaliação de Prontidão", "Análise Pós-Treino"]
            )

            st.session_state.app_mode = app_mode

            if app_mode == "Avaliação de Prontidão":
                # Código existente do Sintonia
                if st.session_state.is_admin and st.session_state.show_admin:
                    admin_dashboard()
                else:
                    show_questionnaire()
            else:
                # Nova funcionalidade
                show_post_training_analysis()
    except Exception as e:
        st.error(f"Erro na aplicação: {e}")
        st.info("Tente recarregar a página ou entre em contato com o administrador.")
    finally:
        # Restaurar stderr
        sys.stderr = old_stderr

if __name__ == "__main__":
    main()
