"""
Módulo de conexão com banco de dados para o Sistema de Monitoramento do Atleta
-----------------------------------------------------------------------------
Este módulo contém funções para conexão e interação com o banco de dados Supabase.
"""

import streamlit as st
import os
from supabase import create_client, Client
from dotenv import load_dotenv

# Carrega variáveis de ambiente se existirem
load_dotenv()

def get_supabase_client():
    """
    Obtém um cliente Supabase para interação com o banco de dados.
    
    Returns:
        Client: Cliente Supabase configurado
    """
    # Verifica se já existe um cliente na sessão
    if 'supabase' not in st.session_state:
        # Tenta obter as credenciais do ambiente ou usa valores padrão para desenvolvimento
        supabase_url = os.getenv("SUPABASE_URL", "https://sua-url-supabase.supabase.co")
        supabase_key = os.getenv("SUPABASE_KEY", "sua-chave-supabase")
        
        # Cria o cliente Supabase
        st.session_state.supabase = create_client(supabase_url, supabase_key)
    
    return st.session_state.supabase

def init_connection():
    """
    Inicializa a conexão com o banco de dados.
    
    Returns:
        Client: Cliente Supabase configurado
    """
    return get_supabase_client()

def get_user_data(user_id):
    """
    Obtém os dados de um usuário específico.
    
    Args:
        user_id (str): ID do usuário
    
    Returns:
        dict: Dados do usuário ou None se não encontrado
    """
    if not user_id:
        return None
    
    supabase = get_supabase_client()
    
    try:
        response = supabase.table('athlete_users').select('*').eq('id', user_id).execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]
        
        return None
    
    except Exception as e:
        st.error(f"Erro ao obter dados do usuário: {str(e)}")
        return None

def get_readiness_data(user_id, days=7):
    """
    Obtém os dados de prontidão de um usuário para um período específico.
    
    Args:
        user_id (str): ID do usuário
        days (int): Número de dias para buscar (padrão: 7)
    
    Returns:
        list: Lista de registros de prontidão
    """
    if not user_id:
        return []
    
    supabase = get_supabase_client()
    
    try:
        # Consulta os registros de prontidão ordenados por data
        response = supabase.table('readiness_assessment') \
            .select('*') \
            .eq('user_id', user_id) \
            .order('date', desc=True) \
            .limit(days) \
            .execute()
        
        if response.data:
            # Inverte a lista para ordem cronológica
            return list(reversed(response.data))
        
        return []
    
    except Exception as e:
        st.error(f"Erro ao obter dados de prontidão: {str(e)}")
        return []

def get_training_data(user_id, days=7):
    """
    Obtém os dados de treino de um usuário para um período específico.
    
    Args:
        user_id (str): ID do usuário
        days (int): Número de dias para buscar (padrão: 7)
    
    Returns:
        list: Lista de registros de treino
    """
    if not user_id:
        return []
    
    supabase = get_supabase_client()
    
    try:
        # Consulta os registros de treino ordenados por data
        response = supabase.table('training_assessment') \
            .select('*') \
            .eq('user_id', user_id) \
            .order('date', desc=True) \
            .limit(days) \
            .execute()
        
        if response.data:
            # Inverte a lista para ordem cronológica
            return list(reversed(response.data))
        
        return []
    
    except Exception as e:
        st.error(f"Erro ao obter dados de treino: {str(e)}")
        return []

def get_psychological_data(user_id, days=30):
    """
    Obtém os dados psicológicos de um usuário para um período específico.
    
    Args:
        user_id (str): ID do usuário
        days (int): Número de dias para buscar (padrão: 30)
    
    Returns:
        list: Lista de registros psicológicos
    """
    if not user_id:
        return []
    
    supabase = get_supabase_client()
    
    try:
        # Consulta os registros psicológicos ordenados por data
        response = supabase.table('psychological_assessment') \
            .select('*') \
            .eq('user_id', user_id) \
            .order('date', desc=True) \
            .limit(days) \
            .execute()
        
        if response.data:
            # Inverte a lista para ordem cronológica
            return list(reversed(response.data))
        
        return []
    
    except Exception as e:
        st.error(f"Erro ao obter dados psicológicos: {str(e)}")
        return []

def get_user_goals(user_id):
    """
    Obtém as metas ativas de um usuário.
    
    Args:
        user_id (str): ID do usuário
    
    Returns:
        list: Lista de metas ativas
    """
    if not user_id:
        return []
    
    supabase = get_supabase_client()
    
    try:
        # Consulta as metas ativas do usuário
        response = supabase.table('goal') \
            .select('*') \
            .eq('user_id', user_id) \
            .eq('is_achieved', False) \
            .execute()
        
        if response.data:
            return response.data
        
        return []
    
    except Exception as e:
        st.error(f"Erro ao obter metas do usuário: {str(e)}")
        return []

def save_readiness_assessment(user_id, assessment_data):
    """
    Salva uma nova avaliação de prontidão.
    
    Args:
        user_id (str): ID do usuário
        assessment_data (dict): Dados da avaliação
    
    Returns:
        bool: True se salvo com sucesso, False caso contrário
    """
    if not user_id or not assessment_data:
        return False
    
    supabase = get_supabase_client()
    
    try:
        # Adiciona o ID do usuário aos dados
        assessment_data['user_id'] = user_id
        
        # Insere o registro no banco
        response = supabase.table('readiness_assessment').insert(assessment_data).execute()
        
        if response.data:
            return True
        
        return False
    
    except Exception as e:
        st.error(f"Erro ao salvar avaliação de prontidão: {str(e)}")
        return False

def save_training_assessment(user_id, training_data):
    """
    Salva um novo registro de treino.
    
    Args:
        user_id (str): ID do usuário
        training_data (dict): Dados do treino
    
    Returns:
        bool: True se salvo com sucesso, False caso contrário
    """
    if not user_id or not training_data:
        return False
    
    supabase = get_supabase_client()
    
    try:
        # Adiciona o ID do usuário aos dados
        training_data['user_id'] = user_id
        
        # Insere o registro no banco
        response = supabase.table('training_assessment').insert(training_data).execute()
        
        if response.data:
            return True
        
        return False
    
    except Exception as e:
        st.error(f"Erro ao salvar registro de treino: {str(e)}")
        return False

def save_psychological_assessment(user_id, psychological_data):
    """
    Salva uma nova avaliação psicológica.
    
    Args:
        user_id (str): ID do usuário
        psychological_data (dict): Dados da avaliação psicológica
    
    Returns:
        bool: True se salvo com sucesso, False caso contrário
    """
    if not user_id or not psychological_data:
        return False
    
    supabase = get_supabase_client()
    
    try:
        # Adiciona o ID do usuário aos dados
        psychological_data['user_id'] = user_id
        
        # Insere o registro no banco
        response = supabase.table('psychological_assessment').insert(psychological_data).execute()
        
        if response.data:
            return True
        
        return False
    
    except Exception as e:
        st.error(f"Erro ao salvar avaliação psicológica: {str(e)}")
        return False

def save_user_goal(user_id, goal_data):
    """
    Salva uma nova meta para o usuário.
    
    Args:
        user_id (str): ID do usuário
        goal_data (dict): Dados da meta
    
    Returns:
        bool: True se salvo com sucesso, False caso contrário
    """
    if not user_id or not goal_data:
        return False
    
    supabase = get_supabase_client()
    
    try:
        # Adiciona o ID do usuário aos dados
        goal_data['user_id'] = user_id
        
        # Insere o registro no banco
        response = supabase.table('goal').insert(goal_data).execute()
        
        if response.data:
            return True
        
        return False
    
    except Exception as e:
        st.error(f"Erro ao salvar meta: {str(e)}")
        return False

def update_user_goal(goal_id, update_data):
    """
    Atualiza uma meta existente.
    
    Args:
        goal_id (str): ID da meta
        update_data (dict): Dados para atualização
    
    Returns:
        bool: True se atualizado com sucesso, False caso contrário
    """
    if not goal_id or not update_data:
        return False
    
    supabase = get_supabase_client()
    
    try:
        # Atualiza o registro no banco
        response = supabase.table('goal').update(update_data).eq('id', goal_id).execute()
        
        if response.data:
            return True
        
        return False
    
    except Exception as e:
        st.error(f"Erro ao atualizar meta: {str(e)}")
        return False
