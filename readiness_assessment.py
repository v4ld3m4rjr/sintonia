import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Importar funções do arquivo utils
from utils import init_supabase, get_user_assessments

def compute_readiness(ctl, atl, hooper, tqr, nprs,
                     alpha=1.0, beta=1.0, gamma=1.0):
    """
    Readiness simplified:
    (ctl - atl)
      - alpha * ((hooper - 4) / 24)
      - beta * ((20 - tqr) / 14)
      - gamma * (nprs / 10)
    """
    fitness_vs_fadiga = ctl - atl
    hooper_norm = (hooper - 4) / 24
    tqr_norm = (20 - tqr) / 14
    nprs_norm = nprs / 10
    
    readiness = fitness_vs_fadiga - alpha * hooper_norm - beta * tqr_norm - gamma * nprs_norm
    # Normalizar para porcentagem (0-100%)
    readiness = min(max(readiness * 10 + 50, 0), 100)
    
    return readiness

def analyze_readiness_trend(readiness_data):
    """
    Analisa a tendência dos dados de prontidão
    Retorna: direção da tendência, força da tendência
    """
    if len(readiness_data) < 3:
        return None, None
    
    scores = [entry['readiness'] for entry in readiness_data]
    x = np.arange(len(scores))
    
    # Regressão linear
    slope, intercept, r_value, p_value, std_err = np.polyfit(x, scores, 1, full=True)[0:5]
    
    # Determinar direção e força
    direction = "melhorando" if slope > 0 else "piorando"
    strength = abs(r_value)
    
    return direction, strength

def show_readiness_assessment():
    st.header("Avaliação de Prontidão")
    st.markdown("""
    Esta avaliação utiliza ferramentas validadas cientificamente para medir sua prontidão física:
    * **Hooper Index**: Avalia fadiga, estresse, dor muscular e qualidade do sono
    * **TQR (Total Quality Recovery)**: Avalia a percepção global de recuperação
    * **NPRS (Numeric Pain Rating Scale)**: Avalia a intensidade da dor musculoesquelética
    """)
    
    # Hooper Index
    st.subheader("Hooper Index")
    col1, col2 = st.columns(2)
    
    with col1:
        hooper_fadiga = st.slider("Fadiga (1–7)", 1, 7, help="1 = muito, muito baixo, 7 = muito, muito alto")
        hooper_estresse = st.slider("Estresse (1–7)", 1, 7, help="1 = muito, muito baixo, 7 = muito, muito alto")
    
    with col2:
        hooper_doms = st.slider("Dor Muscular (1–7)", 1, 7, help="1 = nenhuma, 7 = extrema")
        hooper_sono = st.slider("Qualidade do Sono (1–7)", 1, 7, help="1 = muito, muito ruim, 7 = muito, muito boa")
    
    hooper_total = hooper_fadiga + hooper_estresse + hooper_doms + hooper_sono
    st.info(f"Hooper Index Total: {hooper_total}/28")
    
    # TQR
    st.subheader("Total Quality Recovery (TQR)")
    tqr = st.slider("Em uma escala de 6 a 20, como você avalia sua recuperação nas últimas 24 horas?", 
                     6, 20, help="6 = recuperação muito, muito ruim, 20 = recuperação muito, muito boa")
    
    # NPRS
    st.subheader("Numeric Pain Rating Scale (NPRS)")
    nprs = st.slider("Em uma escala de 0 a 10, qual a intensidade da sua dor musculoesquelética atual?",
                     0, 10, help="0 = sem dor, 10 = pior dor imaginável")
    
    # CTL e ATL
    st.subheader("Histórico de Carga")
    col1, col2 = st.columns(2)
    
    with col1:
        ctl = st.number_input("CTL (Fitness acumulado até ontem)", value=0.0)
    
    with col2:
        atl = st.number_input("ATL (Fadiga acumulada até ontem)", value=0.0)
    
    # Calcular readiness
    readiness = compute_readiness(ctl, atl, hooper_total, tqr, nprs)
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.metric("Prontidão", f"{readiness:.1f}%")
        
        # Interpretação
        if readiness >= 80:
            st.success("Estado ótimo para treino intenso")
        elif readiness >= 60:
            st.info("Bom estado para treino normal")
        elif readiness >= 40:
            st.warning("Reduzir intensidade do treino")
        else:
            st.error("Priorizar recuperação")
    
    # Histórico e tendências
    with col2:
        if st.session_state.get('user_id'):
            # Buscar histórico
            readiness_history = get_user_assessments(st.session_state.user_id, days=7)
            
            if readiness_history:
                # Analisar tendência
                direction, strength = analyze_readiness_trend(readiness_history)
                
                if direction and strength:
                    st.info(f"Tendência: Prontidão está {direction} (confiança: {strength:.2f})")
                
                # Gráfico
                df = pd.DataFrame(readiness_history)
                df['created_at'] = pd.to_datetime(df['created_at'])
                
                fig, ax = plt.subplots(figsize=(8, 4))
                ax.plot(df['created_at'], df['readiness'], 'o-', label='Prontidão')
                
                # Linha de tendência
                x = np.arange(len(df))
                if len(x) > 1:
                    z = np.polyfit(x, df['readiness'], 1)
                    p = np.poly1d(z)
                    ax.plot(df['created_at'], p(x), "r--", label='Tendência')
                
                ax.set_title('Histórico de Prontidão (7 dias)')
                ax.set_ylabel('Prontidão (%)')
                ax.set_xlabel('Data')
                ax.grid(True)
                ax.legend()
                plt.xticks(rotation=45)
                plt.tight_layout()
                
                st.pyplot(fig)
            else:
                st.info("Nenhum histórico disponível. Os dados aparecerão após a primeira avaliação.")
    
    # Botão para salvar
    if st.button("Salvar Avaliação"):
        if not st.session_state.get('user_id'):
            st.error("Faça login para salvar avaliações")
            return
            
        supabase = init_supabase()
        if not supabase:
            return
            
        try:
            assessment_data = {
                "user_id": st.session_state.user_id,
                "hooper_fadiga": hooper_fadiga,
                "hooper_estresse": hooper_estresse,
                "hooper_dor": hooper_doms,
                "hooper_sono": hooper_sono,
                "hooper_total": hooper_total,
                "tqr": tqr,
                "nprs": nprs,
                "ctl": ctl,
                "atl": atl,
                "readiness": readiness
            }
            
            response = supabase.table("readiness_assessments").insert(assessment_data).execute()
            
            if response.data:
                st.success("Avaliação de prontidão salva com sucesso!")
                
                # Atualizar o histórico na sessão
                new_entry = {
                    "id": response.data[0]['id'],
                    "date": datetime.now(),
                    "readiness": readiness,
                    "hooper": hooper_total,
                    "tqr": tqr,
                    "nprs": nprs
                }
                
                if 'readiness_history' not in st.session_state:
                    st.session_state.readiness_history = []
                    
                st.session_state.readiness_history.append(new_entry)
            else:
                st.error("Erro ao salvar avaliação")
        except Exception as e:
            st.error(f"Erro: {str(e)}")