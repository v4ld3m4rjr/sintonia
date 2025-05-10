from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from datetime import datetime, timedelta
from utils import calculate_readiness_score, get_interpretation
import json

readiness_bp = Blueprint('readiness', __name__)

@readiness_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('readiness/index.html')

@readiness_bp.route('/assessment', methods=['GET', 'POST'])
def assessment():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        from app import db, ReadinessAssessment
        
        # Coletar dados do formulário
        data = {
            'sleep_quality': int(request.form['sleep_quality']),
            'sleep_duration': float(request.form['sleep_duration']),
            'stress_level': int(request.form['stress_level']),
            'muscle_soreness': int(request.form['muscle_soreness']),
            'energy_level': int(request.form['energy_level']),
            'motivation': int(request.form['motivation']),
            'nutrition_quality': int(request.form['nutrition_quality']),
            'hydration': int(request.form['hydration'])
        }
        
        # Calcular score de prontidão
        readiness_score = calculate_readiness_score(data)
        
        # Salvar no banco
        assessment = ReadinessAssessment(
            user_id=session['user_id'],
            date=request.form.get('date', datetime.now().date()),
            sleep_quality=data['sleep_quality'],
            sleep_duration=data['sleep_duration'],
            stress_level=data['stress_level'],
            muscle_soreness=data['muscle_soreness'],
            energy_level=data['energy_level'],
            motivation=data['motivation'],
            nutrition_quality=data['nutrition_quality'],
            hydration=data['hydration'],
            readiness_score=readiness_score,
            notes=request.form.get('notes', '')
        )
        
        db.session.add(assessment)
        db.session.commit()
        
        flash(f'Avaliação salva! Seu score de prontidão é: {readiness_score}')
        return redirect(url_for('readiness.results', assessment_id=assessment.id))
    
    return render_template('readiness/assessment.html')

@readiness_bp.route('/results/<int:assessment_id>')
def results(assessment_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    from app import db, ReadinessAssessment
    
    assessment = ReadinessAssessment.query.get_or_404(assessment_id)
    
    if assessment.user_id != session['user_id']:
        flash('Você não tem permissão para visualizar esta avaliação.')
        return redirect(url_for('readiness.index'))
    
    # Obter interpretação
    interpretation = get_interpretation(assessment.readiness_score, 'readiness')
    
    # Criar gráfico de radar para os componentes
    components = {
        'Qualidade do Sono': assessment.sleep_quality,
        'Duração do Sono': min(assessment.sleep_duration / 8 * 5, 5),  # Normalizar para escala 1-5
        'Nível de Estresse': 6 - assessment.stress_level,  # Inverter escala
        'Dor Muscular': 6 - assessment.muscle_soreness,  # Inverter escala
        'Nível de Energia': assessment.energy_level,
        'Motivação': assessment.motivation,
        'Qualidade Nutricional': assessment.nutrition_quality,
        'Hidratação': assessment.hydration
    }
    
    # Buscar histórico dos últimos 30 dias
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    historical_data = ReadinessAssessment.query.filter(
        ReadinessAssessment.user_id == session['user_id'],
        ReadinessAssessment.date >= thirty_days_ago
    ).order_by(ReadinessAssessment.date).all()
    
    # Preparar dados para gráfico
    history_chart_data = {
        'dates': [h.date.strftime('%Y-%m-%d') for h in historical_data],
        'scores': [h.readiness_score for h in historical_data],
        'sleep_quality': [h.sleep_quality for h in historical_data],
        'energy_level': [h.energy_level for h in historical_data],
        'stress_level': [h.stress_level for h in historical_data]
    }
    
    return render_template('readiness/results.html',
                         assessment=assessment,
                         interpretation=interpretation,
                         components=components,
                         history_data=history_chart_data)

@readiness_bp.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    from app import db, ReadinessAssessment
    
    # Obter período do filtro
    days = request.args.get('days', 30, type=int)
    start_date = datetime.now().date() - timedelta(days=days)
    
    # Buscar dados
    assessments = ReadinessAssessment.query.filter(
        ReadinessAssessment.user_id == session['user_id'],
        ReadinessAssessment.date >= start_date
    ).order_by(ReadinessAssessment.date.desc()).all()
    
    # Calcular estatísticas
    if assessments:
        stats = {
            'average_score': sum(a.readiness_score for a in assessments) / len(assessments),
            'highest_score': max(a.readiness_score for a in assessments),
            'lowest_score': min(a.readiness_score for a in assessments),
            'total_assessments': len(assessments),
            'average_sleep': sum(a.sleep_duration for a in assessments) / len(assessments),
            'average_stress': sum(a.stress_level for a in assessments) / len(assessments),
            'average_energy': sum(a.energy_level for a in assessments) / len(assessments)
        }
    else:
        stats = {}
    
    return render_template('readiness/history.html', 
                         assessments=assessments,
                         stats=stats,
                         days=days)

@readiness_bp.route('/api/chart-data')
def api_chart_data():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    from app import db, ReadinessAssessment
    
    # Obter parâmetros
    days = request.args.get('days', 30, type=int)
    start_date = datetime.now().date() - timedelta(days=days)
    
    # Buscar dados
    assessments = ReadinessAssessment.query.filter(
        ReadinessAssessment.user_id == session['user_id'],
        ReadinessAssessment.date >= start_date
    ).order_by(ReadinessAssessment.date).all()
    
    # Preparar dados para diferentes tipos de gráficos
    data = {
        'timeline': {
            'dates': [a.date.strftime('%Y-%m-%d') for a in assessments],
            'readiness_scores': [a.readiness_score for a in assessments],
            'sleep_quality': [a.sleep_quality for a in assessments],
            'sleep_duration': [a.sleep_duration for a in assessments],
            'stress_level': [a.stress_level for a in assessments],
            'energy_level': [a.energy_level for a in assessments],
            'muscle_soreness': [a.muscle_soreness for a in assessments]
        },
        'averages': {
            'readiness': sum(a.readiness_score for a in assessments) / len(assessments) if assessments else 0,
            'sleep_quality': sum(a.sleep_quality for a in assessments) / len(assessments) if assessments else 0,
            'sleep_duration': sum(a.sleep_duration for a in assessments) / len(assessments) if assessments else 0,
            'stress_level': sum(a.stress_level for a in assessments) / len(assessments) if assessments else 0,
            'energy_level': sum(a.energy_level for a in assessments) / len(assessments) if assessments else 0
        },
        'trends': {
            'readiness': 'stable',  # Pode ser 'increasing', 'decreasing', 'stable'
            'sleep': 'stable',
            'stress': 'stable'
        }
    }
    
    # Calcular tendências
    if len(assessments) >= 7:
        recent_week = assessments[-7:]
        previous_week = assessments[-14:-7] if len(assessments) >= 14 else []
        
        if previous_week:
            recent_avg = sum(a.readiness_score for a in recent_week) / len(recent_week)
            previous_avg = sum(a.readiness_score for a in previous_week) / len(previous_week)
            
            if recent_avg > previous_avg * 1.1:
                data['trends']['readiness'] = 'increasing'
            elif recent_avg < previous_avg * 0.9:
                data['trends']['readiness'] = 'decreasing'
    
    return jsonify(data)

@readiness_bp.route('/recommendations')
def recommendations():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    from app import db, ReadinessAssessment
    
    # Buscar última avaliação
    latest_assessment = ReadinessAssessment.query.filter(
        ReadinessAssessment.user_id == session['user_id']
    ).order_by(ReadinessAssessment.date.desc()).first()
    
    recommendations = []
    
    if latest_assessment:
        score = latest_assessment.readiness_score
        
        # Recomendações baseadas no score geral
        if score < 50:
            recommendations.append({
                'category': 'Geral',
                'title': 'Foco em Recuperação',
                'description': 'Seus níveis de prontidão estão baixos. Priorize descanso e recuperação.',
                'actions': [
                    'Reduzir intensidade dos treinos',
                    'Aumentar tempo de sono (8+ horas)',
                    'Praticar atividades relaxantes'
                ]
            })
        elif score > 80:
            recommendations.append({
                'category': 'Geral',
                'title': 'Aproveite a Alta Prontidão',
                'description': 'Excelente momento para treinos intensos ou competições.',
                'actions': [
                    'Agendar treinos de alta intensidade',
                    'Manter rotina de sono consistente',
                    'Maximizar recuperação pós-treino'
                ]
            })
        
        # Recomendações específicas
        if latest_assessment.sleep_quality < 3:
            recommendations.append({
                'category': 'Sono',
                'title': 'Melhorar Qualidade do Sono',
                'description': 'Sua qualidade de sono precisa de atenção.',
                'actions': [
                    'Criar rotina relaxante antes de dormir',
                    'Evitar telas 1 hora antes de dormir',
                    'Manter ambiente escuro e fresco'
                ]
            })
        
        if latest_assessment.sleep_duration < 7:
            recommendations.append({
                'category': 'Sono',
                'title': 'Aumentar Duração do Sono',
                'description': 'Você está dormindo menos que o recomendado.',
                'actions': [
                    'Deitar mais cedo',
                    'Reduzir cafeína após 14h',
                    'Criar horário consistente de sono'
                ]
            })
        
        if latest_assessment.stress_level > 4:
            recommendations.append({
                'category': 'Estresse',
                'title': 'Gerenciar Estresse',
                'description': 'Seus níveis de estresse estão elevados.',
                'actions': [
                    'Praticar meditação ou mindfulness',
                    'Fazer exercícios respiratórios',
                    'Identificar e gerenciar fontes de estresse'
                ]
            })
        
        if latest_assessment.muscle_soreness > 4:
            recommendations.append({
                'category': 'Recuperação',
                'title': 'Recuperação Muscular',
                'description': 'Você está com dor muscular significativa.',
                'actions': [
                    'Fazer alongamentos suaves',
                    'Usar foam roller',
                    'Considerar massagem ou banho quente'
                ]
            })
        
        if latest_assessment.nutrition_quality < 3:
            recommendations.append({
                'category': 'Nutrição',
                'title': 'Melhorar Alimentação',
                'description': 'Sua nutrição pode estar impactando sua prontidão.',
                'actions': [
                    'Planejar refeições com antecedência',
                    'Incluir mais frutas e vegetais',
                    'Garantir proteína adequada'
                ]
            })
        
        if latest_assessment.hydration < 3:
            recommendations.append({
                'category': 'Hidratação',
                'title': 'Aumentar Hidratação',
                'description': 'Sua hidratação está insuficiente.',
                'actions': [
                    'Carregar garrafa de água sempre',
                    'Beber água regularmente, não apenas quando com sede',
                    'Incluir alimentos ricos em água'
                ]
            })
    
    return render_template('readiness/recommendations.html', 
                         recommendations=recommendations,
                         assessment=latest_assessment)

@readiness_bp.route('/export')
def export():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Implementar exportação de dados de prontidão
    # Pode ser PDF, Excel ou CSV
    pass