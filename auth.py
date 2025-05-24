"""
Módulo de autenticação para o Sistema de Monitoramento do Atleta
----------------------------------------------------------------
Este módulo contém funções para autenticação de usuários, incluindo:
- Verificação de autenticação
- Login de usuários
- Criação de contas
- Recuperação de senha
"""

import streamlit as st
import hashlib
import os
from datetime import datetime
from utils.database import get_supabase_client

def check_authentication():
    """
    Verifica se o usuário está autenticado na sessão atual.
    
    Returns:
        bool: True se o usuário estiver autenticado, False caso contrário.
    """
    # Verifica se as informações de usuário existem na sessão
    if 'authenticated' in st.session_state and st.session_state.authenticated:
        if 'user_id' in st.session_state and 'user_name' in st.session_state:
            return True
    return False

def login_user(email, password):
    """
    Autentica um usuário com email e senha.
    
    Args:
        email (str): Email do usuário
        password (str): Senha do usuário
    
    Returns:
        bool: True se o login for bem-sucedido, False caso contrário.
    """
    if not email or not password:
        return False
    
    # Hash da senha para comparação com o banco
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    # Obtém o cliente Supabase
    supabase = get_supabase_client()
    
    try:
        # Consulta o usuário no banco de dados
        response = supabase.table('athlete_users').select('*').eq('email', email).execute()
        
        # Verifica se encontrou o usuário e se a senha está correta
        if response.data and len(response.data) > 0:
            user = response.data[0]
            if user['password_hash'] == hashed_password:
                # Armazena as informações do usuário na sessão
                st.session_state.authenticated = True
                st.session_state.user_id = user['id']
                st.session_state.user_name = user['name']
                st.session_state.user_email = user['email']
                
                # Atualiza a data do último login
                supabase.table('athlete_users').update({
                    'last_login': datetime.now().isoformat()
                }).eq('id', user['id']).execute()
                
                return True
        
        return False
    
    except Exception as e:
        st.error(f"Erro ao fazer login: {str(e)}")
        return False

def create_account(name, email, password):
    """
    Cria uma nova conta de usuário.
    
    Args:
        name (str): Nome completo do usuário
        email (str): Email do usuário
        password (str): Senha do usuário
    
    Returns:
        bool: True se a conta for criada com sucesso, False caso contrário.
    """
    if not name or not email or not password:
        return False
    
    # Hash da senha para armazenamento seguro
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    # Obtém o cliente Supabase
    supabase = get_supabase_client()
    
    try:
        # Verifica se o email já está em uso
        response = supabase.table('athlete_users').select('id').eq('email', email).execute()
        if response.data and len(response.data) > 0:
            st.error("Este email já está em uso.")
            return False
        
        # Cria o novo usuário
        response = supabase.table('athlete_users').insert({
            'name': name,
            'email': email,
            'password_hash': hashed_password,
            'created_at': datetime.now().isoformat()
        }).execute()
        
        if response.data and len(response.data) > 0:
            return True
        
        return False
    
    except Exception as e:
        st.error(f"Erro ao criar conta: {str(e)}")
        return False

def reset_password(email):
    """
    Inicia o processo de recuperação de senha para um usuário.
    
    Args:
        email (str): Email do usuário
    
    Returns:
        bool: True se o processo for iniciado com sucesso, False caso contrário.
    """
    if not email:
        return False
    
    # Obtém o cliente Supabase
    supabase = get_supabase_client()
    
    try:
        # Verifica se o email existe
        response = supabase.table('athlete_users').select('id').eq('email', email).execute()
        
        if response.data and len(response.data) > 0:
            # Em uma implementação real, aqui seria enviado um email com link de recuperação
            # Para este protótipo, apenas simulamos o sucesso
            return True
        
        return False
    
    except Exception as e:
        st.error(f"Erro ao processar recuperação de senha: {str(e)}")
        return False

def logout_user():
    """
    Encerra a sessão do usuário atual.
    
    Returns:
        bool: True se o logout for bem-sucedido.
    """
    # Remove as informações de autenticação da sessão
    if 'authenticated' in st.session_state:
        st.session_state.authenticated = False
    
    if 'user_id' in st.session_state:
        del st.session_state.user_id
    
    if 'user_name' in st.session_state:
        del st.session_state.user_name
    
    if 'user_email' in st.session_state:
        del st.session_state.user_email
    
    return True

def change_password(user_id, current_password, new_password):
    """
    Altera a senha de um usuário.
    
    Args:
        user_id (str): ID do usuário
        current_password (str): Senha atual
        new_password (str): Nova senha
    
    Returns:
        bool: True se a senha for alterada com sucesso, False caso contrário.
    """
    if not user_id or not current_password or not new_password:
        return False
    
    # Hash das senhas
    hashed_current = hashlib.sha256(current_password.encode()).hexdigest()
    hashed_new = hashlib.sha256(new_password.encode()).hexdigest()
    
    # Obtém o cliente Supabase
    supabase = get_supabase_client()
    
    try:
        # Verifica se a senha atual está correta
        response = supabase.table('athlete_users').select('id').eq('id', user_id).eq('password_hash', hashed_current).execute()
        
        if response.data and len(response.data) > 0:
            # Atualiza a senha
            supabase.table('athlete_users').update({
                'password_hash': hashed_new,
                'updated_at': datetime.now().isoformat()
            }).eq('id', user_id).execute()
            
            return True
        
        return False
    
    except Exception as e:
        st.error(f"Erro ao alterar senha: {str(e)}")
        return False
