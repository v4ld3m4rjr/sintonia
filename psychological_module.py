from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from datetime import datetime, timedelta
from utils import calculate_dass21_scores, calculate_flow_score, calculate_motivation_scores, get_interpretation
import json

psychological_bp = Blueprint('psychological', __name__)

@psychological_bp.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('psychological/index.html')

@psychological_bp.route('/assessment', methods=['GET', 'POST'])
def assessment():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        from app import db, PsychologicalAssessment
        
        # Coletar dados do DASS-21
        dass21_responses = []
        for i in range(21):
            dass21_responses.append(int(request.form.get(f'dass21_{i+1}', 0)))
        
        dass21_scores = calculate_dass21_scores(dass21_responses)
        
        # Coletar dados de motivação
        motivation_responses = []
        for i in range(12):
            motivation_responses.append(int(request.form.get(f'motivation_{i+1}', 0)))
        
        motivation_scores = calculate_motivation_scores(motivation_responses)
        
        # Coletar dados do Flow State Scale
        flow_responses = []
        for i in range(9):
            flow_responses.append(int(request.form.get(f'flow_{i+1}', 0)))
        
        flow_score = calculate_flow_score(flow_responses)
        
        # Coletar outros dados
        assessment_data = {
            'confidence_level': int(request.form['confidence_level']),
            'focus_ability': int(request.form['focus_ability']),
            'emotional_state': request.form['emotional_state'],
            'satisfaction_with_training': int(request.form['satisfaction_with_training']),
            'notes': request.form.get('notes', '')
        }
        
        # Campos opcionais
        if 'pre_competition_anxiety' in request.form and request.form['pre_competition_anxiety']:
            assessment_data['pre_competition_anxiety'] = int(request.form['pre_competition_anxiety'])
        
        if 'team_cohesion' in request.form and request.form['team_cohesion']:
            assessment_data['team_cohesion'] = int(request.form['team_cohesion'])
        
        # Salvar no banco
        assessment = PsychologicalAssessment(
            user_id=session['user_id'],
            date=request.form.get('date', datetime.now().date()),
            depression_score=dass21_scores['depression_score'],
            anxiety_score=dass21_scores['anxiety_score'],
            stress_score=dass21_scores['stress_score'],
            intrinsic_motivation=motivation_scores['intrinsic_motivation'],
            extrinsic_motivation=motivation_scores['extrinsic_motivation'],
            amotivation=motivation_scores['amotivation'],
            flow_score=flow_score,
            **assessment_data
        )
        
        db.session.add(assessment)
        db.session.commit()
        
        flash('Avaliação psicológica salva com sucesso!')
        return redirect(url_for('psychological.results', assessment_id=assessment.id))
    
    # Questionários para o formulário
    dass21_questions = [
        "Achei difícil me acalmar",
        "Percebi que minha boca estava seca",
        "Não consegui ter sentimentos positivos",
        "Senti dificuldades em respirar",
        "Achei difícil começar a fazer as coisas",
        "Tive tendência a reagir exageradamente",
        "Tive tremores nas mãos",
        "Senti que estava inquieto",
        "Preocupei-me com situações que poderia entrar em pânico",
        "Senti que não tinha algo pelo que me entusiasmar",
        "Me vi ficando agitado",
        "Achei difícil relaxar",
        "Senti-me desanimado e melancólico",
        "Fui intolerante com coisas que me impedissem de continuar fazendo as coisas",
        "Senti que estava quase em pânico",
        "Não consegui me entusiasmar com nada",
        "Senti que não tinha valor como pessoa",
        "Senti que estava sendo irritadiço",
        "Percebi os batimentos de meu coração sem fazer exercício físico",
        "Senti medo sem uma razão",
        "Senti que a vida não tinha sentido"
    ]
    
    motivation_questions = [
        # Motivação Intrínseca
        "Participo dos treinos porque são interessantes",
        "Pratico porque gosto de aprender novas técnicas",
        "Treino porque é prazeroso desenvolver minhas habilidades",
        "Participo porque sinto satisfação em dominar atividades difíceis",
        
        # Motivação Extrínseca
        "Treino porque outras pessoas dizem que deveria",
        "Pratico para ganhar prestígio",
        "Treino porque é esperado que eu o faça",
        "Participo para mostrar aos outros que sou competente",
        
        # Amotivação
        "Não sei mais por que pratico",
        "Tenho questionado por que continuo",
        "Sinto que estou desperdiçando tempo",
        "Não vejo mais um bom motivo para continuar"
    ]
    
    flow_questions = [
        "Senti-me completamente concentrado na tarefa",
        "Tudo fluiu automaticamente",
        "Perdi a noção do tempo",
        "Senti-me no controle total",
        "A tarefa em si era recompensadora",
        "Senti uma sensação de facilidade",
        "Estava totalmente imerso na atividade",
        "Senti uma mistura perfeita de desafio e habilidade",
        "Experimentei uma sensação de unidade entre ação e consciência"
    ]
    
    return render_template('psychological/assessment.html',
                         dass21_questions=dass21_questions,
                         motivation_questions=motivation_questions,
                         flow_questions=flow_questions)

@psychological_bp.route('/results/<int:assessment_id>')
def results(assessment_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    from app import db, PsychologicalAssessment
    
    assessment = PsychologicalAssessment.query.get_or_404(assessment_id)
    
    if assessment.user_id != session['user_id']:
        flash('Você não tem permissão para visualizar esta avaliação.')
        return redirect(url_for('psychological.index'))
    
    # Obter interpretações
    interpretations = {
        'depression': get_interpretation(assessment.depression_score, 'depression'),
        'anxiety': get_interpretation(assessment.anxiety_score, 'anxiety'),
        'stress': get_interpretation(assessment.stress_score, 'stress'),
        'flow': get_interpretation(assessment.flow_score, 'flow')
    }
    
    # Dados para gráfico de radar (DASS-21)
    dass21_data = {
        'Depression': assessment.depression_score,
        'Anxiety': assessment.anxiety_score,
        'Stress': assessment.stress_score
    }
    
    # Dados para gráfico de motivação
    motivation_data = {
        'Intrínseca': assessment.intrinsic_motivation,
        'Extrínseca': assessment.extrinsic_motivation,
        'Amotivação': assessment.amotivation
    }
    
    # Buscar histórico dos últimos 30 dias
    thirty_days_ago = datetime.now().date() - timedelta(days=30)
    historical_data = PsychologicalAssessment.query.filter(
        PsychologicalAssessment.user_id == session['user_id'],
        PsychologicalAssessment.date >= thirty_days_ago
@psychological_bp.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    from app import db, PsychologicalAssessment
    
    # Obter período do filtro
    days = request.args.get('days', 30, type=int)
    start_date = datetime.now().date() - timedelta(days=days)
    
    # Buscar dados
    assessments = PsychologicalAssessment.query.filter(
        PsychologicalAssessment.user_id == session['user_id'],
        PsychologicalAssessment.date >= start_date
    ).order_by(PsychologicalAssessment.date.desc()).all()
    
    # Calcular estatísticas
    if assessments:
        stats = {
            'average_stress': sum(a.stress_score for a in assessments) / len(assessments),
            'average_anxiety': sum(a.anxiety_score for a in assessments) / len(assessments),
            'average_depression': sum(a.depression_score for a in assessments) / len(assessments),
            'average_flow': sum(a.flow_score for a in assessments) / len(assessments),
            'average_confidence': sum(a.confidence_level for a in assessments) / len(assessments),
            'average_satisfaction': sum(a.satisfaction_with_training for a in assessments) / len(assessments),
            'total_assessments': len(assessments),
            'emotional_states': {},
            'motivation_trends': {
                'intrinsic': sum(a.intrinsic_motivation for a in assessments) / len(assessments),
                'extrinsic': sum(a.extrinsic_motivation for a in assessments) / len(assessments),
                'amotivation': sum(a.amotivation for a in assessments) / len(assessments)
            }
        }
        
        # Contar estados emocionais
        for assessment in assessments:
            if assessment.emotional_state:
                stats['emotional_states'][assessment.emotional_state] = stats['emotional_states'].get(assessment.emotional_state, 0) + 1
    else:
        stats = {}
    
    return render_template('psychological/history.html', 
                         assessments=assessments,
                         stats=stats,
                         days=days)

@psychological_bp.route('/api/chart-data')
def api_chart_data():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    from app import db, PsychologicalAssessment
    
    # Obter parâmetros
    days = request.args.get('days', 30, type=int)
    start_date = datetime.now().date() - timedelta(days=days)
    
    # Buscar dados
    assessments = PsychologicalAssessment.query.filter(
        PsychologicalAssessment.user_id == session['user_id'],
        PsychologicalAssessment.date >= start_date
    ).order_by(PsychologicalAssessment.date).all()
    
    # Preparar dados para diferentes tipos de gráficos
    data = {
        'timeline': {
            'dates': [a.date.strftime('%Y-%m-%d') for a in assessments],
            'stress': [a.stress_score for a in assessments],
            'anxiety': [a.anxiety_score for a in assessments],
            'depression': [a.depression_score for a in assessments],
            'flow': [a.flow_score for a in assessments],
            'confidence': [a.confidence_level for a in assessments],
            'satisfaction': [a.satisfaction_with_training for a in assessments]
        },
        'averages': {
            'stress': sum(a.stress_score for a in assessments) / len(assessments) if assessments else 0,
            'anxiety': sum(a.anxiety_score for a in assessments) / len(assessments) if assessments else 0,
            'depression': sum(a.depression_score for a in assessments) / len(assessments) if assessments else 0,
            'flow': sum(a.flow_score for a in assessments) / len(assessments) if assessments else 0,
            'confidence': sum(a.confidence_level for a in assessments) / len(assessments) if assessments else 0
        },
        'motivation': {
            'dates': [a.date.strftime('%Y-%m-%d') for a in assessments],
            'intrinsic': [a.intrinsic_motivation for a in assessments],
            'extrinsic': [a.extrinsic_motivation for a in assessments],
            'amotivation': [a.amotivation for a in assessments]
        },
        'emotional_states': {}
    }
    
    # Contar estados emocionais
    for assessment in assessments:
        if assessment.emotional_state:
            data['emotional_states'][assessment.emotional_state] = data['emotional_states'].get(assessment.emotional_state, 0) + 1
    
    return jsonify(data)

@psychological_bp.route('/recommendations')
def recommendations():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    from app import db, PsychologicalAssessment
    
    # Buscar última avaliação
    latest_assessment = PsychologicalAssessment.query.filter(
        PsychologicalAssessment.user_id == session['user_id']
    ).order_by(PsychologicalAssessment.date.desc()).first()
    
    recommendations = []
    
    if latest_assessment:
        # Recomendações baseadas em DASS-21
        if latest_assessment.stress_score > 15:
            recommendations.append({
                'category': 'Estresse',
                'title': 'Gerenciamento do Estresse',
                'description': f'Seu nível de estresse está em {latest_assessment.stress_score} (severo).',
                'actions': [
                    'Praticar técnicas de respiração profunda',
                    'Implementar mindfulness ou meditação',
                    'Considerar redução na carga de treino temporariamente',
                    'Buscar apoio de profissional de saúde mental'
                ]
            })
        elif latest_assessment.stress_score > 10:
            recommendations.append({
                'category': 'Estresse',
                'title': 'Atenção ao Estresse',
                'description': f'Seu nível de estresse está em {latest_assessment.stress_score} (moderado).',
                'actions': [
                    'Aumentar atividades relaxantes',
                    'Praticar yoga ou alongamentos',
                    'Revisar rotina de sono',
                    'Manter diário de gratidão'
                ]
            })
        
        if latest_assessment.anxiety_score > 8:
            recommendations.append({
                'category': 'Ansiedade',
                'title': 'Controle da Ansiedade',
                'description': f'Sua ansiedade está em {latest_assessment.anxiety_score}.',
                'actions': [
                    'Praticar visualização positiva',
                    'Usar técnicas de grounding',
                    'Estabelecer rotinas pré-competição',
                    'Conversar com técnico/psicólogo esportivo'
                ]
            })
        
        if latest_assessment.depression_score > 7:
            recommendations.append({
                'category': 'Humor',
                'title': 'Suporte para o Humor',
                'description': f'Scores de depressão em {latest_assessment.depression_score}.',
                'actions': [
                    'Manter atividade física regular (mesmo leve)',
                    'Buscar conexões sociais',
                    'Considerar terapia profissional',
                    'Estabelecer objetivos pequenos e alcançáveis'
                ]
            })
        
        # Recomendações baseadas em Flow
        if latest_assessment.flow_score < 3:
            recommendations.append({
                'category': 'Engajamento',
                'title': 'Aumentar Estado de Flow',
                'description': f'Seu score de flow está baixo: {latest_assessment.flow_score:.1f}.',
                'actions': [
                    'Ajustar nível de desafio dos treinos',
                    'Estabelecer objetivos claros',
                    'Eliminar distrações durante treinos',
                    'Buscar feedback imediato'
                ]
            })
        
        # Recomendações baseadas em motivação
        if latest_assessment.amotivation > 4:
            recommendations.append({
                'category': 'Motivação',
                'title': 'Redescobrir a Motivação',
                'description': 'Você está experienciando amotivação elevada.',
                'actions': [
                    'Revisar objetivos e metas',
                    'Lembrar dos motivos iniciais para praticar',
                    'Variar rotina de treinos',
                    'Buscar novos desafios ou competições'
                ]
            })
        
        if latest_assessment.intrinsic_motivation < latest_assessment.extrinsic_motivation:
            recommendations.append({
                'category': 'Motivação',
                'title': 'Fortalecer Motivação Intrínseca',
                'description': 'Sua motivação está mais baseada em fatores externos.',
                'actions': [
                    'Focar no prazer da atividade',
                    'Celebrar pequenas conquistas',
                    'Buscar aspectos divertidos nos treinos',
                    'Desenvolver autonomia nas escolhas de treino'
                ]
            })
        
        # Recomendações baseadas em confiança
        if latest_assessment.confidence_level < 5:
            recommendations.append({
                'category': 'Confiança',
                'title': 'Construir Autoconfiança',
                'description': f'Seu nível de confiança está em {latest_assessment.confidence_level}/10.',
                'actions': [
                    'Manter registro de conquistas',
                    'Visualizar sucessos passados',
                    'Estabelecer metas progressivas',
                    'Praticar auto-fala positiva'
                ]
            })
        
        # Recomendações baseadas em satisfação
        if latest_assessment.satisfaction_with_training < 5:
            recommendations.append({
                'category': 'Satisfação',
                'title': 'Melhorar Satisfação com Treinos',
                'description': f'Satisfação com treinos: {latest_assessment.satisfaction_with_training}/10.',
                'actions': [
                    'Revisar programa de treinamento',
                    'Comunicar-se mais com treinador',
                    'Adicionar variedade aos treinos',
                    'Estabelecer objetivos mais alinhados'
                ]
            })
    
    return render_template('psychological/recommendations.html', 
                         recommendations=recommendations,
                         assessment=latest_assessment)

@psychological_bp.route('/insights')
def insights():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    from app import db, PsychologicalAssessment, TrainingAssessment, ReadinessAssessment
    
    # Buscar dados dos últimos 90 dias
    ninety_days_ago = datetime.now().date() - timedelta(days=90)
    
    psych_data = PsychologicalAssessment.query.filter(
        PsychologicalAssessment.user_id == session['user_id'],
        PsychologicalAssessment.date >= ninety_days_ago
    ).order_by(PsychologicalAssessment.date).all()
    
    training_data = TrainingAssessment.query.filter(
        TrainingAssessment.user_id == session['user_id'],
        TrainingAssessment.date >= ninety_days_ago
    ).order_by(TrainingAssessment.date).all()
    
    readiness_data = ReadinessAssessment.query.filter(
        ReadinessAssessment.user_id == session['user_id'],
        ReadinessAssessment.date >= ninety_days_ago
    ).order_by(ReadinessAssessment.date).all()
    
    # Análise de correlações entre dados psicológicos e físicos
    correlations = []
    trends = []
    insights = []
    
    # Preparar dados para análise
    if psych_data and training_data:
        # Correlação entre estresse e carga de treino
        stress_scores = [p.stress_score for p in psych_data]
        
        # Encontrar correspondências por data
        for psych in psych_data:
            matching_training = next((t for t in training_data if t.date == psych.date), None)
            if matching_training and matching_training.training_load:
                if psych.stress_score > 15 and matching_training.training_load > 100:
                    insights.append({
                        'type': 'warning',
                        'title': 'Estresse Alto com Carga Intensa',
                        'date': psych.date.strftime('%d/%m'),
                        'description': f'Estresse: {psych.stress_score}, Carga: {matching_training.training_load:.1f}'
                    })
    
    # Análise de tendências
    if len(psych_data) >= 7:
        recent_week = psych_data[-7:]
        
        # Tendência de estresse
        stress_trend = 'increasing' if recent_week[-1].stress_score > recent_week[0].stress_score else 'decreasing'
        flow_trend = 'increasing' if recent_week[-1].flow_score > recent_week[0].flow_score else 'decreasing'
        
        trends.append({
            'metric': 'Estresse',
            'direction': stress_trend,
            'change': recent_week[-1].stress_score - recent_week[0].stress_score
        })
        
        trends.append({
            'metric': 'Flow',
            'direction': flow_trend,
            'change': recent_week[-1].flow_score - recent_week[0].flow_score
        })
    
    # Análise de padrões
    patterns = []
    
    # Dias da semana com mais estresse
    if psych_data:
        weekday_stress = {}
        for p in psych_data:
            weekday = p.date.strftime('%A')
            if weekday not in weekday_stress:
                weekday_stress[weekday] = []
            weekday_stress[weekday].append(p.stress_score)
        
        for day, scores in weekday_stress.items():
            avg_stress = sum(scores) / len(scores)
            if avg_stress > 15:
                patterns.append({
                    'pattern': f'{day} costuma ter estresse elevado',
                    'detail': f'Média: {avg_stress:.1f}'
                })
    
    return render_template('psychological/insights.html',
                         correlations=correlations,
                         trends=trends,
                         insights=insights,
                         patterns=patterns,
                         psych_data=psych_data)
    
    # Preparar dados para gráficos históricos
    history_chart_data = {
        'dates': [h.date.strftime('%Y-%m-%d') for h in historical_data],
        'stress': [h.stress_score for h in historical_data],
        'anxiety': [h.anxiety_score for h in historical_data],
        'depression': [h.depression_score for h in historical_data],
        'flow': [h.flow_score for h in historical_data],
        'confidence': [h.confidence_level for h in historical_data],
        'satisfaction': [h.satisfaction_with_training for h in historical_data]
    }
    
    return render_template('psychological/results.html',
                         assessment=assessment,
                         interpretations=interpretations,
                         dass21_data=dass21_data,
                         motivation_data=motivation_data,
                         history_data=history_chart_data)

@psychological_bp.route('/history')
def history():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    from app import db, PsychologicalAssessment
    
    # Obter período do filtro
    days = request.args.get('days', 30, type=int)
    start_date = datetime.now().date() - timedelta(days=days)
    
    # Buscar dados
    assessments = PsychologicalAssessment.query.filter(
        PsychologicalAssessment.user_id == session['user_id'],
        PsychologicalAssessment.date >= start_date
    ).order_