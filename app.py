
import streamlit as st
import supabase
import json

# Configuração da página
st.set_page_config(
    page_title="Sintonia - Diagnóstico",
    page_icon="🧠",
    layout="wide"
)

# Função para inicializar conexão com Supabase
def init_connection():
    try:
        # Tentar obter credenciais dos secrets
        url = st.secrets.get("supabase_url", "")
        key = st.secrets.get("supabase_key", "")

        if not url or not key:
            st.warning("Credenciais do Supabase não encontradas em st.secrets")
            # Verificar variáveis de ambiente
            import os
            url = os.environ.get("SUPABASE_URL", "")
            key = os.environ.get("SUPABASE_KEY", "")

            if url and key:
                st.success("Credenciais encontradas nas variáveis de ambiente")
            else:
                st.error("Credenciais não encontradas nas variáveis de ambiente")
                return None

        client = supabase.create_client(url, key)
        return client
    except Exception as e:
        st.error(f"Erro ao conectar com Supabase: {str(e)}")
        return None

# Título da página
st.title("Diagnóstico de Conexão com Supabase")

# Testar conexão
st.subheader("1. Teste de Conexão")
supabase_client = init_connection()

if supabase_client:
    st.success("✅ Conexão com Supabase estabelecida com sucesso!")
else:
    st.error("❌ Falha na conexão com Supabase")
    st.info("Verifique se as credenciais estão configuradas corretamente em st.secrets ou variáveis de ambiente.")

# Formulário para testar login
st.subheader("2. Teste de Login")
with st.form("test_login"):
    username = st.text_input("Usuário")
    password = st.text_input("Senha", type="password")
    submit = st.form_submit_button("Testar Login")

    if submit and supabase_client:
        try:
            # Consultar usuário
            response = supabase_client.table("users").select("*").eq("username", username).execute()

            st.write("Resposta da consulta:")
            st.json(json.dumps(response.dict()))

            if response.data:
                user = response.data[0]
                if user.get("password") == password:
                    st.success(f"✅ Login bem-sucedido para o usuário: {username}")
                else:
                    st.error("❌ Senha incorreta")
            else:
                st.error(f"❌ Usuário '{username}' não encontrado")
        except Exception as e:
            st.error(f"Erro ao consultar usuário: {str(e)}")

# Listar usuários (apenas para diagnóstico)
st.subheader("3. Usuários Cadastrados")
if supabase_client:
    try:
        with st.expander("Ver usuários cadastrados"):
            response = supabase_client.table("users").select("username, email, created_at").execute()

            if response.data:
                import pandas as pd
                df = pd.DataFrame(response.data)
                st.dataframe(df)
            else:
                st.info("Nenhum usuário cadastrado")
    except Exception as e:
        st.error(f"Erro ao listar usuários: {str(e)}")

# Formulário para criar usuário de teste
st.subheader("4. Criar Usuário de Teste")
with st.form("create_test_user"):
    new_username = st.text_input("Novo Usuário")
    new_password = st.text_input("Nova Senha", type="password")
    new_email = st.text_input("Email", value="teste@example.com")
    submit = st.form_submit_button("Criar Usuário de Teste")

    if submit and supabase_client and new_username and new_password:
        try:
            # Verificar se usuário já existe
            check = supabase_client.table("users").select("username").eq("username", new_username).execute()

            if check.data:
                st.error(f"Usuário '{new_username}' já existe")
            else:
                # Criar novo usuário
                data = {
                    "username": new_username,
                    "password": new_password,
                    "email": new_email,
                    "age": 30,
                    "gender": "Não informado"
                }

                response = supabase_client.table("users").insert(data).execute()
                st.success(f"✅ Usuário de teste '{new_username}' criado com sucesso!")
                st.json(json.dumps(response.dict()))
        except Exception as e:
            st.error(f"Erro ao criar usuário: {str(e)}")
