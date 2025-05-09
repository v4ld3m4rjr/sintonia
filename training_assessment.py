import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Importar função do supabase do app.py
from app import init_supabase, get_user_training_assessments, get_user_assessments

def calculate_trimp(duration, rpe):
    """
    Calcula TRIMP (Training Impulse) pelo método Session-RPE
    TRIMP = duração (minutos) * RPE (0-10)
    """
    return duration * rpe

def calculate_injury_risk(trimp, readiness, acute_load, chronic_load):
    """
    Calcula risco de lesão baseado em:
    - Carga de treino atual (TRIMP)
    - Estado de prontidão
    - Relação aguda:crônica (ACWR)
    """
    # Normalizar readiness para 0-1
    readiness_factor = readiness / 100
    
    # Calcular ACWR
    if chronic_load == 0:
        acwr = 1.0  # Valor neutro se não houver carga crônica
    else:
        acwr = acute_load / chronic_load
    
    # Risco base pelo ACWR
    if acwr < 0.8:
        base_risk = 0.4  # Risco moderado-baixo por subcarga
    elif 0.8 <= acwr <= 1.3:
        base_risk = 0.2  # Risco baixo - zona ideal
    elif 1.3 < acwr <= 1.5:
        base_risk = 0.6  # Risco moderado-alto
    else:
        base_risk = 0.8  # Risco alto
    
    # Ajustar risco pela prontidão e carga atual
    trimp_factor = min(trimp / 1000, 0.5)  # TRIMP normalizado, máximo 0.5
    
    final_risk = (base_risk + trimp_factor) * (2 - readiness_factor)
    
    # Garantir que o risco esteja entre 0 e 100%
    return min(max(final_risk * 100, 0), 100)

def calculate_load_metrics(training_loads, days=7):
    """
    Calcula métricas de carga de treino:
    - Carga aguda (7 dias)
    - Carga crônica (28 dias)
    - ACWR (Acute:Chronic Workload Ratio)
    - Monotonia
    - Strain
    """
    if not training_loads or len(training_loads) < days:
        return None, None, None, None, None
    
    # Extrair valores de carga
    loads = [session['training_load'] for session in training_loads]
    
    # Carga aguda (últimos 7 dias)
    acute_load = sum(loads[-7:]) if len(loads) >= 7 else sum(loads)
    
    # Carga crônica (últimos 28 dias)
    chronic_load = sum(loads[-28:]) / 4 if len(loads) >= 28 else sum(loads) / max(1, len(loads) / 7)
    
    # ACWR
    acwr = acute_load / chronic_load if chronic_load > 0 else 0
    
    # Calcular monotonia (últimos 7 dias)
    recent_loads = loads[-7:] if len(loads) >= 7 else loads
    mean_load = np.mean(recent_loads)
    sd_load = np.std(recent_loads)
    monotony = mean_load / sd_load if sd_load > 0 else 0
    
    # Calcular strain
    strain = acute_load * monotony
    
    return acute_load, chronic_load, acwr, monotony, strain

def show_training_assessment():
    st.header("Avaliação do Estado de Treino")
    st.markdown("""
    Esta avaliação utiliza métricas validadas cientificamente para monitorar seu treino:
    * **TRIMP (Training Impulse)**: Quantifica a carga de treino
    * **ACWR (Acute:Chronic Workload Ratio)**: Relação entre carga aguda e crônica
    * **Monotonia e Strain**: Avaliam variabilidade e esforço acumulado
    * **Risco de Lesão**: Estimativa baseada em fatores combinados
    """)
    
    # Variáveis de entrada
    st.subheader("Detalhes do Treino")
    col1, col2 = st.columns(2)
    
    with col1:
        duration = st.number_input("Duração do treino (minutos)", min_value=0, value=60)
        heart_rate = st.number_input("Frequência cardíaca média (bpm)", min_value=0, value=140)
    
    with col2:
        rpe = st.slider("Percepção de Esforço (RPE 0-10)", 0.0, 10.0, 5.0, 0.5, 
                        help="0 = Repouso, 10 = Esforço máximo")
        notes = st.text_area("Observações do treino", height=100)
    
    # Calcular TRIMP
    trimp = calculate_trimp(duration, rpe)
    training_load = trimp  # Neste caso, usamos TRIMP como carga de treino
    
    # Mostrar métricas do treino atual
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("TRIMP", f"{trimp:.1f}")
        st.info("TRIMP (Training Impulse) é uma métrica que quantifica a carga interna de treino, combinando duração e intensidade.")
    
    # Buscar dados de prontidão recentes
    readiness = 70  # Valor padrão
    
    if st.session_state.get('user_id'):
        readiness_data = get_user_assessments(st.session_state.user_id, days=1)
        if readiness_data:
            readiness = readiness_data[-1].get('readiness', 70)
    
    # Buscar histórico de treino
    training_history = []
    acute_load, chronic_load, acwr, monotony, strain = None, None, None, None, None
    
    if st.session_state.get('user_id'):
        training_history = get_user_training_assessments(st.session_state.user_id, days=28)
        if training_history:
            acute_load, chronic_load, acwr, monotony, strain = calculate_load_metrics(training_history)
    
    # Calcular risco de lesão
    injury_risk = calculate_injury_risk(
        trimp, 
        readiness, 
        acute_load if acute_load else trimp, 
        chronic_load if chronic_load else trimp/2
    )
    
    with col2:
        st.metric("Risco de Lesão", f"{injury_risk:.1f}%")
        
        # Interpretação do risco
        if injury_risk < 30:
            st.success("Risco Baixo")
        elif injury_risk < 60:
            st.warning("Risco Moderado - Monitore sintomas")
        else:
            st.error("Risco Alto - Considere reduzir carga")
    
    # Métricas de carga (se disponíveis)
    if acute_load and chronic_load:
        st.subheader("Métricas de Carga")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Carga Aguda (7 dias)", f"{acute_load:.1f}")
        
        with col2:
            st.metric("Carga Crônica (28 dias)", f"{chronic_load:.1f}")
        
        with col3:
            st.metric("ACWR", f"{acwr:.2f}")
            
            # Interpretação do ACWR
            if acwr < 0.8:
                st.info("Subcarga relativa")
            elif 0.8 <= acwr <= 1.3:
                st.success("Zona ideal")
            elif 1.3 < acwr <= 1.5:
                st.warning("Sobrecarga moderada")
            else:
                st.error("Sobrecarga elevada")
    
    # Visualização do histórico
    if training_history:
        st.subheader("Histórico de Treino (7 dias)")
        
        # Preparar dados
        df = pd.DataFrame(training_history[-7:])
        df['created_at'] = pd.to_datetime(df['created_at'])
        
        # Gráfico de carga
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(df['created_at'], df['training_load'], alpha=0.7, label='Carga Diária')
        
        # Linha para ACWR
        if acwr:
            ax2 = ax.twinx()
            ax2.axhline(y=0.8, color='g', linestyle='--', alpha=0.5)
            ax2.axhline(y=1.3, color='g', linestyle='--', alpha=0.5)
            ax2.axhline(y=1.5, color='r', linestyle='--', alpha=0.5)
            ax2.set_ylabel('ACWR')
            ax2.set_ylim(0, 2)
        
        ax.set_title('Histórico de Carga de Treino')
        ax.set_ylabel('Carga de Treino (TRIMP)')
        ax.set_xlabel('Data')
        ax.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        st.pyplot(fig)
        
        # Gráfico de radar para métricas atuais
        if monotony and strain:
            st.subheader("Perfil de Treino Atual")
            
            # Normalizar valores para radar
            norm_acwr = min(acwr / 2, 1)  # ACWR 0-2 normalizado para 0-1
            norm_monotony = min(monotony / 2, 1)  # Monotonia 0-2 normalizado para 0-1
            norm_strain = min(strain / (acute_load * 2), 1)  # Strain normalizado
            norm_risk = injury_risk / 100  # Risco já está em 0-100
            
            # Dados para radar
            categories = ['ACWR', 'Monotonia', 'Strain', 'Risco']
            values = [norm_acwr, norm_monotony, norm_strain, norm_risk]
            
            # Criar radar
            fig = plt.figure(figsize=(8, 8))
            ax = fig.add_subplot(111, polar=True)
            
            # Ângulos para cada eixo
            angles = np.linspace(0, 2*np.pi, len(categories), endpoint=False).tolist()
            values = values + [values[0]]  # Fechar o gráfico
            angles = angles + [angles[0]]  # Fechar o gráfico
            
            # Plotar dados e preencher
            ax.plot(angles, values, 'o-', linewidth=2)
            ax.fill(angles, values, alpha=0.25)
            
            # Configurar labels
            ax.set_thetagrids(np.degrees(angles[:-1]), categories)
            
            # Ajustar limites e título
            ax.set_ylim(0, 1)
            plt.title('Perfil de Métricas de Treino', size=15, y=1.1)
            
            st.pyplot(fig)
    
    # Botão para salvar
    if st.button("Salvar Treino"):
        if not st.session_state.get('user_id'):
            st.error("Faça login para salvar treinos")
            return
            
        supabase = init_supabase()
        if not supabase:
            return
            
        try:
            training_data = {
                "user_id": st.session_state.user_id,
                "duration": duration,
                "rpe": rpe,
                "heart_rate": heart_rate,
                "trimp": trimp,
                "training_load": training_load,
                "injury_risk": injury_risk,
                "notes": notes
            }
            
            # Adicionar métricas avançadas se disponíveis
            if acute_load:
                training_data["acute_load"] = acute_load
            if chronic_load:
                training_data["chronic_load"] = chronic_load
            if acwr:
                training_data["acwr"] = acwr
            if monotony:
                training_data["monotony"] = monotony
            if strain:
                training_data["strain"] = strain
            
            response = supabase.table("training_assessments").insert(training_data).execute()
            
            if response.data:
                st.success("Treino salvo com sucesso!")
                
                # Atualizar histórico na sessão
                new_entry = {
                    "id": response.data[0]['id'],
                    "date": datetime.now(),
                    "training_load": training_load,
                    "trimp": trimp,
                    "rpe": rpe,
                    "duration": duration,
                    "injury_risk": injury_risk
                }
                
                if 'training_history' not in st.session_state:
                    st.session_state.training_history = []
                    
                st.session_state.training_history.append(new_entry)
            else:
                st.error("Erro ao salvar treino")
        except Exception as e:
            st.error(f"Erro: {str(e)}")