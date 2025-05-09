import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Importar função do arquivo utils
from utils import init_supabase, get_user_training_assessments, get_user_assessments, save_training_assessment

def calculate_trimp(duration, rpe):
    """
    Calcula TRIMP (Training Impulse) pelo método Session-RPE
    TRIMP = duração (minutos) * RPE (0-10)
    """
    return duration * rpe

def calculate_injury_risk(trimp, readiness, acute_load, chronic_load):
    """
    Calcula risco de lesão baseado em:
    - Carga de treino atual (TRIMP)
    - Estado de prontidão
    - Relação aguda:crônica (ACWR)
    """
    # Normalizar readiness para 0-1
    readiness_factor = readiness / 100
    
    # Calcular ACWR
    if chronic_load == 0:
        acwr = 1.0  # Valor neutro se não houver carga crônica
    else:
        acwr = acute_load / chronic_load
    
    # Risco base pelo ACWR
    if acwr < 0.8:
        base_risk = 0.4  # Risco moderado-baixo por subcarga
    elif 0.8 <= acwr <= 1.3:
        base_risk = 0.2  # Risco baixo - zona ideal
    elif 1.3 < acwr <= 1.5:
        base_risk = 0.6  # Risco moderado-alto
    else:
        base_risk = 0.8  # Risco alto
    
    # Ajustar risco pela prontidão e carga atual
    trimp_factor = min(trimp / 1000, 0.5)  # TRIMP normalizado, máximo 0.5
    
    final_risk = (base_risk + trimp_factor) * (2 - readiness_factor)
    
    # Garantir que o risco esteja entre 0 e 100%
    return min(max(final_risk * 100, 0), 100)

def calculate_load_metrics(training_loads, days=7):
    """
    Calcula métricas de carga de treino:
    - Carga aguda (7 dias)
    - Carga crônica (28 dias)
    - ACWR (Acute:Chronic Workload Ratio)
    - Monotonia
    - Strain
    """
    if not training_loads or len(training_loads) < days:
        return None, None, None, None, None
    
    # Extrair valores de carga
    loads = [session['training_load'] for session in training_loads]
    
    # Carga aguda (últimos 7 dias)
    acute_load = sum(loads[-7:]) if len(loads) >= 7 else sum(loads)
    
    # Carga crônica (últimos 28 dias)
    chronic_load = sum(loads[-28:]) / 4 if len(loads) >= 28 else sum(loads) / max(1, len(loads) / 7)
    
    # ACWR
    acwr = acute_load / chronic_load if chronic_load > 0 else 0
    
    # Calcular monotonia (últimos 7 dias)
    recent_loads = loads[-7:] if len(loads) >= 7 else loads
    mean_load = np.mean(recent_loads)
    sd_load = np.std(recent_loads)
    monotony = mean_load / sd_load if sd_load > 0 else 0
    
    # Calcular strain
    strain = acute_load * monotony
    
    return acute_load, chronic_load, acwr, monotony, strain