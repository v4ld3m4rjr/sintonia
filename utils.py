import os
import sys
import streamlit as st
from datetime import datetime, timedelta
from supabase import create_client, Client

# Para suprimir avisos do Supabase
class NullWriter:
    def write(self, x): pass

# Inicialização do Supabase
def init_supabase():
    try:
        # Primeiro tenta ler do ambiente (Render), depois de st.secrets (local)
        SUPABASE_URL = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
        SUPABASE_KEY = os.getenv("SUPABASE_KEY") or st.secrets.get("SUPABASE_KEY")
        
        # Redirecionar stderr para suprimir mensagens de aviso
        old_stderr = sys.stderr
        sys.stderr = NullWriter()
        
        try:
            client = create_client(SUPABASE_URL, SUPABASE_KEY)
            # Restaurar stderr
            sys.stderr = old_stderr
            return client
        except Exception as e:
            # Restaurar stderr
            sys.stderr = old_stderr
            st.warning(f"Erro ao conectar com Supabase: {str(e)}", icon="⚠️")
            return None
    except Exception as e:
        st.warning(f"Erro ao configurar Supabase: {str(e)}", icon="⚠️")
        return None

# Funções de banco de dados
def get_user_assessments(user_id, days=30):
    try:
        supabase = init_supabase()
        if not supabase:
            return []
        start_date = (datetime.now() - timedelta(days=days)).isoformat()
        response = supabase.table('readiness_assessments')\
            .select('*')\
            .eq('user_id', user_id)\
            .gte('created_at', start_date)\
            .order('created_at', desc=False)\
            .execute()
        return response.data
    except Exception as e:
        st.error(f"Erro ao buscar avaliações: {str(e)}")
        return []

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