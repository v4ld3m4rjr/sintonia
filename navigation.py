"""
Componentes de navegação para o Sistema de Monitoramento do Atleta
-----------------------------------------------------------------
Este módulo contém funções para criar elementos de navegação como sidebar e menus.
"""

import streamlit as st
from utils.auth import logout_user

def create_sidebar():
    """
    Cria a barra lateral de navegação com links para todas as páginas.
    """
    with st.sidebar:
        st.title("🏃 Monitoramento")
        
        # Informações do usuário
        if 'user_name' in st.session_state:
            st.write(f"Olá, **{st.session_state.user_name}**!")
        
        st.markdown("---")
        
        # Links de navegação
        st.subheader("Módulos")
        
        # Dashboard (página inicial)
        if st.sidebar.button("📊 Dashboard", use_container_width=True):
            st.switch_page("app.py")
        
        # Prontidão
        if st.sidebar.button("🔋 Prontidão", use_container_width=True):
            st.switch_page("pages/1_Prontidao.py")
        
        # Treino
        if st.sidebar.button("🏋️ Treino", use_container_width=True):
            st.switch_page("pages/2_Treino.py")
        
        # Psicológico
        if st.sidebar.button("🧠 Psicológico", use_container_width=True):
            st.switch_page("pages/3_Psicologico.py")
        
        # Dashboard Avançado
        if st.sidebar.button("📈 Dashboard Avançado", use_container_width=True):
            st.switch_page("pages/4_Dashboard.py")
        
        # Relatórios
        if st.sidebar.button("📝 Relatórios", use_container_width=True):
            st.switch_page("pages/5_Relatorios.py")
        
        # Configurações
        if st.sidebar.button("⚙️ Configurações", use_container_width=True):
            st.switch_page("pages/6_Configuracoes.py")
        
        st.markdown("---")
        
        # Botão de logout
        if st.sidebar.button("🚪 Sair", use_container_width=True):
            logout_user()
            st.rerun()
        
        # Rodapé
        st.markdown("---")
        st.caption("© 2025 Sistema de Monitoramento do Atleta")

def create_tabs(tab_names):
    """
    Cria um conjunto de abas para navegação dentro de uma página.
    
    Args:
        tab_names (list): Lista de nomes das abas
    
    Returns:
        list: Lista de objetos de aba do Streamlit
    """
    return st.tabs(tab_names)

def create_breadcrumbs(path_items):
    """
    Cria uma trilha de navegação (breadcrumbs) para mostrar a localização atual.
    
    Args:
        path_items (list): Lista de itens do caminho
    """
    breadcrumb_html = """
    <style>
    .breadcrumb {
        display: flex;
        flex-wrap: wrap;
        list-style: none;
        margin: 0;
        padding: 0;
        font-size: 14px;
        margin-bottom: 15px;
    }
    .breadcrumb-item {
        color: #1E88E5;
        margin-right: 5px;
    }
    .breadcrumb-separator {
        color: #9E9E9E;
        margin: 0 5px;
    }
    .breadcrumb-active {
        color: #424242;
        font-weight: 500;
    }
    </style>
    <div class="breadcrumb">
    """
    
    for i, item in enumerate(path_items):
        if i == len(path_items) - 1:
            # Último item (ativo)
            breadcrumb_html += f'<div class="breadcrumb-active">{item}</div>'
        else:
            # Itens anteriores
            breadcrumb_html += f'<div class="breadcrumb-item">{item}</div>'
            breadcrumb_html += '<div class="breadcrumb-separator">›</div>'
    
    breadcrumb_html += "</div>"
    
    st.markdown(breadcrumb_html, unsafe_allow_html=True)

def create_section_header(title, description="", icon=""):
    """
    Cria um cabeçalho de seção com título, descrição e ícone opcional.
    
    Args:
        title (str): Título da seção
        description (str): Descrição da seção
        icon (str): Ícone para a seção
    """
    header_html = f"""
    <style>
    .section-header {{
        margin-bottom: 20px;
    }}
    .section-title {{
        font-size: 24px;
        font-weight: 600;
        color: #1E88E5;
        margin-bottom: 5px;
        display: flex;
        align-items: center;
    }}
    .section-icon {{
        margin-right: 10px;
        font-size: 28px;
    }}
    .section-description {{
        color: #616161;
        font-size: 16px;
        margin-top: 5px;
    }}
    </style>
    <div class="section-header">
        <div class="section-title">
    """
    
    if icon:
        header_html += f'<span class="section-icon">{icon}</span>'
    
    header_html += f"""
        {title}
        </div>
    """
    
    if description:
        header_html += f'<div class="section-description">{description}</div>'
    
    header_html += "</div>"
    
    st.markdown(header_html, unsafe_allow_html=True)

def create_action_buttons(actions):
    """
    Cria um conjunto de botões de ação.
    
    Args:
        actions (list): Lista de dicionários com 'label', 'icon' e 'action'
    """
    cols = st.columns(len(actions))
    
    for i, action in enumerate(actions):
        with cols[i]:
            if st.button(f"{action.get('icon', '')} {action['label']}", use_container_width=True):
                action['action']()

def create_page_navigation(current_page, total_pages, on_previous, on_next):
    """
    Cria controles de navegação de página para listas paginadas.
    
    Args:
        current_page (int): Página atual
        total_pages (int): Total de páginas
        on_previous (function): Função a ser chamada ao clicar em anterior
        on_next (function): Função a ser chamada ao clicar em próximo
    """
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        if current_page > 1:
            if st.button("← Anterior", use_container_width=True):
                on_previous()
    
    with col2:
        st.markdown(f"<div style='text-align: center; color: #616161;'>Página {current_page} de {total_pages}</div>", unsafe_allow_html=True)
    
    with col3:
        if current_page < total_pages:
            if st.button("Próximo →", use_container_width=True):
                on_next()
