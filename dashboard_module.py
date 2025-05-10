from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from datetime import datetime, timedelta, date
from utils import (export_to_pdf, export_to_excel, create_performance_chart, 
                  calculate_correlations, generate_weekly_report, generate_insights,
                  create_performance_management_chart)
import json

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    from app import db, ReadinessAssessment, TrainingAssessment, PsychologicalAssessment
    
    user_id = session['user_id']
    today = datetime.now().date()
    
    # Data ranges
    seven_days_ago = today - timedelta(days=7)
    thirty_days_ago = today - timedelta(days=30)
    
    # Buscar dados para o dashboard
    recent_readiness = ReadinessAssessment.query.filter(
        ReadinessAssessment.user_id == user_id,
        ReadinessAssessment.date >= seven_days_ago
    ).order_by(ReadinessAssessment.date.desc()).all()
    
    recent_training = TrainingAssessment.query.filter(
        TrainingAssessment.user_id == user_id,
        TrainingAssessment.date >= seven_days_ago
    ).order_by(TrainingAssessment.date.desc()).all()
    
    recent_psychological = PsychologicalAssessment.query.filter(
        PsychologicalAssessment.user_id == user_id,
        PsychologicalAssessment.date >= seven_days_ago
    ).order_by(PsychologicalAssessment.date.desc()).all()
    
    # Calcular métricas principais
    metrics = {
        'current_readiness': recent_readiness[0].readiness_score if recent_readiness else 0,
        'avg_readiness_7d': sum([r.readiness_score for r in recent_readiness]) / len(recent_readiness) if recent_readiness else 0,
        'current_ctl': recent_training[0].chronic_load if recent_training and recent_training[0].chronic_load else 0,
        'current_atl': recent_training[0].acute_load if recent_training and recent_training[0].acute_load else 0,
        'current_tsb': (recent_training[0].chronic_load - recent_training[0].acute_load) if recent_training and recent_training[0].chronic_load and recent_training[0].acute_load else 0,
        'avg_stress_7d': sum([p.stress_score for p in recent_psychological]) / len(recent_psychological) if recent_psychological else 0,
        'avg_flow_7d': sum([p.flow_score for p in recent_psychological]) / len(recent_psychological) if recent_psychological else 0,
        'total_training_load_7d': sum([t.training_load for t in recent_training]),
        'total_training_time_7d': sum([t.training_duration for t in recent_training]),
    }
    
    # Buscar dados para gráficos
    chart_data = {
        'dates': [],
        'readiness': [],
        'training_load': [],
        'stress': [],
        'ctl': [],
        'atl': [],
        'tsb': []
    }
    
    # Combinar dados para os últimos 30 dias
    for i in range(30, -1, -1):
        current_date = today - timedelta(days=i)
        chart_data['dates'].append(current_date.strftime('%Y-%m-%d'))
        
        # Readiness
        day_readiness = next((r.readiness_score for r in recent_readiness if r.date == current_date), None)
        chart_data['readiness'].append(day_readiness)
        
        # Training
        day_training = next((t for t in recent_training if t.date == current_date), None)
        if day_training:
            chart_data['training_load'].append(day_training.training_load)
            chart_data['ctl'].append(day_training.chronic_load)
            chart_data['atl'].append(day_training.acute_load)
            chart_data['tsb'].append((day_training.chronic_load - day_training.acute_load) if day_training.chronic_load and day_training.acute_load else None)
        else:
            chart_data['training_load'].append(None)
            chart_data['ctl'].append(None)
            chart_data['atl'].append(None)
            chart_data['tsb'].append(None)
        
        # Psychological
        day_psych = next((p.stress_score for p in recent_psychological if p.date == current_date), None)
        chart_data['stress'].append(day_psych)
    
    # Gerar insights automáticos
    insights = generate_insights({
        'recent_readiness': [r.readiness_score for r in recent_readiness],
        'recent_training_loads': [t.training_load for t in recent_training],
        'recent_stress': [p.stress_score for p in recent_psychological]
    })
    
    # Próximas competições/eventos (placeholder)
    upcoming_events = []
    
    return render_template('dashboard/index.html',
                         metrics=metrics,
                         chart_data=chart_data,
                         insights=insights,
                         upcoming_events=upcoming_events)

@dashboard_bp.route('/analytics')
def analytics():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    from app import db, ReadinessAssessment, TrainingAssessment, PsychologicalAssessment
    
    user_id = session['user_id']
    
    # Obter período do filtro
    period = request.args.get('period', '30d')
    if period == '7d':
        days = 7
    elif period == '15d':
        days = 15
    elif period == '30d':
        days = 30
    elif period == '90d':
        days = 90
    elif period == '6m':
        days = 180
    else:
        days = 30
    
    start_date = datetime.now().date() - timedelta(days=days)
    
    # Buscar dados completos
    readiness_data = ReadinessAssessment.query.filter(
        ReadinessAssessment.user_id == user_id,
        ReadinessAssessment.date >= start_date
    ).order_by(ReadinessAssessment.date).all()
    
    training_data = TrainingAssessment.query.filter(
        TrainingAssessment.user_id == user_id,
        TrainingAssessment.date >= start_date
    ).order_by(TrainingAssessment.date).all()
    
    psychological_data = PsychologicalAssessment.query.filter(
        PsychologicalAssessment.user_id == user_id,
        PsychologicalAssessment.date >= start_date
    ).order_by(PsychologicalAssessment.date).all()
    
    # Preparar dados para análise
    combined_data = []
    for date_point in [(start_date + timedelta(days=i)) for i in range(days + 1)]:
        day_data = {'date': date_point}
        
        # Readiness
        readiness = next((r for r in readiness_data if r.date == date_point), None)
        if readiness:
            day_data['readiness'] = readiness.readiness_score
            day_data['sleep_quality'] = readiness.sleep_quality
            day_data['sleep_duration'] = readiness.sleep_duration
            day_data['stress_level'] = readiness.stress_level
            day_data['energy_level'] = readiness.energy_level
        
        # Training
        training = next((t for t in training_data if t.date == date_point), None)
        if training:
            day_data['training_load'] = training.training_load
            day_data['ctl'] = training.chronic_load
            day_data['atl'] = training.acute_load
            day_data['rpe'] = training.rpe
            day_data['training_duration'] = training.training_duration
        
        # Psychological
        psych = next((p for p in psychological_data if p.date == date_point), None)
        if psych:
            day_data['stress_score'] = psych.stress_score
            day_data['anxiety_score'] = psych.anxiety_score
            day_data['flow_score'] = psych.flow_score
            day_data['confidence'] = psych.confidence_level
        
        combined_data.append(day_data)
    
    # Calcular correlações
    correlation_data = {
        'readiness': [d.get('readiness', 0) for d in combined_data if 'readiness' in d],
        'training_load': [d.get('training_load', 0) for d in combined_data if 'training_load' in d],
        'stress': [d.get('stress_score', 0) for d in combined_data if 'stress_score' in d],
        'sleep_quality': [d.get('sleep_quality', 0) for d in combined_data if 'sleep_quality' in d],
        'flow': [d.get('flow_score', 0) for d in combined_data if 'flow_score' in d]
    }
    
    correlations = calculate_correlations(correlation_data)
    
    # Criar gráfico PMC
    pmc_data = [
        {
            'date': d['date'],
            'ctl': d.get('ctl', 0),
            'atl': d.get('atl', 0),
            'tsb': (d.get('ctl', 0) - d.get('atl', 0))
        }
        for d in combined_data if 'ctl' in d and 'atl' in d
    ]
    
    pmc_chart = create_performance_management_chart(pmc_data) if pmc_data else None
    
    # Estatísticas resumidas
    stats = {
        'total_assessments': {
            'readiness': len(readiness_data),
            'training': len(training_data),
            'psychological': len(psychological_data)
        },
        'averages': {
            'readiness': sum(d.get('readiness', 0) for d in combined_data if 'readiness' in d) / len([d for d in combined_data if 'readiness' in d]) if any('readiness' in d for d in combined_data) else 0,
            'training_load': sum(d.get('training_load', 0) for d in combined_data if 'training_load' in d) / len([d for d in combined_data if 'training_load' in d]) if any('training_load' in d for d in combined_data) else 0,
            'stress': sum(d.get('stress_score', 0) for d in combined_data if 'stress_score' in d) / len([d for d in combined_data if 'stress_score' in d]) if any('stress_score' in d for d in combined_data) else 0,
        },
        'trends': {
            'fitness': 'stable',
            'readiness': 'stable',
            'stress': 'stable'
        }
    }
    
    return render_template('dashboard/analytics.html',
                         period=period,
                         combined_data=combined_data,
                         correlations=correlations,
                         pmc_chart=pmc_chart,
                         stats=stats)

@dashboard_bp.route('/reports')
def reports():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Buscar relatórios disponíveis
    available_reports = [
        {
            'id': 'weekly',
            'title': 'Relatório Semanal',
            'description': 'Resumo completo da semana com métricas e recomendações',
            'frequency': 'Semanal'
        },
        {
            'id': 'monthly',
            'title': 'Relatório Mensal',
            'description': 'Análise detalhada do mês com tendências e insights',
            'frequency': 'Mensal'
        },
        {
            'id': 'competition',
            'title': 'Relatório Pré-Competição',
            'description': 'Análise focada em preparação para competições',
            'frequency': 'Sob demanda'
        },
        {
            'id': 'recovery',
            'title': 'Relatório de Recuperação',
            'description': 'Foco em métricas de recuperação e prontidão',
            'frequency': 'Sob demanda'
        }
    ]
    
    return render_template('dashboard/reports.html',
                         available_reports=available_reports)

@dashboard_bp.route('/generate-report/<report_type>')
def generate_report(report_type):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    from app import db, User
    
    user_id = session['user_id']
    user = User.query.get(user_id)
    
    if report_type == 'weekly':
        # Gerar relatório semanal
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=7)
        
        report_data = generate_weekly_report(user_id, start_date, end_date, db)
        report_data['name'] = user.name
        
        # Criar PDF
        pdf_buffer = export_to_pdf(report_data, f'relatorio_semanal_{start_date}_{end_date}.pdf')
        
        return send_file(
            pdf_buffer,
            as_attachment=True,
            download_name=f'relatorio_semanal_{start_date.strftime("%Y%m%d")}.pdf',
            mimetype='application/pdf'
        )
    
    elif report_type == 'monthly':
        # Implementar relatório mensal
        flash('Relatório mensal em desenvolvimento')
        return redirect(url_for('dashboard.reports'))
    
    else:
        flash('Tipo de relatório não encontrado')
        return redirect(url_for('dashboard.reports'))

@dashboard_bp.route('/export', methods=['GET', 'POST'])
def export():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        from app import db, ReadinessAssessment, TrainingAssessment, PsychologicalAssessment
        
        # Obter parâmetros de exportação
        export_format = request.form.get('format', 'excel')
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
        include_readiness =