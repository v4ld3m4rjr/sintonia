"""
Módulo de Configurações para o Sistema de Monitoramento do Atleta
-----------------------------------------------------------
Este módulo permite ao atleta personalizar o sistema e gerenciar suas configurações.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
from PIL import Image
import json

# Adiciona os diretórios ao path para importação dos módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importa os módulos de utilidades
from utils.auth import check_authentication, update_user_info
from utils.database import get_user_settings, save_user_settings

# Importa os componentes reutilizáveis
from components.cards import metric_card, info_card
from components.navigation import create_sidebar, create_tabs, create_breadcrumbs, create_section_header

# Configuração da página
st.set_page_config(
    page_title="Configurações - Sistema de Monitoramento do Atleta",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Verifica autenticação
if not check_authentication():
    st.switch_page("app.py")

# Cria a barra lateral
create_sidebar()

# Título da página
st.title("⚙️ Configurações")
create_breadcrumbs(["Dashboard", "Configurações"])

# Função para carregar as configurações do usuário
def load_user_settings():
    """
    Carrega as configurações do usuário do banco de dados.
    
    Returns:
        dict: Configurações do usuário
    """
    settings = get_user_settings(st.session_state.user_id)
    
    # Configurações padrão
    default_settings = {
        "profile": {
            "name": "",
            "age": 30,
            "gender": "Masculino",
            "weight": 70,
            "height": 170,
            "sport": "Corrida",
            "level": "Intermediário"
        },
        "app": {
            "theme": "default",
            "dashboard_metrics": ["prontidão", "trimp", "sono", "humor"],
            "show_recommendations": True,
            "show_faixas_normalidade": True,
            "default_period": "30"
        },
        "training": {
            "default_training_types": ["Corrida", "Musculação", "Natação", "Ciclismo", "Funcional", "Outro"],
            "use_borg_scale": True,
            "use_tss": True,
            "use_monotony_strain": True
        },
        "notifications": {
            "enable_reminders": True,
            "reminder_time": "20:00",
            "reminder_days": ["Segunda", "Quarta", "Sexta"]
        },
        "data": {
            "auto_backup": False,
            "backup_frequency": "Semanal",
            "last_backup": None
        }
    }
    
    # Se não houver configurações, usa as padrão
    if not settings:
        return default_settings
    
    # Mescla as configurações existentes com as padrão
    for category in default_settings:
        if category not in settings:
            settings[category] = default_settings[category]
        else:
            for key in default_settings[category]:
                if key not in settings[category]:
                    settings[category][key] = default_settings[category][key]
    
    return settings

# Função para salvar as configurações do usuário
def save_user_settings_to_db(settings):
    """
    Salva as configurações do usuário no banco de dados.
    
    Args:
        settings (dict): Configurações do usuário
    
    Returns:
        bool: True se salvo com sucesso, False caso contrário
    """
    return save_user_settings(st.session_state.user_id, settings)

# Função para exibir configurações de perfil
def show_profile_settings(settings):
    """
    Exibe e permite editar as configurações de perfil do usuário.
    
    Args:
        settings (dict): Configurações do usuário
    
    Returns:
        dict: Configurações atualizadas
    """
    create_section_header(
        "Perfil do Atleta", 
        "Atualize suas informações pessoais e esportivas.",
        "👤"
    )
    
    profile = settings["profile"]
    
    col1, col2 = st.columns(2)
    
    with col1:
        profile["name"] = st.text_input("Nome", profile["name"])
        profile["age"] = st.number_input("Idade", min_value=10, max_value=100, value=profile["age"])
        profile["gender"] = st.selectbox(
            "Gênero", 
            ["Masculino", "Feminino", "Outro"],
            index=["Masculino", "Feminino", "Outro"].index(profile["gender"]) if profile["gender"] in ["Masculino", "Feminino", "Outro"] else 0
        )
    
    with col2:
        profile["weight"] = st.number_input("Peso (kg)", min_value=30.0, max_value=200.0, value=float(profile["weight"]), step=0.1, format="%.1f")
        profile["height"] = st.number_input("Altura (cm)", min_value=100, max_value=250, value=profile["height"])
        profile["sport"] = st.text_input("Esporte Principal", profile["sport"])
        profile["level"] = st.selectbox(
            "Nível", 
            ["Iniciante", "Intermediário", "Avançado", "Elite"],
            index=["Iniciante", "Intermediário", "Avançado", "Elite"].index(profile["level"]) if profile["level"] in ["Iniciante", "Intermediário", "Avançado", "Elite"] else 1
        )
    
    # Atualiza as configurações
    settings["profile"] = profile
    
    return settings

# Função para exibir configurações do aplicativo
def show_app_settings(settings):
    """
    Exibe e permite editar as configurações do aplicativo.
    
    Args:
        settings (dict): Configurações do usuário
    
    Returns:
        dict: Configurações atualizadas
    """
    create_section_header(
        "Configurações do Aplicativo", 
        "Personalize a aparência e funcionalidades do sistema.",
        "🎨"
    )
    
    app = settings["app"]
    
    col1, col2 = st.columns(2)
    
    with col1:
        app["theme"] = st.selectbox(
            "Tema",
            ["default", "dark", "light", "blue", "green"],
            index=["default", "dark", "light", "blue", "green"].index(app["theme"]) if app["theme"] in ["default", "dark", "light", "blue", "green"] else 0,
            format_func=lambda x: {
                "default": "Padrão (Azul Tecnológico)",
                "dark": "Escuro",
                "light": "Claro",
                "blue": "Azul",
                "green": "Verde"
            }.get(x, x.capitalize())
        )
        
        app["default_period"] = st.selectbox(
            "Período Padrão para Gráficos",
            ["7", "15", "30", "60", "90"],
            index=["7", "15", "30", "60", "90"].index(app["default_period"]) if app["default_period"] in ["7", "15", "30", "60", "90"] else 2,
            format_func=lambda x: f"{x} dias"
        )
    
    with col2:
        app["show_recommendations"] = st.checkbox("Mostrar Recomendações", app["show_recommendations"])
        app["show_faixas_normalidade"] = st.checkbox("Mostrar Faixas de Normalidade nos Gráficos", app["show_faixas_normalidade"])
    
    st.subheader("Métricas do Dashboard")
    st.caption("Selecione as métricas que deseja exibir no dashboard principal")
    
    all_metrics = [
        "prontidão", "trimp", "sono", "humor", "estresse", 
        "ctl", "atl", "tsb", "monotonia", "strain", 
        "ansiedade", "depressão", "motivação", "energia"
    ]
    
    # Organiza as métricas em 3 colunas
    cols = st.columns(3)
    selected_metrics = []
    
    for i, metric in enumerate(all_metrics):
        col_idx = i % 3
        with cols[col_idx]:
            is_selected = metric in app["dashboard_metrics"]
            if st.checkbox(metric.capitalize(), value=is_selected, key=f"metric_{metric}"):
                selected_metrics.append(metric)
    
    app["dashboard_metrics"] = selected_metrics
    
    # Atualiza as configurações
    settings["app"] = app
    
    return settings

# Função para exibir configurações de treino
def show_training_settings(settings):
    """
    Exibe e permite editar as configurações de treino.
    
    Args:
        settings (dict): Configurações do usuário
    
    Returns:
        dict: Configurações atualizadas
    """
    create_section_header(
        "Configurações de Treino", 
        "Personalize as opções relacionadas ao registro e análise de treinos.",
        "🏋️"
    )
    
    training = settings["training"]
    
    # Tipos de treino
    st.subheader("Tipos de Treino")
    st.caption("Adicione ou remova tipos de treino disponíveis no sistema")
    
    # Exibe os tipos existentes
    training_types = training["default_training_types"]
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        training_types_str = st.text_area(
            "Tipos de Treino (um por linha)",
            "\n".join(training_types),
            height=150
        )
        
        # Converte de volta para lista
        training["default_training_types"] = [t.strip() for t in training_types_str.split("\n") if t.strip()]
    
    with col2:
        st.markdown("**Exemplos:**")
        st.markdown("- Corrida")
        st.markdown("- Musculação")
        st.markdown("- Natação")
        st.markdown("- Ciclismo")
        st.markdown("- Funcional")
    
    # Configurações de métricas
    st.subheader("Métricas de Treino")
    
    col1, col2 = st.columns(2)
    
    with col1:
        training["use_borg_scale"] = st.checkbox("Usar Escala de Borg (0-10)", training["use_borg_scale"])
        training["use_tss"] = st.checkbox("Calcular TSS (Training Stress Score)", training["use_tss"])
    
    with col2:
        training["use_monotony_strain"] = st.checkbox("Calcular Monotonia e Strain", training["use_monotony_strain"])
    
    # Atualiza as configurações
    settings["training"] = training
    
    return settings

# Função para exibir configurações de notificações
def show_notification_settings(settings):
    """
    Exibe e permite editar as configurações de notificações.
    
    Args:
        settings (dict): Configurações do usuário
    
    Returns:
        dict: Configurações atualizadas
    """
    create_section_header(
        "Configurações de Notificações", 
        "Configure lembretes e notificações do sistema.",
        "🔔"
    )
    
    notifications = settings["notifications"]
    
    notifications["enable_reminders"] = st.checkbox("Ativar Lembretes", notifications["enable_reminders"])
    
    if notifications["enable_reminders"]:
        col1, col2 = st.columns(2)
        
        with col1:
            notifications["reminder_time"] = st.time_input(
                "Horário do Lembrete",
                datetime.strptime(notifications["reminder_time"], "%H:%M").time() if isinstance(notifications["reminder_time"], str) else datetime.now().time()
            ).strftime("%H:%M")
        
        with col2:
            days = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"]
            selected_days = []
            
            for day in days:
                if st.checkbox(day, day in notifications["reminder_days"], key=f"day_{day}"):
                    selected_days.append(day)
            
            notifications["reminder_days"] = selected_days
    
    # Atualiza as configurações
    settings["notifications"] = notifications
    
    return settings

# Função para exibir configurações de dados
def show_data_settings(settings):
    """
    Exibe e permite editar as configurações de dados.
    
    Args:
        settings (dict): Configurações do usuário
    
    Returns:
        dict: Configurações atualizadas
    """
    create_section_header(
        "Configurações de Dados", 
        "Gerencie seus dados e configurações de backup.",
        "💾"
    )
    
    data = settings["data"]
    
    col1, col2 = st.columns(2)
    
    with col1:
        data["auto_backup"] = st.checkbox("Backup Automático", data["auto_backup"])
        
        if data["auto_backup"]:
            data["backup_frequency"] = st.selectbox(
                "Frequência de Backup",
                ["Diário", "Semanal", "Mensal"],
                index=["Diário", "Semanal", "Mensal"].index(data["backup_frequency"]) if data["backup_frequency"] in ["Diário", "Semanal", "Mensal"] else 1
            )
    
    with col2:
        if data["last_backup"]:
            st.info(f"Último backup: {data['last_backup']}")
        else:
            st.info("Nenhum backup realizado ainda")
        
        if st.button("Fazer Backup Agora", use_container_width=True):
            # Simulação de backup
            data["last_backup"] = datetime.now().strftime("%d/%m/%Y %H:%M")
            st.success("Backup realizado com sucesso!")
    
    # Exportação de dados
    st.subheader("Exportação de Dados")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Exportar Dados de Prontidão", use_container_width=True):
            st.info("Funcionalidade disponível na página de Relatórios")
    
    with col2:
        if st.button("Exportar Dados de Treino", use_container_width=True):
            st.info("Funcionalidade disponível na página de Relatórios")
    
    with col3:
        if st.button("Exportar Dados Psicológicos", use_container_width=True):
            st.info("Funcionalidade disponível na página de Relatórios")
    
    # Exclusão de dados
    st.subheader("Exclusão de Dados")
    
    with st.expander("Excluir Dados"):
        st.warning("Atenção: A exclusão de dados é permanente e não pode ser desfeita.")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Excluir Dados de Prontidão", use_container_width=True):
                st.error("Esta ação excluirá todos os seus dados de prontidão.")
                if st.button("Confirmar Exclusão", key="confirm_readiness", use_container_width=True):
                    # Implementar exclusão
                    st.success("Dados excluídos com sucesso!")
        
        with col2:
            if st.button("Excluir Dados de Treino", use_container_width=True):
                st.error("Esta ação excluirá todos os seus dados de treino.")
                if st.button("Confirmar Exclusão", key="confirm_training", use_container_width=True):
                    # Implementar exclusão
                    st.success("Dados excluídos com sucesso!")
        
        with col3:
            if st.button("Excluir Dados Psicológicos", use_container_width=True):
                st.error("Esta ação excluirá todos os seus dados psicológicos.")
                if st.button("Confirmar Exclusão", key="confirm_psychological", use_container_width=True):
                    # Implementar exclusão
                    st.success("Dados excluídos com sucesso!")
    
    # Atualiza as configurações
    settings["data"] = data
    
    return settings

# Função para exibir configurações de conta
def show_account_settings():
    """
    Exibe e permite editar as configurações de conta do usuário.
    """
    create_section_header(
        "Configurações de Conta", 
        "Gerencie sua conta e credenciais de acesso.",
        "🔒"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        email = st.text_input("E-mail", st.session_state.get("user_email", ""))
    
    with col2:
        st.text_input("Senha Atual", type="password")
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_password = st.text_input("Nova Senha", type="password")
    
    with col2:
        confirm_password = st.text_input("Confirmar Nova Senha", type="password")
    
    if st.button("Atualizar Credenciais", use_container_width=True):
        if new_password and new_password != confirm_password:
            st.error("As senhas não coincidem")
        else:
            # Implementar atualização de credenciais
            if update_user_info(st.session_state.user_id, email, new_password if new_password else None):
                st.success("Credenciais atualizadas com sucesso!")
                st.session_state.user_email = email
            else:
                st.error("Erro ao atualizar credenciais")

# Função para exibir informações do sistema
def show_system_info():
    """
    Exibe informações sobre o sistema.
    """
    create_section_header(
        "Informações do Sistema", 
        "Detalhes técnicos e versão do sistema.",
        "ℹ️"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Versão do Sistema:** 1.0.0")
        st.markdown("**Data de Lançamento:** 24/05/2025")
        st.markdown("**Desenvolvido por:** Manus AI")
    
    with col2:
        st.markdown("**Bibliotecas Principais:**")
        st.markdown("- Streamlit 1.22.0")
        st.markdown("- Plotly 5.14.1")
        st.markdown("- Pandas 2.0.1")
        st.markdown("- Supabase 1.0.3")
    
    st.markdown("**Descrição:**")
    st.markdown("""
    O Sistema de Monitoramento do Atleta é uma aplicação web desenvolvida para ajudar atletas a monitorar
    seu estado de prontidão, treinos e estado psicológico. O sistema utiliza métricas avançadas como CTL, ATL, TSB,
    Monotonia e Strain para fornecer insights valiosos sobre o estado do atleta e ajudar na tomada de decisões
    relacionadas ao treinamento.
    """)

# Função principal
def main():
    """Função principal que controla o fluxo da página."""
    # Adiciona o logo na barra lateral
    logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "images", "logo_sintonia.png")
    if os.path.exists(logo_path):
        logo = Image.open(logo_path)
        st.sidebar.image(logo, width=200)
    
    # Carrega as configurações do usuário
    settings = load_user_settings()
    
    # Cria as abas
    tabs = create_tabs([
        "Perfil", "Aplicativo", "Treino", "Notificações", "Dados", "Conta", "Sistema"
    ])
    
    # Variável para controlar se houve alterações
    settings_changed = False
    
    # Aba de Perfil
    with tabs[0]:
        settings = show_profile_settings(settings)
        settings_changed = True
    
    # Aba de Aplicativo
    with tabs[1]:
        settings = show_app_settings(settings)
        settings_changed = True
    
    # Aba de Treino
    with tabs[2]:
        settings = show_training_settings(settings)
        settings_changed = True
    
    # Aba de Notificações
    with tabs[3]:
        settings = show_notification_settings(settings)
        settings_changed = True
    
    # Aba de Dados
    with tabs[4]:
        settings = show_data_settings(settings)
        settings_changed = True
    
    # Aba de Conta
    with tabs[5]:
        show_account_settings()
    
    # Aba de Sistema
    with tabs[6]:
        show_system_info()
    
    # Botão para salvar configurações
    if settings_changed:
        st.divider()
        if st.button("Salvar Configurações", type="primary", use_container_width=True):
            if save_user_settings_to_db(settings):
                st.success("Configurações salvas com sucesso!")
            else:
                st.error("Erro ao salvar configurações")

# Executa a função principal
if __name__ == "__main__":
    main()
