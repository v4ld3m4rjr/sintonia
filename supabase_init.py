
def init_supabase():
    try:
        from supabase import create_client
        import streamlit as st

        # Redirecionar stderr para suprimir mensagens de aviso
        old_stderr = sys.stderr
        sys.stderr = NullWriter()

        try:
            # Obter credenciais dos secrets do Streamlit
            url = st.secrets["SUPABASE_URL"]
            key = st.secrets["SUPABASE_KEY"]

            if not url or not key:
                # Restaurar stderr
                sys.stderr = old_stderr
                st.warning("Credenciais do Supabase não encontradas. Verifique as configurações no Streamlit Cloud.", icon="⚠️")
                return None

            client = create_client(url, key)

            # Restaurar stderr
            sys.stderr = old_stderr

            return client
        except Exception as e:
            # Restaurar stderr
            sys.stderr = old_stderr
            st.warning(f"Erro ao conectar com Supabase: {str(e)[:100]}...", icon="⚠️")
            return None
    except Exception as e:
        st.warning(f"Erro ao importar biblioteca Supabase: {str(e)[:100]}...", icon="⚠️")
        return None
