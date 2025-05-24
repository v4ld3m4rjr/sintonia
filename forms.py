"""
Módulo de formulários para o Sistema de Monitoramento do Atleta
-----------------------------------------------------------
Este módulo contém funções para criação e validação de formulários.
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Funções de validação

def validate_required_fields(form_data, required_fields):
    """
    Valida campos obrigatórios em um formulário.
    
    Args:
        form_data (dict): Dicionário com dados do formulário
        required_fields (list): Lista de campos obrigatórios
    
    Returns:
        tuple: (válido, mensagem de erro)
    """
    missing_fields = []
    
    for field in required_fields:
        if field not in form_data or form_data[field] is None or form_data[field] == "":
            missing_fields.append(field)
    
    if missing_fields:
        field_names = ", ".join(missing_fields)
        return False, f"Os seguintes campos são obrigatórios: {field_names}"
    
    return True, ""

def validate_numeric_range(value, min_val=None, max_val=None, field_name=""):
    """
    Valida se um valor está dentro de um intervalo numérico.
    
    Args:
        value: Valor a ser validado
        min_val: Valor mínimo permitido
        max_val: Valor máximo permitido
        field_name: Nome do campo para mensagem de erro
    
    Returns:
        tuple: (válido, mensagem de erro)
    """
    if value is None:
        return True, ""
    
    try:
        num_value = float(value)
        
        if min_val is not None and num_value < min_val:
            return False, f"{field_name} deve ser maior ou igual a {min_val}"
        
        if max_val is not None and num_value > max_val:
            return False, f"{field_name} deve ser menor ou igual a {max_val}"
        
        return True, ""
    
    except (ValueError, TypeError):
        return False, f"{field_name} deve ser um número válido"

def validate_date_range(date_value, min_date=None, max_date=None, field_name=""):
    """
    Valida se uma data está dentro de um intervalo.
    
    Args:
        date_value: Data a ser validada
        min_date: Data mínima permitida
        max_date: Data máxima permitida
        field_name: Nome do campo para mensagem de erro
    
    Returns:
        tuple: (válido, mensagem de erro)
    """
    if date_value is None:
        return True, ""
    
    try:
        if isinstance(date_value, str):
            date_value = datetime.strptime(date_value, "%Y-%m-%d").date()
        
        if min_date is not None:
            if isinstance(min_date, str):
                min_date = datetime.strptime(min_date, "%Y-%m-%d").date()
            
            if date_value < min_date:
                return False, f"{field_name} deve ser posterior a {min_date.strftime('%d/%m/%Y')}"
        
        if max_date is not None:
            if isinstance(max_date, str):
                max_date = datetime.strptime(max_date, "%Y-%m-%d").date()
            
            if date_value > max_date:
                return False, f"{field_name} deve ser anterior a {max_date.strftime('%d/%m/%Y')}"
        
        return True, ""
    
    except (ValueError, TypeError):
        return False, f"{field_name} deve ser uma data válida"

def validate_email(email):
    """
    Valida um endereço de e-mail.
    
    Args:
        email: Endereço de e-mail a ser validado
    
    Returns:
        tuple: (válido, mensagem de erro)
    """
    if email is None or email == "":
        return True, ""
    
    import re
    
    # Padrão básico de validação de e-mail
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    
    if re.match(pattern, email):
        return True, ""
    else:
        return False, "Endereço de e-mail inválido"

def validate_password_strength(password):
    """
    Valida a força de uma senha.
    
    Args:
        password: Senha a ser validada
    
    Returns:
        tuple: (válido, mensagem de erro, pontuação)
    """
    if password is None or password == "":
        return False, "Senha não pode estar vazia", 0
    
    import re
    
    # Critérios de validação
    length_ok = len(password) >= 8
    has_upper = bool(re.search(r'[A-Z]', password))
    has_lower = bool(re.search(r'[a-z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
    
    # Pontuação de força (0-100)
    score = 0
    if length_ok:
        score += 25
    if has_upper:
        score += 15
    if has_lower:
        score += 15
    if has_digit:
        score += 20
    if has_special:
        score += 25
    
    # Mensagens de erro
    errors = []
    if not length_ok:
        errors.append("pelo menos 8 caracteres")
    if not has_upper:
        errors.append("pelo menos uma letra maiúscula")
    if not has_lower:
        errors.append("pelo menos uma letra minúscula")
    if not has_digit:
        errors.append("pelo menos um número")
    if not has_special:
        errors.append("pelo menos um caractere especial")
    
    if errors:
        error_msg = "A senha deve conter: " + ", ".join(errors)
        return score >= 70, error_msg, score
    
    return True, "", score

# Funções de formulários

def create_readiness_form():
    """
    Cria um formulário de avaliação de prontidão.
    
    Returns:
        dict: Dados do formulário
    """
    with st.form("readiness_form"):
        st.subheader("Nova Avaliação de Prontidão")
        
        col1, col2 = st.columns(2)
        
        with col1:
            date = st.date_input("Data", datetime.now().date())
            
            sleep_quality = st.slider(
                "Qualidade do Sono (1-5)",
                min_value=1,
                max_value=5,
                value=3,
                help="1 = Muito ruim, 5 = Excelente"
            )
            
            # Descrição dinâmica da qualidade do sono
            sleep_quality_descriptions = {
                1: "Muito ruim - Sono extremamente fragmentado, insônia severa",
                2: "Ruim - Dificuldade para dormir, despertares frequentes",
                3: "Regular - Sono razoável com alguns despertares",
                4: "Bom - Sono contínuo com poucos despertares",
                5: "Excelente - Sono profundo e reparador"
            }
            st.caption(sleep_quality_descriptions[sleep_quality])
            
            sleep_duration = st.number_input(
                "Duração do Sono (horas)",
                min_value=0.0,
                max_value=12.0,
                value=7.0,
                step=0.5,
                help="Duração total do sono em horas"
            )
            
            # Descrição dinâmica da duração do sono
            if sleep_duration < 5:
                st.caption(f"Insuficiente - {sleep_duration} horas")
            elif sleep_duration < 6:
                st.caption(f"Baixo - {sleep_duration} horas")
            elif sleep_duration < 7:
                st.caption(f"Moderado - {sleep_duration} horas")
            elif sleep_duration < 8:
                st.caption(f"Adequado - {sleep_duration} horas")
            else:
                st.caption(f"Excelente - {sleep_duration} horas")
            
            stress = st.slider(
                "Estresse (1-5)",
                min_value=1,
                max_value=5,
                value=3,
                help="1 = Muito baixo, 5 = Muito alto"
            )
            
            # Descrição dinâmica do estresse
            stress_descriptions = {
                1: "Muito baixo - Completamente relaxado e calmo",
                2: "Baixo - Levemente relaxado, pouca preocupação",
                3: "Moderado - Alguma tensão presente, mas controlável",
                4: "Alto - Tensão significativa, dificuldade para relaxar",
                5: "Muito alto - Extremamente tenso, sobrecarregado"
            }
            st.caption(stress_descriptions[stress])
            
            fatigue = st.slider(
                "Fadiga (1-5)",
                min_value=1,
                max_value=5,
                value=3,
                help="1 = Muito baixa, 5 = Muito alta"
            )
            
            # Descrição dinâmica da fadiga
            fatigue_descriptions = {
                1: "Muito baixa - Completamente recuperado, sem fadiga",
                2: "Baixa - Levemente fatigado, boa recuperação",
                3: "Moderada - Alguma fadiga presente, recuperação parcial",
                4: "Alta - Fadiga significativa, recuperação insuficiente",
                5: "Muito alta - Extremamente fatigado, sem recuperação"
            }
            st.caption(fatigue_descriptions[fatigue])
        
        with col2:
            muscle_soreness = st.slider(
                "Dor Muscular (1-5)",
                min_value=1,
                max_value=5,
                value=3,
                help="1 = Nenhuma dor, 5 = Dor severa"
            )
            
            # Descrição dinâmica da dor muscular
            soreness_descriptions = {
                1: "Nenhuma - Sem dor ou desconforto muscular",
                2: "Leve - Leve sensibilidade em alguns músculos",
                3: "Moderada - Dor perceptível que não limita movimentos",
                4: "Alta - Dor significativa que limita alguns movimentos",
                5: "Severa - Dor intensa que limita a maioria dos movimentos"
            }
            st.caption(soreness_descriptions[muscle_soreness])
            
            energy = st.slider(
                "Energia (1-5)",
                min_value=1,
                max_value=5,
                value=3,
                help="1 = Muito baixa, 5 = Muito alta"
            )
            
            # Descrição dinâmica da energia
            energy_descriptions = {
                1: "Muito baixa - Sem energia, completamente esgotado",
                2: "Baixa - Pouca energia, sensação de letargia",
                3: "Moderada - Energia razoável para atividades normais",
                4: "Alta - Boa energia, disposição para atividades extras",
                5: "Muito alta - Energia excelente, completamente disposto"
            }
            st.caption(energy_descriptions[energy])
            
            motivation = st.slider(
                "Motivação (1-5)",
                min_value=1,
                max_value=5,
                value=3,
                help="1 = Muito baixa, 5 = Muito alta"
            )
            
            # Descrição dinâmica da motivação
            motivation_descriptions = {
                1: "Muito baixa - Sem vontade de treinar ou se exercitar",
                2: "Baixa - Pouca vontade de treinar, prefere descansar",
                3: "Moderada - Disposição normal para treinar",
                4: "Alta - Ansioso para treinar, muito disposto",
                5: "Muito alta - Extremamente motivado, não vê a hora de treinar"
            }
            st.caption(motivation_descriptions[motivation])
            
            nutrition = st.slider(
                "Nutrição (1-5)",
                min_value=1,
                max_value=5,
                value=3,
                help="1 = Muito ruim, 5 = Excelente"
            )
            
            # Descrição dinâmica da nutrição
            nutrition_descriptions = {
                1: "Muito ruim - Alimentação inadequada, muitos alimentos processados",
                2: "Ruim - Alimentação abaixo do ideal, poucas refeições balanceadas",
                3: "Regular - Alimentação razoável, algumas escolhas saudáveis",
                4: "Boa - Alimentação balanceada, maioria das refeições saudáveis",
                5: "Excelente - Alimentação ótima, todas as refeições nutritivas e balanceadas"
            }
            st.caption(nutrition_descriptions[nutrition])
            
            hydration = st.slider(
                "Hidratação (1-5)",
                min_value=1,
                max_value=5,
                value=3,
                help="1 = Muito baixa, 5 = Excelente"
            )
            
            # Descrição dinâmica da hidratação
            hydration_descriptions = {
                1: "Muito baixa - Desidratado, sede constante",
                2: "Baixa - Pouca ingestão de água, abaixo do recomendado",
                3: "Moderada - Ingestão razoável de água",
                4: "Boa - Bem hidratado, ingestão regular de água",
                5: "Excelente - Perfeitamente hidratado, ingestão ótima de água"
            }
            st.caption(hydration_descriptions[hydration])
        
        notes = st.text_area("Observações", "", help="Observações adicionais sobre seu estado atual")
        
        submitted = st.form_submit_button("Salvar Avaliação")
        
        if submitted:
            # Calcula o score de prontidão (0-100)
            # Inverte valores para estresse, fadiga e dor muscular (onde menor é melhor)
            stress_inv = 6 - stress
            fatigue_inv = 6 - fatigue
            soreness_inv = 6 - muscle_soreness
            
            # Normaliza duração do sono para escala 1-5
            sleep_duration_norm = max(1, min(5, (sleep_duration - 4) / 1.5 + 1))
            
            # Pesos dos componentes
            weights = {
                'sleep_quality': 0.20,
                'sleep_duration': 0.15,
                'stress': 0.15,
                'fatigue': 0.15,
                'muscle_soreness': 0.10,
                'energy': 0.10,
                'motivation': 0.05,
                'nutrition': 0.05,
                'hydration': 0.05
            }
            
            # Calcula o score ponderado
            score = (
                sleep_quality * weights['sleep_quality'] +
                sleep_duration_norm * weights['sleep_duration'] +
                stress_inv * weights['stress'] +
                fatigue_inv * weights['fatigue'] +
                soreness_inv * weights['muscle_soreness'] +
                energy * weights['energy'] +
                motivation * weights['motivation'] +
                nutrition * weights['nutrition'] +
                hydration * weights['hydration']
            )
            
            # Converte para escala 0-100
            score = int((score - 1) / 4 * 100)
            
            return {
                'date': date,
                'sleep_quality': sleep_quality,
                'sleep_duration': sleep_duration,
                'stress': stress,
                'fatigue': fatigue,
                'muscle_soreness': muscle_soreness,
                'energy': energy,
                'motivation': motivation,
                'nutrition': nutrition,
                'hydration': hydration,
                'notes': notes,
                'score': score
            }
    
    return None

def create_training_form(readiness_score=None):
    """
    Cria um formulário de registro de treino.
    
    Args:
        readiness_score (int): Score de prontidão para recomendação de volume
    
    Returns:
        dict: Dados do formulário
    """
    with st.form("training_form"):
        st.subheader("Nova Sessão de Treino")
        
        # Exibe recomendação de volume se houver score de prontidão
        if readiness_score is not None:
            # Calcula a redução recomendada de volume
            # 100 = 0% de redução, 50 = 40% de redução, 0 = 80% de redução
            volume_reduction = max(0, min(80, 80 - readiness_score * 0.8))
            recommended_volume = 100 - volume_reduction
            
            st.info(f"Com base no seu score de prontidão ({readiness_score}/100), recomendamos que você treine com {recommended_volume:.0f}% do seu volume normal (redução de {volume_reduction:.0f}%).")
            
            # Barra visual de volume recomendado
            st.progress(recommended_volume / 100)
        
        col1, col2 = st.columns(2)
        
        with col1:
            date = st.date_input("Data", datetime.now().date())
            
            training_type = st.selectbox(
                "Tipo de Treino",
                options=["Resistência", "Força", "Hipertrofia", "Potência", "Flexibilidade", "Técnico", "Recuperativo", "Outro"],
                index=0
            )
            
            duration = st.number_input(
                "Duração (minutos)",
                min_value=5,
                max_value=300,
                value=60,
                step=5,
                help="Duração total do treino em minutos"
            )
            
            # Descrição dinâmica da duração
            if duration < 30:
                st.caption(f"Curta - {duration} minutos")
            elif duration < 60:
                st.caption(f"Moderada - {duration} minutos")
            elif duration < 90:
                st.caption(f"Normal - {duration} minutos")
            elif duration < 120:
                st.caption(f"Longa - {duration} minutos")
            else:
                st.caption(f"Muito longa - {duration} minutos")
        
        with col2:
            rpe = st.slider(
                "Percepção de Esforço (0-10)",
                min_value=0,
                max_value=10,
                value=5,
                help="Escala de Borg adaptada (0-10)"
            )
            
            # Descrição dinâmica da RPE
            rpe_descriptions = {
                0: "Nenhum esforço - Repouso completo",
                1: "Muito, muito leve - Atividade quase imperceptível",
                2: "Muito leve - Como caminhar lentamente",
                3: "Leve - Atividade confortável, respiração normal",
                4: "Moderado - Começa a sentir algum esforço",
                5: "Um pouco difícil - Respiração mais intensa, ainda confortável",
                6: "Difícil - Respiração mais pesada, conversação ainda possível",
                7: "Muito difícil - Respiração profunda, conversação difícil",
                8: "Muito, muito difícil - Respiração muito pesada, fala limitada",
                9: "Máximo - Quase no limite máximo",
                10: "Extremo máximo - Esforço máximo absoluto"
            }
            st.caption(rpe_descriptions[rpe])
            
            # Calcula TRIMP automaticamente
            trimp = duration * rpe
            st.metric("TRIMP (Impulso de Treino)", trimp)
            
            post_feeling = st.slider(
                "Sensação Pós-Treino (1-5)",
                min_value=1,
                max_value=5,
                value=3,
                help="1 = Muito ruim, 5 = Excelente"
            )
            
            # Descrição dinâmica da sensação pós-treino
            feeling_descriptions = {
                1: "Muito ruim - Extremamente fatigado, incapaz de completar o treino como planejado",
                2: "Ruim - Mais difícil que o esperado, sensação de fadiga excessiva",
                3: "Normal - Concluiu o treino conforme planejado, fadiga esperada",
                4: "Bom - Treino fluiu bem, sensação de energia e força",
                5: "Excelente - Treino excepcional, sensação de superação e energia"
            }
            st.caption(feeling_descriptions[post_feeling])
        
        notes = st.text_area("Observações", "", help="Observações adicionais sobre o treino")
        
        submitted = st.form_submit_button("Salvar Treino")
        
        if submitted:
            # Calcula TSS (Training Stress Score)
            intensity_factor = rpe / 10.0
            tss = (duration * 60 * intensity_factor**2 * 100) / 3600
            
            return {
                'date': date,
                'type': training_type,
                'duration': duration,
                'rpe': rpe,
                'trimp': trimp,
                'tss': tss,
                'post_feeling': post_feeling,
                'notes': notes
            }
    
    return None

def create_psychological_form():
    """
    Cria um formulário de avaliação psicológica.
    
    Returns:
        dict: Dados do formulário
    """
    with st.form("psychological_form"):
        st.subheader("Nova Avaliação Psicológica")
        
        date = st.date_input("Data", datetime.now().date())
        
        st.write("### Escala DASS (Depressão, Ansiedade e Estresse)")
        st.caption("Avalie como você se sentiu na última semana")
        
        col1, col2 = st.columns(2)
        
        with col1:
            dass_depression = st.slider(
                "Depressão (0-3)",
                min_value=0,
                max_value=3,
                value=0,
                help="0 = Não se aplicou, 3 = Aplicou-se muito"
            )
            
            # Descrição dinâmica da depressão
            depression_descriptions = {
                0: "Não se aplicou - Sem sintomas de depressão",
                1: "Aplicou-se um pouco - Sintomas leves de tristeza ou desânimo",
                2: "Aplicou-se bastante - Sintomas moderados, dificuldade para se animar",
                3: "Aplicou-se muito - Sintomas intensos, sensação de desvalorização"
            }
            st.caption(depression_descriptions[dass_depression])
            
            dass_anxiety = st.slider(
                "Ansiedade (0-3)",
                min_value=0,
                max_value=3,
                value=0,
                help="0 = Não se aplicou, 3 = Aplicou-se muito"
            )
            
            # Descrição dinâmica da ansiedade
            anxiety_descriptions = {
                0: "Não se aplicou - Sem sintomas de ansiedade",
                1: "Aplicou-se um pouco - Sintomas leves de nervosismo",
                2: "Aplicou-se bastante - Sintomas moderados, preocupação frequente",
                3: "Aplicou-se muito - Sintomas intensos, medo ou pânico"
            }
            st.caption(anxiety_descriptions[dass_anxiety])
        
        with col2:
            dass_stress = st.slider(
                "Estresse (0-3)",
                min_value=0,
                max_value=3,
                value=0,
                help="0 = Não se aplicou, 3 = Aplicou-se muito"
            )
            
            # Descrição dinâmica do estresse
            stress_descriptions = {
                0: "Não se aplicou - Sem sintomas de estresse",
                1: "Aplicou-se um pouco - Sintomas leves de tensão",
                2: "Aplicou-se bastante - Sintomas moderados, irritabilidade",
                3: "Aplicou-se muito - Sintomas intensos, agitação constante"
            }
            st.caption(stress_descriptions[dass_stress])
            
            mood = st.slider(
                "Humor Geral (1-5)",
                min_value=1,
                max_value=5,
                value=3,
                help="1 = Muito ruim, 5 = Excelente"
            )
            
            # Descrição dinâmica do humor
            mood_descriptions = {
                1: "Muito ruim - Extremamente negativo, irritado ou triste",
                2: "Ruim - Predominantemente negativo, pouca alegria",
                3: "Neutro - Nem positivo nem negativo, estável",
                4: "Bom - Predominantemente positivo, otimista",
                5: "Excelente - Extremamente positivo, alegre e entusiasmado"
            }
            st.caption(mood_descriptions[mood])
        
        st.write("### Fatores Adicionais")
        
        col3, col4 = st.columns(2)
        
        with col3:
            sleep_quality = st.slider(
                "Qualidade do Sono (1-5)",
                min_value=1,
                max_value=5,
                value=3,
                help="1 = Muito ruim, 5 = Excelente"
            )
            
            # Descrição dinâmica da qualidade do sono
            sleep_quality_descriptions = {
                1: "Muito ruim - Sono extremamente fragmentado, insônia severa",
                2: "Ruim - Dificuldade para dormir, despertares frequentes",
                3: "Regular - Sono razoável com alguns despertares",
                4: "Bom - Sono contínuo com poucos despertares",
                5: "Excelente - Sono profundo e reparador"
            }
            st.caption(sleep_quality_descriptions[sleep_quality])
        
        with col4:
            life_stress = st.slider(
                "Estresse da Vida (1-5)",
                min_value=1,
                max_value=5,
                value=3,
                help="1 = Muito baixo, 5 = Muito alto"
            )
            
            # Descrição dinâmica do estresse da vida
            life_stress_descriptions = {
                1: "Muito baixo - Sem eventos estressantes, vida tranquila",
                2: "Baixo - Poucos estressores, bem administrados",
                3: "Moderado - Estressores normais do dia a dia",
                4: "Alto - Vários estressores significativos",
                5: "Muito alto - Múltiplos estressores intensos, sobrecarga"
            }
            st.caption(life_stress_descriptions[life_stress])
        
        notes = st.text_area("Observações", "", help="Observações adicionais sobre seu estado psicológico")
        
        submitted = st.form_submit_button("Salvar Avaliação")
        
        if submitted:
            # Calcula o score DASS (0-100, onde maior é melhor)
            # Inverte a escala, pois no DASS original, valores menores são melhores
            dass_score = 100 - ((dass_depression + dass_anxiety + dass_stress) / 9 * 100)
            
            return {
                'date': date,
                'dass_depression': dass_depression,
                'dass_anxiety': dass_anxiety,
                'dass_stress': dass_stress,
                'mood': mood,
                'sleep_quality': sleep_quality,
                'life_stress': life_stress,
                'notes': notes,
                'dass_score': int(dass_score)
            }
    
    return None

def create_login_form():
    """
    Cria um formulário de login.
    
    Returns:
        dict: Dados do formulário
    """
    with st.form("login_form"):
        st.subheader("Login")
        
        email = st.text_input("E-mail", key="login_email")
        password = st.text_input("Senha", type="password", key="login_password")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            submitted = st.form_submit_button("Entrar")
        
        if submitted:
            # Valida campos obrigatórios
            valid, error_msg = validate_required_fields(
                {'email': email, 'password': password},
                ['email', 'password']
            )
            
            if not valid:
                st.error(error_msg)
                return None
            
            # Valida formato de e-mail
            valid, error_msg = validate_email(email)
            
            if not valid:
                st.error(error_msg)
                return None
            
            return {
                'email': email,
                'password': password
            }
    
    return None

def create_signup_form():
    """
    Cria um formulário de criação de conta.
    
    Returns:
        dict: Dados do formulário
    """
    with st.form("signup_form"):
        st.subheader("Criar Conta")
        
        name = st.text_input("Nome", key="signup_name")
        email = st.text_input("E-mail", key="signup_email")
        password = st.text_input("Senha", type="password", key="signup_password")
        confirm_password = st.text_input("Confirmar Senha", type="password", key="signup_confirm")
        
        submitted = st.form_submit_button("Criar Conta")
        
        if submitted:
            # Valida campos obrigatórios
            valid, error_msg = validate_required_fields(
                {'name': name, 'email': email, 'password': password, 'confirm_password': confirm_password},
                ['name', 'email', 'password', 'confirm_password']
            )
            
            if not valid:
                st.error(error_msg)
                return None
            
            # Valida formato de e-mail
            valid, error_msg = validate_email(email)
            
            if not valid:
                st.error(error_msg)
                return None
            
            # Valida força da senha
            valid, error_msg, score = validate_password_strength(password)
            
            if not valid:
                st.error(error_msg)
                return None
            
            # Valida confirmação de senha
            if password != confirm_password:
                st.error("As senhas não coincidem")
                return None
            
            return {
                'name': name,
                'email': email,
                'password': password
            }
    
    return None

def create_reset_password_form():
    """
    Cria um formulário de redefinição de senha.
    
    Returns:
        dict: Dados do formulário
    """
    with st.form("reset_password_form"):
        st.subheader("Redefinir Senha")
        
        email = st.text_input("E-mail", key="reset_email")
        
        submitted = st.form_submit_button("Enviar Link de Redefinição")
        
        if submitted:
            # Valida campos obrigatórios
            valid, error_msg = validate_required_fields(
                {'email': email},
                ['email']
            )
            
            if not valid:
                st.error(error_msg)
                return None
            
            # Valida formato de e-mail
            valid, error_msg = validate_email(email)
            
            if not valid:
                st.error(error_msg)
                return None
            
            return {
                'email': email
            }
    
    return None

def create_profile_form(user_data=None):
    """
    Cria um formulário de perfil do usuário.
    
    Args:
        user_data (dict): Dados atuais do usuário
    
    Returns:
        dict: Dados do formulário
    """
    if user_data is None:
        user_data = {}
    
    with st.form("profile_form"):
        st.subheader("Perfil do Atleta")
        
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input(
                "Nome",
                value=user_data.get('name', '')
            )
            
            email = st.text_input(
                "E-mail",
                value=user_data.get('email', ''),
                disabled=True  # E-mail não pode ser alterado
            )
            
            birth_date = st.date_input(
                "Data de Nascimento",
                value=user_data.get('birth_date', datetime.now().date() - timedelta(days=365*25))
            )
            
            gender = st.selectbox(
                "Gênero",
                options=["Masculino", "Feminino", "Outro", "Prefiro não informar"],
                index=["Masculino", "Feminino", "Outro", "Prefiro não informar"].index(user_data.get('gender', "Prefiro não informar"))
            )
        
        with col2:
            height = st.number_input(
                "Altura (cm)",
                min_value=100,
                max_value=250,
                value=int(user_data.get('height', 170)),
                help="Altura em centímetros"
            )
            
            weight = st.number_input(
                "Peso (kg)",
                min_value=30.0,
                max_value=200.0,
                value=float(user_data.get('weight', 70.0)),
                step=0.1,
                help="Peso em quilogramas"
            )
            
            sport = st.text_input(
                "Esporte Principal",
                value=user_data.get('sport', '')
            )
            
            level = st.selectbox(
                "Nível",
                options=["Iniciante", "Intermediário", "Avançado", "Elite"],
                index=["Iniciante", "Intermediário", "Avançado", "Elite"].index(user_data.get('level', "Intermediário"))
            )
        
        st.write("### Objetivos")
        
        goals = st.text_area(
            "Objetivos",
            value=user_data.get('goals', ''),
            help="Descreva seus principais objetivos esportivos"
        )
        
        submitted = st.form_submit_button("Salvar Perfil")
        
        if submitted:
            # Calcula IMC
            if height > 0:
                bmi = weight / ((height / 100) ** 2)
            else:
                bmi = 0
            
            return {
                'name': name,
                'email': email,
                'birth_date': birth_date,
                'gender': gender,
                'height': height,
                'weight': weight,
                'sport': sport,
                'level': level,
                'goals': goals,
                'bmi': bmi
            }
    
    return None

def create_settings_form(settings_data=None):
    """
    Cria um formulário de configurações do aplicativo.
    
    Args:
        settings_data (dict): Configurações atuais
    
    Returns:
        dict: Dados do formulário
    """
    if settings_data is None:
        settings_data = {}
    
    with st.form("settings_form"):
        st.subheader("Configurações do Aplicativo")
        
        st.write("### Aparência")
        
        theme = st.selectbox(
            "Tema",
            options=["Escuro", "Claro", "Sistema"],
            index=["Escuro", "Claro", "Sistema"].index(settings_data.get('theme', "Escuro"))
        )
        
        st.write("### Dashboard")
        
        default_period = st.selectbox(
            "Período Padrão",
            options=["7 dias", "14 dias", "30 dias", "90 dias"],
            index=["7 dias", "14 dias", "30 dias", "90 dias"].index(settings_data.get('default_period', "30 dias"))
        )
        
        show_recommendations = st.checkbox(
            "Mostrar Recomendações",
            value=settings_data.get('show_recommendations', True)
        )
        
        show_reference_ranges = st.checkbox(
            "Mostrar Faixas de Referência",
            value=settings_data.get('show_reference_ranges', True)
        )
        
        st.write("### Notificações")
        
        enable_notifications = st.checkbox(
            "Ativar Notificações",
            value=settings_data.get('enable_notifications', True)
        )
        
        if enable_notifications:
            reminder_time = st.time_input(
                "Horário do Lembrete",
                value=datetime.strptime(settings_data.get('reminder_time', "08:00"), "%H:%M").time()
            )
            
            reminder_days = st.multiselect(
                "Dias de Lembrete",
                options=["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"],
                default=settings_data.get('reminder_days', ["Segunda", "Terça", "Quarta", "Quinta", "Sexta"])
            )
        else:
            reminder_time = datetime.strptime("08:00", "%H:%M").time()
            reminder_days = []
        
        st.write("### Métricas Avançadas")
        
        show_advanced_metrics = st.checkbox(
            "Mostrar Métricas Avançadas",
            value=settings_data.get('show_advanced_metrics', True),
            help="TSS, CTL, ATL, TSB, Monotonia, Strain"
        )
        
        submitted = st.form_submit_button("Salvar Configurações")
        
        if submitted:
            return {
                'theme': theme,
                'default_period': default_period,
                'show_recommendations': show_recommendations,
                'show_reference_ranges': show_reference_ranges,
                'enable_notifications': enable_notifications,
                'reminder_time': reminder_time.strftime("%H:%M"),
                'reminder_days': reminder_days,
                'show_advanced_metrics': show_advanced_metrics
            }
    
    return None

def create_report_form():
    """
    Cria um formulário para geração de relatórios.
    
    Returns:
        dict: Dados do formulário
    """
    with st.form("report_form"):
        st.subheader("Gerar Relatório")
        
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input(
                "Data de Início",
                value=datetime.now().date() - timedelta(days=30)
            )
        
        with col2:
            end_date = st.date_input(
                "Data de Fim",
                value=datetime.now().date()
            )
        
        st.write("### Conteúdo do Relatório")
        
        include_readiness = st.checkbox("Incluir Dados de Prontidão", value=True)
        include_training = st.checkbox("Incluir Dados de Treino", value=True)
        include_psychological = st.checkbox("Incluir Dados Psicológicos", value=True)
        include_advanced_metrics = st.checkbox("Incluir Métricas Avançadas", value=True)
        
        st.write("### Formato")
        
        report_format = st.radio(
            "Formato",
            options=["PDF", "CSV"],
            index=0
        )
        
        submitted = st.form_submit_button("Gerar Relatório")
        
        if submitted:
            # Valida intervalo de datas
            if start_date > end_date:
                st.error("A data de início não pode ser posterior à data de fim")
                return None
            
            # Verifica se pelo menos um tipo de dado está selecionado
            if not (include_readiness or include_training or include_psychological):
                st.error("Selecione pelo menos um tipo de dado para incluir no relatório")
                return None
            
            return {
                'start_date': start_date,
                'end_date': end_date,
                'include_readiness': include_readiness,
                'include_training': include_training,
                'include_psychological': include_psychological,
                'include_advanced_metrics': include_advanced_metrics,
                'format': report_format
            }
    
    return None

def create_goal_form():
    """
    Cria um formulário para definição de metas.
    
    Returns:
        dict: Dados do formulário
    """
    with st.form("goal_form"):
        st.subheader("Nova Meta")
        
        goal_type = st.selectbox(
            "Tipo de Meta",
            options=["Prontidão", "Treino", "Psicológico", "Outro"],
            index=0
        )
        
        if goal_type == "Prontidão":
            metric = st.selectbox(
                "Métrica",
                options=["Score de Prontidão", "Qualidade do Sono", "Estresse", "Fadiga", "Energia", "Motivação"],
                index=0
            )
        elif goal_type == "Treino":
            metric = st.selectbox(
                "Métrica",
                options=["TRIMP Semanal", "TSS Semanal", "Frequência de Treino", "Volume de Treino", "RPE Médio"],
                index=0
            )
        elif goal_type == "Psicológico":
            metric = st.selectbox(
                "Métrica",
                options=["Score DASS", "Ansiedade", "Depressão", "Estresse", "Humor"],
                index=0
            )
        else:
            metric = st.text_input("Métrica Personalizada")
        
        target_value = st.number_input(
            "Valor Alvo",
            min_value=0.0,
            value=80.0,
            step=1.0
        )
        
        target_date = st.date_input(
            "Data Alvo",
            value=datetime.now().date() + timedelta(days=30)
        )
        
        description = st.text_area(
            "Descrição",
            help="Descreva sua meta em detalhes"
        )
        
        submitted = st.form_submit_button("Salvar Meta")
        
        if submitted:
            # Valida data alvo
            if target_date < datetime.now().date():
                st.error("A data alvo não pode ser no passado")
                return None
            
            return {
                'type': goal_type,
                'metric': metric,
                'target_value': target_value,
                'target_date': target_date,
                'description': description,
                'created_at': datetime.now().date(),
                'status': 'active'
            }
    
    return None

# Funções de formulários específicos para o sistema

def create_variable_selection_form(available_variables, selected_variables=None):
    """
    Cria um formulário para seleção de variáveis para análise.
    
    Args:
        available_variables (dict): Dicionário com variáveis disponíveis
        selected_variables (list): Lista de variáveis já selecionadas
    
    Returns:
        list: Lista de variáveis selecionadas
    """
    if selected_variables is None:
        selected_variables = []
    
    with st.form("variable_selection_form"):
        st.subheader("Selecionar Variáveis para Análise")
        
        st.write("### Variáveis de Prontidão")
        readiness_vars = st.multiselect(
            "Selecione as variáveis de prontidão",
            options=available_variables.get('readiness', []),
            default=[var for var in selected_variables if var in available_variables.get('readiness', [])]
        )
        
        st.write("### Variáveis de Treino")
        training_vars = st.multiselect(
            "Selecione as variáveis de treino",
            options=available_variables.get('training', []),
            default=[var for var in selected_variables if var in available_variables.get('training', [])]
        )
        
        st.write("### Variáveis Psicológicas")
        psych_vars = st.multiselect(
            "Selecione as variáveis psicológicas",
            options=available_variables.get('psychological', []),
            default=[var for var in selected_variables if var in available_variables.get('psychological', [])]
        )
        
        st.write("### Métricas Avançadas")
        advanced_vars = st.multiselect(
            "Selecione as métricas avançadas",
            options=available_variables.get('advanced', []),
            default=[var for var in selected_variables if var in available_variables.get('advanced', [])]
        )
        
        submitted = st.form_submit_button("Aplicar Seleção")
        
        if submitted:
            # Combina todas as variáveis selecionadas
            selected = readiness_vars + training_vars + psych_vars + advanced_vars
            
            # Verifica se há variáveis selecionadas
            if not selected:
                st.error("Selecione pelo menos uma variável para análise")
                return None
            
            return selected
    
    return None

def create_correlation_analysis_form(available_variables):
    """
    Cria um formulário para análise de correlação entre duas variáveis.
    
    Args:
        available_variables (list): Lista de variáveis disponíveis
    
    Returns:
        dict: Dados do formulário
    """
    with st.form("correlation_analysis_form"):
        st.subheader("Análise de Correlação")
        
        col1, col2 = st.columns(2)
        
        with col1:
            variable_x = st.selectbox(
                "Variável X",
                options=available_variables,
                index=0
            )
        
        with col2:
            variable_y = st.selectbox(
                "Variável Y",
                options=available_variables,
                index=min(1, len(available_variables) - 1)
            )
        
        method = st.radio(
            "Método de Correlação",
            options=["Pearson", "Spearman"],
            index=0,
            help="Pearson: linear, Spearman: monotônica (não necessariamente linear)"
        )
        
        show_trendline = st.checkbox("Mostrar Linha de Tendência", value=True)
        
        submitted = st.form_submit_button("Analisar Correlação")
        
        if submitted:
            # Verifica se as variáveis são diferentes
            if variable_x == variable_y:
                st.error("Selecione duas variáveis diferentes para análise de correlação")
                return None
            
            return {
                'variable_x': variable_x,
                'variable_y': variable_y,
                'method': method.lower(),
                'show_trendline': show_trendline
            }
    
    return None

def create_date_filter_form(min_date=None, max_date=None, default_period=30):
    """
    Cria um formulário para filtro de datas.
    
    Args:
        min_date (date): Data mínima disponível
        max_date (date): Data máxima disponível
        default_period (int): Período padrão em dias
    
    Returns:
        dict: Dados do formulário
    """
    if min_date is None:
        min_date = datetime.now().date() - timedelta(days=365)
    
    if max_date is None:
        max_date = datetime.now().date()
    
    with st.form("date_filter_form"):
        st.subheader("Filtro de Período")
        
        # Opções de período predefinidas
        period_options = {
            "7 dias": 7,
            "14 dias": 14,
            "30 dias": 30,
            "90 dias": 90,
            "Todo o período": (max_date - min_date).days + 1,
            "Personalizado": 0
        }
        
        selected_period = st.selectbox(
            "Período",
            options=list(period_options.keys()),
            index=list(period_options.keys()).index("30 dias")
        )
        
        if selected_period == "Personalizado":
            col1, col2 = st.columns(2)
            
            with col1:
                start_date = st.date_input(
                    "Data de Início",
                    value=max_date - timedelta(days=default_period),
                    min_value=min_date,
                    max_value=max_date
                )
            
            with col2:
                end_date = st.date_input(
                    "Data de Fim",
                    value=max_date,
                    min_value=min_date,
                    max_value=max_date
                )
        else:
            days = period_options[selected_period]
            start_date = max(min_date, max_date - timedelta(days=days-1))
            end_date = max_date
        
        submitted = st.form_submit_button("Aplicar Filtro")
        
        if submitted:
            # Valida intervalo de datas
            if start_date > end_date:
                st.error("A data de início não pode ser posterior à data de fim")
                return None
            
            return {
                'start_date': start_date,
                'end_date': end_date,
                'period_name': selected_period
            }
    
    return None
