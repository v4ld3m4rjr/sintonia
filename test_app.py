import streamlit as st

st.title("Teste de Conexão")

st.write("Este é um aplicativo de teste simples.")

try:
    # Tente acessar os segredos
    if "SUPABASE_URL" in st.secrets:
        url = st.secrets["SUPABASE_URL"]
        st.success("URL do Supabase configurada corretamente!")
    else:
        st.error("URL do Supabase não encontrada nos segredos.")

    if "SUPABASE_KEY" in st.secrets:
        st.success("Chave do Supabase configurada corretamente!")
    else:
        st.error("Chave do Supabase não encontrada nos segredos.")

except Exception as e:
    st.error(f"Erro ao acessar segredos: {e}")

st.write("Se você está vendo esta mensagem, o aplicativo está funcionando!")
