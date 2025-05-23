import pandas as pd
import numpy as np

def calculate_readiness_score(data):
    """
    Calcula o score de prontidão baseado nos dados fornecidos
    Pesos definidos com base em literatura científica
    """
    weights = {
        'sleep_quality': 0.25,      # 25% - Qualidade do sono
        'sleep_duration': 0.15,     # 15% - Duração do sono
        'stress_level': 0.20,       # 20% - Nível de estresse
        'muscle_soreness': 0.15,    # 15% - Dor muscular
        'energy_level': 0.15,       # 15% - Nível de energia
        'motivation': 0.05,         # 5% - Motivação
        'nutrition_quality': 0.03,  # 3% - Qualidade nutricional
        'hydration': 0.02          # 2% - Hidratação
    }
    
    # Normalizar variáveis invertidas (quanto menor, melhor)
    normalized_stress = 6 - data['stress_level']
    normalized_soreness = 6 - data['muscle_soreness']
    
    # Normalizar duração do sono (ideal = 8 horas, máximo = 5 pontos)
    sleep_duration_normalized = min(data['sleep_duration'] / 8 * 5, 5)
    
    # Calcular score ponderado
    score = (
        weights['sleep_quality'] * data['sleep_quality'] +
        weights['sleep_duration'] * sleep_duration_normalized +
        weights['stress_level'] * normalized_stress +
        weights['muscle_soreness'] * normalized_soreness +
        weights['energy_level'] * data['energy_level'] +
        weights['motivation'] * data['motivation'] +
        weights['nutrition_quality'] * data['nutrition_quality'] +
        weights['hydration'] * data['hydration']
    )
    
    # Converter para escala 0-100
    return round(score * 20, 1)

def get_readiness_interpretation(score):
    """
    Retorna interpretação do score de prontidão
    """
    if score >= 85:
        return {
            "level": "Excelente",
            "color": "#2E7D32",  # Verde escuro
            "emoji": "🟢",
            "description": "Prontidão excelente! Ideal para treinos de alta intensidade ou competições.",
            "recommendations": [
                "Aproveite para treinos de alta intensidade",
                "Momento ideal para competições",
                "Mantenha a consistência na rotina"
            ]
        }
    elif score >= 70:
        return {
            "level": "Boa",
            "color": "#388E3C",  # Verde
            "emoji": "🔵",
            "description": "Boa prontidão. Adequado para treinos regulares com intensidade moderada a alta.",
            "recommendations": [
                "Treinos de intensidade moderada a alta são apropriados",
                "Continue monitorando os indicadores",
                "Foque na manutenção da qualidade do sono"
            ]
        }
    elif score >= 55:
        return {
            "level": "Moderada",
            "color": "#FBC02D",  # Amarelo
            "emoji": "🟡",
            "description": "Prontidão moderada. Considere treinos de intensidade média.",
            "recommendations": [
                "Treinos de intensidade baixa a moderada",
                "Evite esforços máximos",
                "Revise fatores de recuperação"
            ]
        }
    elif score >= 40:
        return {
            "level": "Baixa",
            "color": "#FF8F00",  # Laranja
            "emoji": "🟠",
            "description": "Prontidão baixa. Recomenda-se treinos leves ou descanso ativo.",
            "recommendations": [
                "Apenas treinos leves ou descanso ativo",
                "Priorize recuperação",
                "Analise fatores que impactam o sono e estresse"
            ]
        }
    else:
        return {
            "level": "Muito Baixa",
            "color": "#D32F2F",  # Vermelho
            "emoji": "🔴",
            "description": "Prontidão muito baixa. Priorize recuperação e descanso.",
            "recommendations": [
                "Descanso completo ou atividade muito leve",
                "Foque totalmente na recuperação",
                "Considere consultar profissional de saúde"
            ]
        }

def analyze_readiness_trend(data):
    """
    Analisa tendência dos scores de prontidão
    """
    if len(data) < 3:
        return {
            "trend": "Dados insuficientes",
            "description": "Precisamos de mais dados para análise de tendência",
            "color": "#757575"
        }
    
    scores = data['readiness_score'].tolist()
    
    # Calcular tendência usando regressão linear simples
    x = np.arange(len(scores))
    slope = np.polyfit(x, scores, 1)[0]
    
    if slope > 2:
        return {
            "trend": "Melhorando significativamente",
            "description": f"Tendência positiva (+{slope:.1f} pontos por avaliação)",
            "color": "#2E7D32",
            "emoji": "📈"
        }
    elif slope > 0.5:
        return {
            "trend": "Melhorando",
            "description": f"Leve melhora (+{slope:.1f} pontos por avaliação)",
            "color": "#388E3C",
            "emoji": "📈"
        }
    elif slope < -2:
        return {
            "trend": "Piorando significativamente",
            "description": f"Tendência negativa ({slope:.1f} pontos por avaliação)",
            "color": "#D32F2F",
            "emoji": "📉"
        }
    elif slope < -0.5:
        return {
            "trend": "Piorando",
            "description": f"Leve declínio ({slope:.1f} pontos por avaliação)",
            "color": "#FF8F00",
            "emoji": "📉"
        }
    else:
        return {
            "trend": "Estável",
            "description": "Prontidão mantendo-se estável",
            "color": "#1565C0",
            "emoji": "➡️"
        }

def get_component_analysis(data):
    """
    Analisa componentes individuais da prontidão
    """
    if data.empty:
        return {}
    
    latest = data.iloc[0]  # Mais recente
    avg_30d = data.head(30).mean() if len(data) >= 30 else data.mean()
    
    components = {
        'sleep_quality': {
            'name': 'Qualidade do Sono',
            'current': latest['sleep_quality'],
            'average': avg_30d['sleep_quality'],
            'weight': 25,
            'optimal_range': (4, 5)
        },
        'sleep_duration': {
            'name': 'Duração do Sono',
            'current': latest['sleep_duration'],
            'average': avg_30d['sleep_duration'],
            'weight': 15,
            'optimal_range': (7, 9),
            'unit': 'horas'
        },
        'stress_level': {
            'name': 'Nível de Estresse',
            'current': latest['stress_level'],
            'average': avg_30d['stress_level'],
            'weight': 20,
            'optimal_range': (1, 2),
            'inverted': True
        },
        'muscle_soreness': {
            'name': 'Dor Muscular',
            'current': latest['muscle_soreness'],
            'average': avg_30d['muscle_soreness'],
            'weight': 15,
            'optimal_range': (1, 2),
            'inverted': True
        },
        'energy_level': {
            'name': 'Nível de Energia',
            'current': latest['energy_level'],
            'average': avg_30d['energy_level'],
            'weight': 15,
            'optimal_range': (4, 5)
        },
        'motivation': {
            'name': 'Motivação',
            'current': latest['motivation'],
            'average': avg_30d['motivation'],
            'weight': 5,
            'optimal_range': (4, 5)
        },
        'nutrition_quality': {
            'name': 'Qualidade Nutricional',
            'current': latest['nutrition_quality'],
            'average': avg_30d['nutrition_quality'],
            'weight': 3,
            'optimal_range': (4, 5)
        },
        'hydration': {
            'name': 'Hidratação',
            'current': latest['hydration'],
            'average': avg_30d['hydration'],
            'weight': 2,
            'optimal_range': (4, 5)
        }
    }
    
    return components

def get_weekly_pattern_analysis(data):
    """
    Analisa padrões semanais de prontidão
    """
    if data.empty:
        return {}
    
    # Adicionar dia da semana
    data_copy = data.copy()
    data_copy['weekday'] = pd.to_datetime(data_copy['date']).dt.day_name()
    data_copy['weekday_pt'] = data_copy['weekday'].map({
        'Monday': 'Segunda',
        'Tuesday': 'Terça',
        'Wednesday': 'Quarta',
        'Thursday': 'Quinta',
        'Friday': 'Sexta',
        'Saturday': 'Sábado',
        'Sunday': 'Domingo'
    })
    
    # Calcular médias por dia da semana
    weekly_avg = data_copy.groupby('weekday_pt')['readiness_score'].agg(['mean', 'count']).round(1)
    
    # Ordenar dias da semana
    day_order = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
    weekly_avg = weekly_avg.reindex([day for day in day_order if day in weekly_avg.index])
    
    # Identificar melhor e pior dia
    best_day = weekly_avg['mean'].idxmax() if not weekly_avg.empty else None
    worst_day = weekly_avg['mean'].idxmin() if not weekly_avg.empty else None
    
    return {
        'weekly_averages': weekly_avg.to_dict('index'),
        'best_day': {
            'day': best_day,
            'score': weekly_avg.loc[best_day, 'mean'] if best_day else 0
        },
        'worst_day': {
            'day': worst_day,
            'score': weekly_avg.loc[worst_day, 'mean'] if worst_day else 0
        }
    }

def get_personalized_recommendations(latest_assessment, historical_data):
    """
    Gera recomendações personalizadas baseadas nos dados
    """
    recommendations = []
    
    if not latest_assessment:
        return recommendations
    
    # Análise do sono
    if latest_assessment['sleep_quality'] < 3:
        recommendations.append({
            'category': 'Sono',
            'priority': 'Alta',
            'title': 'Melhorar Qualidade do Sono',
            'description': 'Sua qualidade de sono está baixa',
            'actions': [
                'Criar rotina relaxante antes de dormir',
                'Evitar telas 1 hora antes de dormir',
                'Manter ambiente escuro e fresco',
                'Considerar técnicas de relaxamento'
            ]
        })
    
    if latest_assessment['sleep_duration'] < 7:
        recommendations.append({
            'category': 'Sono',
            'priority': 'Alta',
            'title': 'Aumentar Duração do Sono',
            'description': f'Você dormiu {latest_assessment["sleep_duration"]:.1f}h, menos que o recomendado',
            'actions': [
                'Deitar mais cedo (ideal: 7-9 horas de sono)',
                'Reduzir cafeína após 15h',
                'Criar horário consistente para dormir'
            ]
        })
    
    # Análise do estresse
    if latest_assessment['stress_level'] > 3:
        recommendations.append({
            'category': 'Estresse',
            'priority': 'Alta',
            'title': 'Gerenciar Estresse',
            'description': 'Seus níveis de estresse estão elevados',
            'actions': [
                'Praticar meditação ou mindfulness',
                'Fazer exercícios respiratórios',
                'Identificar e gerenciar fontes de estresse',
                'Considerar atividades relaxantes'
            ]
        })
    
    # Análise da dor muscular
    if latest_assessment['muscle_soreness'] > 3:
        recommendations.append({
            'category': 'Recuperação',
            'priority': 'Média',
            'title': 'Cuidar da Recuperação Muscular',
            'description': 'Você está com dor muscular significativa',
            'actions': [
                'Fazer alongamentos suaves',
                'Usar foam roller',
                'Considerar massagem ou banho quente',
                'Reduzir intensidade dos treinos temporariamente'
            ]
        })
    
    # Análise da energia
    if latest_assessment['energy_level'] < 3:
        recommendations.append({
            'category': 'Energia',
            'priority': 'Média',
            'title': 'Aumentar Níveis de Energia',
            'description': 'Seus níveis de energia estão baixos',
            'actions': [
                'Revisar alimentação e hidratação',
                'Garantir exposição à luz solar',
                'Verificar qualidade do sono',
                'Considerar reduzir carga de treino'
            ]
        })
    
    # Análise da nutrição
    if latest_assessment['nutrition_quality'] < 3:
        recommendations.append({
            'category': 'Nutrição',
            'priority': 'Baixa',
            'title': 'Melhorar Alimentação',
            'description': 'Sua qualidade nutricional pode ser melhorada',
            'actions': [
                'Planejar refeições com antecedência',
                'Incluir mais frutas e vegetais',
                'Garantir proteína adequada',
                'Manter regularidade nas refeições'
            ]
        })
    
    return recommendations