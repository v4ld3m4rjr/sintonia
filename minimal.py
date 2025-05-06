
import streamlit as st
import os

st.title("Teste de Aplicativo")
st.write("Este é um teste básico para verificar se o Streamlit está funcionando.")

# Exibir informações sobre o ambiente
st.write(f"Python version: {os.environ.get('PYTHON_VERSION', 'Unknown')}")

# Tentar acessar variáveis de ambiente
if "SUPABASE_URL" in os.environ:
    st.success("✅ SUPABASE_URL encontrado!")
else:
    st.error("❌ SUPABASE_URL não encontrado!")

if "SUPABASE_KEY" in os.environ:
    st.success("✅ SUPABASE_KEY encontrado!")
else:
    st.error("❌ SUPABASE_KEY não encontrado!")

st.write("Verificando bibliotecas...")
try:
    import numpy
    st.success(f"✅ NumPy importado com sucesso! Versão: {numpy.__version__}")
except Exception as e:
    st.error(f"❌ Erro ao importar NumPy: {e}")

try:
    import pandas
    st.success(f"✅ Pandas importado com sucesso! Versão: {pandas.__version__}")
except Exception as e:
    st.error(f"❌ Erro ao importar Pandas: {e}")

try:
    import matplotlib
    st.success(f"✅ Matplotlib importado com sucesso! Versão: {matplotlib.__version__}")
except Exception as e:
    st.error(f"❌ Erro ao importar Matplotlib: {e}")

try:
    from supabase import create_client
    st.success("✅ Supabase importado com sucesso!")
except Exception as e:
    st.error(f"❌ Erro ao importar Supabase: {e}")

st.success("Teste concluído!")
