from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from flask import Response
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
import matplotlib.pyplot as plt
import seaborn as sns
import base64
from io import BytesIO
import json

def calculate_readiness_score(data):
    """
    Calcula o score de prontidão baseado nos dados fornecidos
    """
    weights = {
        'sleep_quality': 0.25,
        'sleep_duration': 0.15,
        'stress_level': 0.20,
        'muscle_soreness': 0.15,
        'energy_level': 0.15,
        'motivation': 0.05,
        'nutrition_quality': 0.03,
        'hydration': 0.02
    }
    
    # Normalizar stress_level e muscle_soreness (escala invertida)
    normalized_stress = 6 - data['stress_level']
    normalized_soreness = 6 - data['muscle_soreness']
    
    # Normalizar sleep_duration (ideal = 8 horas)
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

def calculate_training_metrics(user_assessments):
    """
    Calcula métricas de treino (CTL, ATL, TSB)
    """
    df = pd.DataFrame([{
        'date': a.date,
        'training_load': a.training_load
    } for a in user_assessments])
    
    df = df.sort_values('date')
    df.set_index('date', inplace=True)
    
    # Calcular CTL (Chronic Training Load) - média de 42 dias
    df['CTL'] = df['training_load'].rolling(window=42, min_periods=1).mean()
    
    # Calcular ATL (Acute Training Load) - média de 7 dias
    df['ATL'] = df['training_load'].rolling(window=7, min_periods=1).mean()
    
    # Calcular TSB (Training Stress Balance)
    df['TSB'] = df['CTL'] - df['ATL']
    
    # Calcular Ratio ATL/CTL
    df['Ratio'] = df['ATL'] / df['CTL']
    
    return df

def calculate_dass21_scores(responses):
    """
    Calcula os scores do DASS-21
    """
    # Índices das questões para cada dimensão
    depression_items = [2, 4, 9, 12, 15, 16, 20]  # Índices base 0
    anxiety_items = [1, 3, 6, 14, 18, 19, 21]
    stress_items = [0, 5, 7, 8, 10, 11, 13, 17]
    
    # Calcular somas (multiplicar por 2 para ter escala 0-42)
    depression_score = sum([responses[i] for i in depression_items]) * 2
    anxiety_score = sum([responses[i] for i in anxiety_items]) * 2
    stress_score = sum([responses[i] for i in stress_items]) * 2
    
    return {
        'depression_score': depression_score,
        'anxiety_score': anxiety_score,
        'stress_score': stress_score
    }

def calculate_flow_score(responses):
    """
    Calcula o score de Flow State
    """
    # Média das respostas do Flow State Scale
    return sum(responses) / len(responses) if responses else 0

def calculate_motivation_scores(responses):
    """
    Calcula os scores de motivação
    """
    # Assumindo que as respostas vêm em grupos
    intrinsic = sum(responses[0:4]) / 4  # Questões 1-4
    extrinsic = sum(responses[4:8]) / 4  # Questões 5-8
    amotivation = sum(responses[8:12]) / 4  # Questões 9-12
    
    return {
        'intrinsic_motivation': intrinsic,
        'extrinsic_motivation': extrinsic,
        'amotivation': amotivation
    }

def get_interpretation(score, score_type):
    """
    Fornece interpretação para diferentes tipos de scores
    """
    interpretations = {
        'readiness': {
            'ranges': [(0, 40, 'Baixa prontidão'), (40, 70, 'Prontidão moderada'), (70, 100, 'Alta prontidão')],
            'color': lambda s: 'danger' if s < 40 else 'warning' if s < 70 else 'success'
        },
        'stress': {
            'ranges': [(0, 7, 'Normal'), (8, 9, 'Leve'), (10, 12, 'Moderado'), (13, 16, 'Severo'), (17, 42, 'Extremamente severo')],
            'color': lambda s: 'success' if s <= 7 else 'info' if s <= 9 else 'warning' if s <= 12 else 'danger'
        },
        'anxiety': {
            'ranges': [(0, 3, 'Normal'), (4, 5, 'Leve'), (6, 7, 'Moderada'), (8, 9, 'Severa'), (10, 42, 'Extremamente severa')],
            'color': lambda s: 'success' if s <= 3 else 'info' if s <= 5 else 'warning' if s <= 7 else 'danger'
        },
        'depression': {
            'ranges': [(0, 4, 'Normal'), (5, 6, 'Leve'), (7, 10, 'Moderada'), (11, 13, 'Severa'), (14, 42, 'Extremamente severa')],
            'color': lambda s: 'success' if s <= 4 else 'info' if s <= 6 else 'warning' if s <= 10 else 'danger'
        },
        'flow': {
            'ranges': [(1, 2, 'Muito baixo'), (2, 3, 'Baixo'), (3, 4, 'Moderado'), (4, 5, 'Alto'), (5, 6, 'Muito alto')],
            'color': lambda s: 'danger' if s < 2 else 'warning' if s < 3 else 'info' if s < 4 else 'success'
        }
    }
    
    if score_type not in interpretations:
        return {'label': 'N/A', 'color': 'secondary'}
    
    ranges = interpretations[score_type]['ranges']
    color_func = interpretations[score_type]['color']
    
    for min_val, max_val, label in ranges:
        if min_val <= score <= max_val:
            return {'label': label, 'color': color_func(score)}
    
    return {'label': 'N/A', 'color': 'secondary'}

def export_to_pdf(user_data, filename='athlete_report.pdf'):
    """
    Exporta dados para PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    
    # Título
    title = Paragraph("Relatório de Monitoramento do Atleta", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))
    
    # Informações do usuário
    user_info = Paragraph(f"Atleta: {user_data['name']}<br/>Período: {user_data['period']}", styles['Normal'])
    story.append(user_info)
    story.append(Spacer(1, 12))
    
    # Métricas principais
    metrics_data = [
        ['Métrica', 'Valor', 'Interpretação'],
        ['Prontidão Média', f"{user_data['avg_readiness']:.1f}", get_interpretation(user_data['avg_readiness'], 'readiness')['label']],
        ['Carga de Treino', f"{user_data['avg_training_load']:.1f}", ''],
        ['Nível de Estresse', f"{user_data['avg_stress']:.1f}", get_interpretation(user_data['avg_stress'], 'stress')['label']],
    ]
    
    metrics_table = Table(metrics_data)
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(metrics_table)
    story.append(Spacer(1, 12))
    
    # Análise e recomendações
    if 'analysis' in user_data:
        analysis_title = Paragraph("Análise e Recomendações", styles['Heading2'])
        story.append(analysis_title)
        story.append(Spacer(1, 6))
        
        for item in user_data['analysis']:
            bullet = Paragraph(f"• {item}", styles['Normal'])
            story.append(bullet)
            story.append(Spacer(1, 6))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

def export_to_excel(data, filename='athlete_data.xlsx'):
    """
    Exporta dados para Excel
    """
    buffer = BytesIO()
    writer = pd.ExcelWriter(buffer, engine='xlsxwriter')
    
    # Criar planilhas para cada tipo de dado
    if 'readiness' in data:
        df_readiness = pd.DataFrame(data['readiness'])
        df_readiness.to_excel(writer, sheet_name='Prontidão', index=False)
    
    if 'training' in data:
        df_training = pd.DataFrame(data['training'])
        df_training.to_excel(writer, sheet_name='Treino', index=False)
    
    if 'psychological' in data:
        df_psychological = pd.DataFrame(data['psychological'])
        df_psychological.to_excel(writer, sheet_name='Psicológico', index=False)
    
    # Criar planilha de resumo
    if 'summary' in data:
        df_summary = pd.DataFrame(data['summary'])
        df_summary.to_excel(writer, sheet_name='Resumo', index=False)
    
    writer.close()
    buffer.seek(0)
    return buffer

def create_performance_chart(data, chart_type='line'):
    """
    Cria gráficos de performance
    """
    plt.figure(figsize=(12, 8))
    
    if chart_type == 'line':
        plt.plot(data['dates'], data['readiness'], label='Prontidão', marker='o')
        plt.plot(data['dates'], data['training_load'], label='Carga de Treino', marker='s')
        plt.plot(data['dates'], data['stress'], label='Estresse', marker='^')
    
    elif chart_type == 'correlation':
        plt.scatter(data['readiness'], data['training_load'], alpha=0.6)
        plt.xlabel('Prontidão')
        plt.ylabel('Carga de Treino')
        plt.title('Correlação entre Prontidão e Carga de Treino')
    
    elif chart_type == 'training_zones':
        zones = ['Recuperação', 'Aeróbico', 'Anaeróbico', 'Máximo']
        values = [data['zone_distribution'][zone] for zone in zones]
        plt.pie(values, labels=zones, autopct='%1.1f%%')
        plt.title('Distribuição de Zonas de Treino')
    
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    
    # Converter para base64 para embedding
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    return f"data:image/png;base64,{image_base64}"

def calculate_correlations(data):
    """
    Calcula correlações entre diferentes métricas
    """
    df = pd.DataFrame(data)
    
    # Calcular matriz de correlação
    correlation_matrix = df.corr()
    
    # Criar visualização
    plt.figure(figsize=(10, 8))
    sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', center=0, 
                fmt='.2f', square=True, linewidths=0.5)
    plt.title('Matriz de Correlação - Métricas do Atleta')
    plt.tight_layout()
    
    # Converter para base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    # Retornar correlações significativas e gráfico
    significant_correlations = []
    for i in range(len(correlation_matrix.columns)):
        for j in range(i+1, len(correlation_matrix.columns)):
            corr_value = correlation_matrix.iloc[i, j]
            if abs(corr_value) > 0.5:  # Correlação significativa
                significant_correlations.append({
                    'metric1': correlation_matrix.columns[i],
                    'metric2': correlation_matrix.columns[j],
                    'correlation': corr_value,
                    'strength': 'Forte' if abs(corr_value) > 0.7 else 'Moderada',
                    'direction': 'Positiva' if corr_value > 0 else 'Negativa'
                })
    
    return {
        'matrix': correlation_matrix.to_dict(),
        'significant': significant_correlations,
        'chart': f"data:image/png;base64,{image_base64}"
    }

def generate_weekly_report(user_id, start_date, end_date, db):
    """
    Gera relatório semanal completo
    """
    from app import ReadinessAssessment, TrainingAssessment, PsychologicalAssessment
    
    # Buscar dados do período
    readiness_data = ReadinessAssessment.query.filter(
        ReadinessAssessment.user_id == user_id,
        ReadinessAssessment.date.between(start_date, end_date)
    ).all()
    
    training_data = TrainingAssessment.query.filter(
        TrainingAssessment.user_id == user_id,
        TrainingAssessment.date.between(start_date, end_date)
    ).all()
    
    psychological_data = PsychologicalAssessment.query.filter(
        PsychologicalAssessment.user_id == user_id,
        PsychologicalAssessment.date.between(start_date, end_date)
    ).all()
    
    # Calcular métricas agregadas
    report = {
        'period': {
            'start': start_date.strftime('%Y-%m-%d'),
            'end': end_date.strftime('%Y-%m-%d')
        },
        'readiness': {
            'average': np.mean([r.readiness_score for r in readiness_data]) if readiness_data else 0,
            'best_day': max(readiness_data, key=lambda x: x.readiness_score).date.strftime('%Y-%m-%d') if readiness_data else None,
            'worst_day': min(readiness_data, key=lambda x: x.readiness_score).date.strftime('%Y-%m-%d') if readiness_data else None,
            'trend': 'increasing' if len(readiness_data) > 1 and readiness_data[-1].readiness_score > readiness_data[0].readiness_score else 'decreasing'
        },
        'training': {
            'total_load': sum([t.training_load for t in training_data]),
            'total_duration': sum([t.training_duration for t in training_data]),
            'average_rpe': np.mean([t.rpe for t in training_data]) if training_data else 0,
            'types': {},
            'zones': {}
        },
        'psychological': {
            'stress_average': np.mean([p.stress_score for p in psychological_data]) if psychological_data else 0,
            'flow_average': np.mean([p.flow_score for p in psychological_data]) if psychological_data else 0,
            'confidence_average': np.mean([p.confidence_level for p in psychological_data]) if psychological_data else 0
        },
        'recommendations': [],
        'highlights': []
    }
    
    # Análise de tipos de treino
    for t in training_data:
        report['training']['types'][t.training_type] = report['training']['types'].get(t.training_type, 0) + 1
        report['training']['zones'][t.intensity_zone] = report['training']['zones'].get(t.intensity_zone, 0) + 1
    
    # Gerar recomendações baseadas nos dados
    if report['readiness']['average'] < 60:
        report['recommendations'].append("A prontidão média está baixa. Considere aumentar o tempo de recuperação e melhorar a qualidade do sono.")
    
    if report['training']['total_load'] > 0 and report['readiness']['average'] < report['training']['total_load'] / 10:
        report['recommendations'].append("A carga de treino pode estar alta em relação à sua prontidão. Considere ajustar o volume ou intensidade.")
    
    if report['psychological']['stress_average'] > 15:
        report['recommendations'].append("Níveis de estresse estão elevados. Pratique técnicas de relaxamento e considere buscar apoio profissional.")
    
    # Highlights semanais
    if readiness_data:
        best_readiness = max(readiness_data, key=lambda x: x.readiness_score)
        report['highlights'].append(f"Melhor prontidão: {best_readiness.readiness_score:.1f} em {best_readiness.date.strftime('%d/%m')}")
    
    if training_data:
        heaviest_session = max(training_data, key=lambda x: x.training_load)
        report['highlights'].append(f"Sessão mais intensa: {heaviest_session.training_load:.1f} em {heaviest_session.date.strftime('%d/%m')}")
    
    return report

def create_performance_management_chart(data):
    """
    Cria o gráfico de Performance Management Chart (PMC)
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    
    dates = [d['date'] for d in data]
    ctl = [d['ctl'] for d in data]
    atl = [d['atl'] for d in data]
    tsb = [d['tsb'] for d in data]
    
    # Plot CTL e ATL
    ax.plot(dates, ctl, label='CTL (Fitness)', color='blue', linewidth=2)
    ax.plot(dates, atl, label='ATL (Fatigue)', color='orange', linewidth=2)
    
    # Plot TSB como área preenchida
    ax2 = ax.twinx()
    ax2.fill_between(dates, 0, tsb, where=(np.array(tsb) >= 0), 
                     color='green', alpha=0.3, label='TSB Positivo (Descansado)')
    ax2.fill_between(dates, 0, tsb, where=(np.array(tsb) < 0), 
                     color='red', alpha=0.3, label='TSB Negativo (Fatigado)')
    ax2.plot(dates, tsb, color='black', linewidth=1, linestyle='--')
    
    # Configurações
    ax.set_xlabel('Data')
    ax.set_ylabel('CTL / ATL')
    ax2.set_ylabel('TSB')
    ax.set_title('Performance Management Chart (CTL, ATL, TSB)')
    
    # Legendas
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    # Grid
    ax.grid(True, alpha=0.3)
    
    # Formato de data
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Converter para base64
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=300, bbox_inches='tight')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    return f"data:image/png;base64,{image_base64}"

def get_color_scale(value, min_val, max_val, scale_type='viridis'):
    """
    Retorna uma cor baseada no valor dentro de uma escala
    """
    import matplotlib.cm as cm
    
    normalized = (value - min_val) / (max_val - min_val)
    normalized = max(0, min(1, normalized))  # Garantir que está entre 0 e 1
    
    if scale_type == 'viridis':
        colormap = cm.viridis
    elif scale_type == 'RdYlGn':
        colormap = cm.RdYlGn
    elif scale_type == 'coolwarm':
        colormap = cm.coolwarm
    else:
        colormap = cm.viridis
    
    color = colormap(normalized)
    
    # Converter para hex
    return '#' + ''.join([format(int(c*255), '02x') for c in color[:3]])

def calculate_training_zones_distribution(training_data):
    """
    Calcula a distribuição de zonas de treinamento
    """
    zones = {
        'Low': 0,
        'Moderate': 0,
        'High': 0,
        'Very High': 0
    }
    
    total_duration = 0
    
    for session in training_data:
        duration = session['duration']
        zone = session['intensity_zone']
        
        if zone in zones:
            zones[zone] += duration
        
        total_duration += duration
    
    # Converter para percentuais
    for zone in zones:
        if total_duration > 0:
            zones[zone] = (zones[zone] / total_duration) * 100
        else:
            zones[zone] = 0
    
    return zones

def generate_insights(user_data):
    """
    Gera insights automáticos baseados nos dados do usuário
    """
    insights = []
    
    # Análise de prontidão
    recent_readiness = user_data.get('recent_readiness', [])
    if recent_readiness:
        avg_readiness = sum(recent_readiness) / len(recent_readiness)
        if avg_readiness < 60:
            insights.append({
                'type': 'warning',
                'title': 'Prontidão Baixa',
                'message': f'Sua prontidão média está em {avg_readiness:.1f}. Considere aumentar o descanso.',
                'category': 'readiness'
            })
        elif avg_readiness > 80:
            insights.append({
                'type': 'success',
                'title': 'Excelente Prontidão',
                'message': f'Sua prontidão está em {avg_readiness:.1f}. Ótimo momento para treinar intensamente.',
                'category': 'readiness'
            })
    
    # Análise de carga de treino
    recent_loads = user_data.get('recent_training_loads', [])
    if len(recent_loads) >= 7:
        last_week = sum(recent_loads[-7:])
        prev_week = sum(recent_loads[-14:-7]) if len(recent_loads) >= 14 else 0
        
        if prev_week > 0:
            change = ((last_week - prev_week) / prev_week) * 100
            if change > 30:
                insights.append({
                    'type': 'warning',
                    'title': 'Aumento Brusco de Carga',
                    'message': f'Sua carga aumentou {change:.1f}% na última semana. Monitore sinais de overtraining.',
                    'category': 'training'
                })
            elif change < -30:
                insights.append({
                    'type': 'info',
                    'title': 'Redução Significativa',
                    'message': f'Sua carga diminuiu {abs(change):.1f}% na última semana. Bom período para recuperação.',
                    'category': 'training'
                })
    
    # Análise psicológica
    recent_stress = user_data.get('recent_stress', [])
    if recent_stress:
        avg_stress = sum(recent_stress) / len(recent_stress)
        if avg_stress > 15:
            insights.append({
                'type': 'warning',
                'title': 'Estresse Elevado',
                'message': 'Seus níveis de estresse estão acima do normal. Pratique técnicas de relaxamento.',
                'category': 'psychological'
            })
    
    # Análise de correlações
    if user_data.get('correlations'):
        high_correlations = [c for c in user_data['correlations'] if abs(c['correlation']) > 0.7]
        for corr in high_correlations:
            if corr['correlation'] < -0.7 and 'sleep' in corr['metric1'].lower() and 'stress' in corr['metric2'].lower():
                insights.append({
                    'type': 'info',
                    'title': 'Relação Sono-Estresse',
                    'message': 'Existe forte correlação negativa entre qualidade do sono e nível de estresse.',
                    'category': 'correlation'
                })
    
    return insights