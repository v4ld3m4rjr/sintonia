import os
import streamlit as st
from supabase import create_client, Client
import pandas as pd

# --- Supabase config ---
# Primeiro tenta ler do ambiente (Render), depois de st.secrets (local)
SUPABASE_URL = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Cálculos ---
def compute_trimp(rpe: float, duration_min: int) -> float:
    """
    TRIMP via método S-RPE
    TRIMP = RPE * duração em minutos
    """
    return rpe * duration_min

def compute_readiness(ctl: float, atl: float, hooper: int, tqr: int, nprs: int,
                      alpha: float = 1.0, beta: float = 1.0, gamma: float = 1.0) -> float:
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
    return fitness_vs_fadiga - alpha * hooper_norm - beta * tqr_norm - gamma * nprs_norm

# --- Layout do Streamlit ---
st.sidebar.title("Configurações")
st.title("App Sintonia: Readiness e Avaliações")
tab = st.tabs(["Prontidão", "Treino", "Psicoemocional"])

# --- Aba Prontidão ---
with tab[0]:
    st.header("Avaliação de Prontidão")
    hooper_fadiga = st.slider("Fadiga (1–7)", 1, 7)
    hooper_estresse = st.slider("Estresse (1–7)", 1, 7)
    hooper_doms = st.slider("DOMS (1–7)", 1, 7)
    hooper_sono = st.slider("Sono (1–7)", 1, 7)
    hooper_total = hooper_fadiga + hooper_estresse + hooper_doms + hooper_sono

    tqr = st.slider("TQR (6–20)", 6, 20)
    nprs = st.slider("NPRS (0–10)", 0, 10)

    ctl = st.number_input("CTL do dia anterior", value=0.0)
    atl = st.number_input("ATL do dia anterior", value=0.0)

    if st.button("Calcular Prontidão"):
        readiness = compute_readiness(ctl, atl, hooper_total, tqr, nprs)
        st.metric("Readiness", f"{readiness:.2f}")
        supabase.table("readiness_assessments").insert({
            "hooper": hooper_total,
            "tqr": tqr,
            "nprs": nprs,
            "ctl": ctl,
            "atl": atl,
            "readiness": readiness
        }).execute()

# --- Aba Treino ---
with tab[1]:
    st.header("Estado de Treino")
    rpe = st.slider("PSE (0–10)", 0.0, 10.0)
    duration = st.number_input("Duração do treino (min)", value=30)
    trimp = compute_trimp(rpe, duration)
    st.metric("TRIMP", f"{trimp:.2f}")

    injury_risk = trimp * (hooper_total / 28)
    st.metric("Risco de Lesão", f"{injury_risk:.2f}")

    if st.button("Salvar Treino"):
        supabase.table("training_assessments").insert({
            "rpe": rpe,
            "duration": duration,
            "trimp": trimp,
            "injury_risk": injury_risk
        }).execute()

# --- Aba Psicoemocional ---
with tab[2]:
    st.header("Avaliação Psicoemocional")
    st.markdown("**DASS-21**")
    anxiety = st.slider("Ansiedade (0–21)", 0, 21)
    depression = st.slider("Depressão (0–21)", 0, 21)
    stress = st.slider("Estresse (0–21)", 0, 21)

    st.markdown("**PSS-10**")
    pss = st.slider("Score PSS-10 (0–40)", 0, 40)

    st.markdown("**FANTASTIC**")
    fantastic = st.number_input("Score FANTASTIC (0–100)", value=0)

    if st.button("Salvar Psicoemocional"):
        supabase.table("psychological_assessments").insert({
            "dass_anxiety": anxiety,
            "dass_depression": depression,
            "dass_stress": stress,
            "pss": pss,
            "fantastic": fantastic
        }).execute()
        st.success("Avaliação psicoemocional salva com sucesso.")
