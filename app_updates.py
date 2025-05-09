
# Novas funções de banco de dados para os módulos adicionais

def save_psychological_assessment(user_id, anxiety_score, stress_score, lifestyle_score, 
                                anxiety_responses, stress_responses, lifestyle_responses):
    try:
        supabase = init_supabase()
        if not supabase:
            return None

        assessment_data = {
            'user_id': user_id,
            'anxiety_score': anxiety_score,
            'stress_score': stress_score,
            'lifestyle_score': lifestyle_score,
            'anxiety_responses': anxiety_responses,
            'stress_responses': stress_responses,
            'lifestyle_responses': lifestyle_responses
        }

        response = supabase.table('psychological_assessments').insert(assessment_data).execute()
        return response.data[0]['id']
    except Exception as e:
        st.error(f"Erro ao salvar avaliação psicológica: {str(e)}")
        return None

def save_training_assessment(user_id, duration, rpe, heart_rate, trimp, training_load, notes):
    try:
        supabase = init_supabase()
        if not supabase:
            return None

        assessment_data = {
            'user_id': user_id,
            'duration': duration,
            'rpe': rpe,
            'heart_rate': heart_rate,
            'trimp': trimp,
            'training_load': training_load,
            'notes': notes
        }

        response = supabase.table('training_assessments').insert(assessment_data).execute()
        return response.data[0]['id']
    except Exception as e:
        st.error(f"Erro ao salvar avaliação de treino: {str(e)}")
        return None

def get_psychological_assessments(user_id, days=30):
    try:
        supabase = init_supabase()
        if not supabase:
            return []

        start_date = (datetime.now() - timedelta(days=days)).isoformat()

        response = supabase.table('psychological_assessments')\
            .select('*')\
            .eq('user_id', user_id)\
            .gte('created_at', start_date)\
            .order('created_at', desc=False)\
            .execute()

        return response.data
    except Exception as e:
        st.error(f"Erro ao buscar avaliações psicológicas: {str(e)}")
        return []

def get_user_training_assessments(user_id, days=30):
    try:
        supabase = init_supabase()
        if not supabase:
            return []

        start_date = (datetime.now() - timedelta(days=days)).isoformat()

        response = supabase.table('training_assessments')\
            .select('*')\
            .eq('user_id', user_id)\
            .gte('created_at', start_date)\
            .order('created_at', desc=False)\
            .execute()

        return response.data
    except Exception as e:
        st.error(f"Erro ao buscar avaliações de treino: {str(e)}")
        return []

# Atualização da função show_questionnaire para incluir as novas tabs
def show_questionnaire():
    add_logo()

    st.title(f"Olá, {st.session_state.username}! 👋")

    if st.session_state.is_admin:
        if st.sidebar.button("Painel de Administração"):
            st.session_state.show_admin = True
            st.experimental_rerun()

    if st.sidebar.button("Logout"):
        logout()

    # Novas tabs para os diferentes tipos de avaliação
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
            avg_readiness = df_readiness['adjustment_percentage'].mean()
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
                   df_readiness['adjustment_percentage'],
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
                'Prontidão': df_readiness['adjustment_percentage'],
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
