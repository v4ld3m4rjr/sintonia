import streamlit as st

def main():
    st.title("Sistema de Monitoramento do Atleta")
    st.sidebar.title("Autenticação")
    menu = ["Login", "Registro", "Redefinição de senha"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Login":
        st.subheader("Login")
        # Login form here
    elif choice == "Registro":
        st.subheader("Registro")
        # Registration form here
    elif choice == "Redefinição de senha":
        st.subheader("Redefinição de senha")
        # Password reset form here

    st.header("Dashboard Principal")
    st.write("Resumo de métricas, gráfico de tendências e acesso rápido a módulos")

if __name__ == "__main__":
    main()
