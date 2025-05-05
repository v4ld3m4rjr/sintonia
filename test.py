
import streamlit as st

st.title("Teste de Aplicativo")
st.write("Este é um teste básico para verificar se o Streamlit está funcionando.")

try:
    st.write("Verificando acesso aos segredos...")
    if "SUPABASE_URL" in st.secrets:
        st.success("✅ SUPABASE_URL encontrado!")
    else:
        st.error("❌ SUPABASE_URL não encontrado!")

    if "SUPABASE_KEY" in st.secrets:
        st.success("✅ SUPABASE_KEY encontrado!")
    else:
        st.error("❌ SUPABASE_KEY não encontrado!")
except Exception as e:
    st.error(f"Erro ao acessar segredos: {e}")

st.write("Verificando bibliotecas...")
try:
    import numpy
    st.success("✅ NumPy importado com sucesso!")
except:
    st.error("❌ Erro ao importar NumPy")

try:
    import pandas
    st.success("✅ Pandas importado com sucesso!")
except:
    st.error("❌ Erro ao importar Pandas")

try:
    import matplotlib.pyplot
    st.success("✅ Matplotlib importado com sucesso!")
except:
    st.error("❌ Erro ao importar Matplotlib")

try:
    from supabase import create_client
    st.success("✅ Supabase importado com sucesso!")
except Exception as e:
    st.error(f"❌ Erro ao importar Supabase: {e}")

st.success("Teste concluído!")
