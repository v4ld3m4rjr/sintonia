from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from datetime import datetime, timedelta
from utils import calculate_training_metrics, create_performance_management_chart
import json

training_bp = Blueprint('training', __name__)

@training_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('training/index.html')

@training_bp.route('/assessment', methods=['GET', 'POST'])
def assessment():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        from app import db, TrainingAssessment
        
        # Coletar dados do formulário
        training_duration = float(request.form['training_duration'])
        rpe = int(request.form['rpe'])
        training_load = training_duration * rpe
        
        assessment = TrainingAssessment(
            user_id=session['user_id'],
            date=request.form.get('date', datetime.now().date()),
            training_load=training_load,
            training_duration=training_duration,
            rpe=rpe,
            intensity_zone=request.form['intensity_zone'],
            training_type=request.form['training_type'],
            fatigue_level=int(request.form['fatigue_level']),
            performance_feeling=int(request.form['performance_feeling']),
            notes=request.form.get('notes', '')
        )
        
        # Calcular CTL e ATL
        historical_data = TrainingAssessment.query.filter(
            TrainingAssessment.user_id == session['user_id']
        ).order_by(TrainingAssessment.date).all()
        
        # Adicionar novo assessment aos dados históricos para cálculo
        all_assessments = historical_data + [assessment]
        metrics_df = calculate_training_metrics(all_assessments)
        
        # Pegar os valores mais recentes
        if not metrics_df.empty:
            latest_metrics = metrics_df.iloc[-1]
            assessment.chronic_load = latest_metrics['CTL']
            assessment.acute_load = latest_metrics['ATL']
            assessment.training_strain = latest_metrics['Ratio']
        
        db.session.add(assessment)
        db.session.commit()
        
        flash(f'Treino registrado! Carga: {training_load:.1f}, CTL: {assessment.chronic_load:.1f}, ATL: {assessment.acute_load:.1f}')
        return redirect(url_for('training.results', assessment_id=assessment.id))
    
    return render_template('training/assessment.html')

@training_bp.route('/results/<int:assessment_id>')
def results(assessment_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    from app import db, TrainingAssessment
    
    assessment = TrainingAssessment.query.get_or_404(assessment_id)
    
    if assessment.user_id != session['user_id']:
        flash('Você não tem permissão para visualizar esta avaliação.')
        return redirect(url_for('training.index'))
    
    # Obter dados históricos para análise
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    historical_data = TrainingAssessment.query.filter(
        TrainingAssessment.user_id == session['user_id'],
        TrainingAssessment.date >= thirty_days_ago
    ).order_by(TrainingAssessment.date).all()
    
    # Preparar dados para gráficos
    history_chart_data = {
        'dates': [h.date.strftime('%Y-%m-%d') for h in historical_data],
        'training_loads': [h.training_load for h in historical_data],
        'ctl': [h.chronic_load for h in historical_data if h.chronic_load],
        'atl': [h.acute_load for h in historical_data if h.acute_load],
        'tsb': [(h.chronic_load - h.acute_load) for h in historical_data if h.chronic_load and h.acute_load],
        'rpe': [h.rpe for h in historical_data],
        'fatigue': [h.fatigue_level for h in historical_data],
        'performance': [h.performance_feeling for h in historical_data]
    }
    
    # Criar gráfico PMC
    pmc_data = [
        {
            'date': h.date,
            'ctl': h.chronic_load or 0,
            'atl': h.acute_load or 0,
            'tsb': (h.chronic_load or 0) - (h.acute_load or 0)
        }
        for h in historical_data
    ]
    
    pmc_chart = create_performance_management_chart(pmc_data) if pmc_data else None
    
    # Análise e recomendações
    analysis = {
        'training_strain': assessment.training_strain,
        'strain_interpretation': '',
        'fitness_trend': '',
        'fatigue_status': '',
        'recommendations': []
    }
    
    if assessment.training_strain:
        if assessment.training_strain > 1.5:
            analysis['strain_interpretation'] = 'Alto risco de overtraining'
            analysis['recommendations'].append('Reduzir volume de treino')
            analysis['recommendations'].append('Aumentar tempo de recuperação')
        elif assessment.training_strain > 1.2:
            analysis['strain_interpretation'] = 'Carga de treino pesada'
            analysis['recommendations'].append('Monitorar sinais de fadiga')
            analysis['recommendations'].append('Manter boa qualidade de sono')
        elif assessment.training_strain < 0.8:
            analysis['strain_interpretation'] = 'Carga de treino leve'
            analysis['recommendations'].append('Considerar aumentar intensidade')
            analysis['recommendations'].append('Boa oportunidade para treinamento de alta qualidade')
        else:
            analysis['strain_interpretation'] = 'Carga de treino equilibrada'
            analysis['recommendations'].append('Manter consistência')
    
    # Status de fadiga
    if assessment.fatigue_level >= 8:
        analysis['fatigue_status'] = 'Alta fadiga'
        analysis['recommendations'].append('Priorizar recuperação ativa')
    elif assessment.fatigue_level >= 6:
        analysis['fatigue_status'] = 'Fadiga moderada'
        analysis['recommendations'].append('Monitorar intensidade dos próximos treinos')
    else:
        analysis['fatigue_status'] = 'Fadiga baixa'
        analysis['recommendations'].append('Bom momento para treinar')
    
    return render_template('training/results.html',
                         assessment=assessment,
                         history_data=history_chart_data,
                         pmc_chart=pmc_chart,
                         analysis=analysis)

@training_bp.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    from app import db, TrainingAssessment
    
    # Obter período do filtro
    days = request.args.get('days', 30, type=int)
    start_date = datetime.now().date() - timedelta(days=days)
    
    # Buscar dados
    assessments = TrainingAssessment.query.filter(
        TrainingAssessment.user_id == session['user_id'],
        TrainingAssessment.date >= start_date
    ).order_by(TrainingAssessment.date.desc()).all()
    
    # Calcular estatísticas
    if assessments:
        stats = {
            'total_load': sum(a.training_load for a in assessments),
            'average_rpe': sum(a.rpe for a in assessments) / len(assessments),
            'total_duration': sum(a.training_duration for a in assessments),
            'total_sessions': len(assessments),
            'average_ctl': sum(a.chronic_load for a in assessments if a.chronic_load) / len([a for a in assessments if a.chronic_load]) if any(a.chronic_load for a in assessments) else 0,
            'average_atl': sum(a.acute_load for a in assessments if a.acute_load) / len([a for a in assessments if a.acute_load]) if any(a.acute_load for a in assessments) else 0,
            'training_types': {},
            'intensity_zones': {}
        }
        
        # Contar tipos de treino e zonas
        for assessment in assessments:
            stats['training_types'][assessment.training_type] = stats['training_types'].get(assessment.training_type, 0) + 1
            stats['intensity_zones'][assessment.intensity_zone] = stats['intensity_zones'].get(assessment.intensity_zone, 0) + 1
    else:
        stats = {}
    
    return render_template('training/history.html', 
                         assessments=assessments,
                         stats=stats,
                         days=days)

@training_bp.route('/performance-chart')
def performance_chart():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    from app import db, TrainingAssessment
    
    # Buscar dados dos últimos 90 dias
    ninety_days_ago = datetime.now().date() - timedelta(days=90)
    assessments = TrainingAssessment.query.filter(
        TrainingAssessment.user_id == session['user_id'],
        TrainingAssessment.date >= ninety_days_ago
    ).order_by(TrainingAssessment.date).all()
    
    # Preparar dados para PMC
    pmc_data = [
        {
            'date': a.date,
            'ctl': a.chronic_load or 0,
            'atl': a.acute_load or 0,
            'tsb': (a.chronic_load or 0) - (a.acute_load or 0)
        }
        for a in assessments if a.chronic_load and a.acute_load
    ]
    
    pmc_chart = create_performance_management_chart(pmc_data) if pmc_data else None
    
    # Análise de tendências
    trends = {
        'fitness_trend': '',
        'fatigue_trend': '',
        'form_trend': '',
        'training_load_trend': ''
    }
    
    if len(assessments) >= 14:
        recent_ctl = [a.chronic_load for a in assessments[-7:] if a.chronic_load]
        previous_ctl = [a.chronic_load for a in assessments[-14:-7] if a.chronic_load]
        
        if recent_ctl and previous_ctl:
            if sum(recent_ctl) / len(recent_ctl) > sum(previous_ctl) / len(previous_ctl) * 1.05:
                trends['fitness_trend'] = 'Aumentando'
            elif sum(recent_ctl) / len(recent_ctl) < sum(previous_ctl) / len(previous_ctl) * 0.95:
                trends['fitness_trend'] = 'Diminuindo'
            else:
                trends['fitness_trend'] = 'Estável'
    
    return render_template('training/performance_chart.html',
                         pmc_chart=pmc_chart,
                         trends=trends,
                         assessments=assessments)

@training_bp.route('/api/pmc-data')
def api_pmc_data():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    from app import db, TrainingAssessment
    
    # Obter parâmetros
    days = request.args.get('days', 90, type=int)
    start_date = datetime.now().date() - timedelta(days=days)
    
    # Buscar dados
    assessments = TrainingAssessment.query.filter(
        TrainingAssessment.user_id == session['user_id'],
        TrainingAssessment.date >= start_date
    ).order_by(TrainingAssessment.date).all()
    
    # Preparar dados para retorno
    data = {
        'dates': [a.date.strftime('%Y-%m-%d') for a in assessments],
        'training_loads': [a.training_load for a in assessments],
        'ctl': [a.chronic_load for a in assessments],
        'atl': [a.acute_load for a in assessments],
        'tsb': [(a.chronic_load - a.acute_load) if a.chronic_load and a.acute_load else None for a in assessments],
        'rpe': [a.rpe for a in assessments],
        'fatigue': [a.fatigue_level for a in assessments],
        'performance': [a.performance_feeling for a in assessments]
    }
    
    return jsonify(data)

@training_bp.route('/weekly-plan', methods=['GET', 'POST'])
def weekly_plan():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    from app import db, TrainingSession
    
    if request.method == 'POST':
        # Criar nova sessão de treino
        session_data = TrainingSession(
            user_id=session['user_id'],
            date=datetime.strptime(request.form['date'], '%Y-%m-%d'),
            title=request.form['title'],
            description=request.form.get('description', ''),
            training_type=request.form['training_type'],
            planned_duration=float(request.form['planned_duration'])
        )
        
        db.session.add(session_data)
        db.session.commit()
        
        flash('Treino agendado com sucesso!')
        return redirect(url_for('training.weekly_plan'))
    
    # Buscar treinos da semana atual
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    planned_sessions = TrainingSession.query.filter(
        TrainingSession.user_id == session['user_id'],
        TrainingSession.date >= start_of_week,
        TrainingSession.date <= end_of_week
    ).order_by(TrainingSession.date).all()
    
    # Buscar treinos completados da semana
    completed_sessions = TrainingAssessment.query.filter(
        TrainingAssessment.user_id == session['user_id'],
        TrainingAssessment.date >= start_of_week,
        TrainingAssessment.date <= end_of_week
    ).order_by(TrainingAssessment.date).all()
    
    return render_template('training/weekly_plan.html',
                         planned_sessions=planned_sessions,
                         completed_sessions=completed_sessions,
                         start_of_week=start_of_week,
                         end_of_week=end_of_week)

@training_bp.route('/recommendations')
def recommendations():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    from app import db, TrainingAssessment, ReadinessAssessment
    
    # Buscar dados recentes
    recent_trainings = TrainingAssessment.query.filter(
        TrainingAssessment.user_id == session['user_id']
    ).order_by(TrainingAssessment.date.desc()).limit(7).all()
    
    recent_readiness = ReadinessAssessment.query.filter(
        ReadinessAssessment.user_id == session['user_id']
    ).order_by(ReadinessAssessment.date.desc()).first()
    
    recommendations = []
    
    # Análise baseada em CTL/ATL
    if recent_trainings and recent_trainings[0].chronic_load and recent_trainings[0].acute_load:
        latest = recent_trainings[0]
        tsb = latest.chronic_load - latest.acute_load
        ratio = latest.acute_load / latest.chronic_load if latest.chronic_load > 0 else 0
        
        if tsb > 15:
            recommendations.append({
                'category': 'Forma',
                'title': 'Oportunidade de Performance',
                'description': f'Seu TSB está em {tsb:.1f}, indicando boa forma.',
                'actions': [
                    'Agendar sessões de alta intensidade',
                    'Considerar competições ou testes de performance',
                    'Manter consistência nos treinos'
                ]
            })
        elif tsb < -15:
            recommendations.append({
                'category': 'Recuperação',
                'title': 'Risco de Overtraining',
                'description': f'Seu TSB está em {tsb:.1f}, indicando alta fadiga.',
                'actions': [
                    'Reduzir volume de treino',
                    'Adicionar dias de descanso completo',
                    'Focar em recuperação ativa'
                ]
            })
        
        if ratio > 1.4:
            recommendations.append({
                'category': 'Carga',
                'title': 'Carga Aguda Elevada',
                'description': f'Ratio ATL/CTL está em {ratio:.2f}.',
                'actions': [
                    'Evitar aumentos súbitos de volume',
                    'Distribuir carga ao longo da semana',
                    'Monitorar sinais de fadiga'
                ]
            })
    
    # Análise baseada em prontidão
    if recent_readiness:
        if recent_readiness.readiness_score < 60:
            recommendations.append({
                'category': 'Prontidão',
                'title': 'Prontidão Baixa',
                'description': f'Score de prontidão: {recent_readiness.readiness_score:.1f}',
                'actions': [
                    'Priorizar sono de qualidade',
                    'Reduzir intensidade dos treinos',
                    'Revisar nutrição e hidratação'
                ]
            })
    
    # Análise de tendências
    if len(recent_trainings) >= 7:
        recent_loads = [t.training_load for t in recent_trainings]
        avg_load = sum(recent_loads) / len(recent_loads)
        
        if avg_load < 50:
            recommendations.append({
                'category': 'Volume',
                'title': 'Volume Baixo',
                'description': f'Carga média semanal: {avg_load:.1f}',
                'actions': [
                    'Considerar aumentar gradualmente o volume',
                    'Adicionar sessões de baixa intensidade',
                    'Estabelecer base aeróbica'
                ]
            })
        elif avg_load > 150:
            recommendations.append({
                'category': 'Volume',
                'title': 'Volume Alto',
                'description': f'Carga média semanal: {avg_load:.1f}',
                'actions': [
                    'Monitorar sinais de fadiga crônica',
                    'Garantir recuperação adequada',
                    'Considerar semana de descarga'
                ]
            })
    
    return render_template('training/recommendations.html', 
                         recommendations=recommendations,
                         recent_trainings=recent_trainings,
                         recent_readiness=recent_readiness)