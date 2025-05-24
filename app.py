from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import json
import os
from utils import *
from readiness import readiness_bp
from training import training_bp
from psychological import psychological_bp
from dashboard import dashboard_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sua_chave_secreta_aqui'  # Mude para uma chave secreta segura
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///athlete_monitoring.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Registro dos blueprints
app.register_blueprint(readiness_bp, url_prefix='/readiness')
app.register_blueprint(training_bp, url_prefix='/training')
app.register_blueprint(psychological_bp, url_prefix='/psychological')
app.register_blueprint(dashboard_bp, url_prefix='/dashboard')

# Modelos de banco de dados
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    name = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    readiness_assessments = db.relationship('ReadinessAssessment', backref='user', lazy=True)
    training_assessments = db.relationship('TrainingAssessment', backref='user', lazy=True)
    psychological_assessments = db.relationship('PsychologicalAssessment', backref='user', lazy=True)
    training_logs = db.relationship('TrainingLog', backref='user', lazy=True)
    training_sessions = db.relationship('TrainingSession', backref='user', lazy=True)
    goals = db.relationship('Goal', backref='user', lazy=True)
    performance_metrics = db.relationship('PerformanceMetric', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class ReadinessAssessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    sleep_quality = db.Column(db.Integer, nullable=False)  # 1-5
    sleep_duration = db.Column(db.Float, nullable=False)  # em horas
    stress_level = db.Column(db.Integer, nullable=False)  # 1-5
    muscle_soreness = db.Column(db.Integer, nullable=False)  # 1-5
    energy_level = db.Column(db.Integer, nullable=False)  # 1-5
    motivation = db.Column(db.Integer, nullable=False)  # 1-5
    nutrition_quality = db.Column(db.Integer, nullable=False)  # 1-5
    hydration = db.Column(db.Integer, nullable=False)  # 1-5
    readiness_score = db.Column(db.Float, nullable=False)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TrainingAssessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    training_load = db.Column(db.Float, nullable=False)  # RPE * Duration
    training_duration = db.Column(db.Float, nullable=False)  # minutos
    rpe = db.Column(db.Integer, nullable=False)  # 1-10
    intensity_zone = db.Column(db.String(20), nullable=False)  # Low, Moderate, High, Very High
    training_type = db.Column(db.String(50), nullable=False)  # Aerobic, Anaerobic, Mixed, Recovery
    fatigue_level = db.Column(db.Integer, nullable=False)  # 1-10
    performance_feeling = db.Column(db.Integer, nullable=False)  # 1-10
    chronic_load = db.Column(db.Float)  # CTL
    acute_load = db.Column(db.Float)  # ATL
    training_strain = db.Column(db.Float)  # ATL/CTL
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PsychologicalAssessment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    
    # DASS-21 Scores
    depression_score = db.Column(db.Integer, nullable=False)
    anxiety_score = db.Column(db.Integer, nullable=False)
    stress_score = db.Column(db.Integer, nullable=False)
    
    # Motivation Assessment
    intrinsic_motivation = db.Column(db.Integer, nullable=False)  # 1-7
    extrinsic_motivation = db.Column(db.Integer, nullable=False)  # 1-7
    amotivation = db.Column(db.Integer, nullable=False)  # 1-7
    
    # Flow State Scale
    flow_score = db.Column(db.Float, nullable=False)
    
    # Additional fields
    confidence_level = db.Column(db.Integer, nullable=False)  # 1-10
    focus_ability = db.Column(db.Integer, nullable=False)  # 1-10
    emotional_state = db.Column(db.String(50))
    pre_competition_anxiety = db.Column(db.Integer)  # 1-10 (optional)
    satisfaction_with_training = db.Column(db.Integer, nullable=False)  # 1-10
    team_cohesion = db.Column(db.Integer)  # 1-10 (optional)
    
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TrainingLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    training_type = db.Column(db.String(50), nullable=False)
    duration = db.Column(db.Float, nullable=False)  # minutos
    distance = db.Column(db.Float)  # km
    pace = db.Column(db.String(20))  # min/km
    heart_rate_avg = db.Column(db.Integer)  # bpm
    heart_rate_max = db.Column(db.Integer)  # bpm
    calories_burned = db.Column(db.Integer)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class TrainingSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    training_type = db.Column(db.String(50))
    planned_duration = db.Column(db.Float)  # minutos
    actual_duration = db.Column(db.Float)  # minutos
    completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Goal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    target_date = db.Column(db.Date)
    metric_type = db.Column(db.String(50))  # performance, readiness, psychological
    target_value = db.Column(db.Float)
    current_value = db.Column(db.Float)
    status = db.Column(db.String(20), default='active')  # active, completed, abandoned
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PerformanceMetric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    metric_type = db.Column(db.String(50), nullable=False)  # VO2max, 5K time, marathon time, etc.
    value = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20))  # ml/kg/min, minutes, seconds, etc.
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Rotas principais
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        name = request.form['name']
        
        if User.query.filter_by(email=email).first():
            flash('Email já cadastrado!')
            return redirect(url_for('register'))
        
        user = User(email=email, name=name)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Cadastro realizado com sucesso!')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['user_name'] = user.name
            return redirect(url_for('dashboard'))
        
        flash('Email ou senha incorretos!')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    today = datetime.now().date()
    
    # Buscar dados dos últimos 7 dias
    seven_days_ago = today - timedelta(days=7)
    
    readiness_data = db.session.query(ReadinessAssessment).filter(
        ReadinessAssessment.user_id == user_id,
        ReadinessAssessment.date >= seven_days_ago
    ).all()
    
    training_data = db.session.query(TrainingAssessment).filter(
        TrainingAssessment.user_id == user_id,
        TrainingAssessment.date >= seven_days_ago
    ).all()
    
    psychological_data = db.session.query(PsychologicalAssessment).filter(
        PsychologicalAssessment.user_id == user_id,
        PsychologicalAssessment.date >= seven_days_ago
    ).all()
    
    # Calcular médias
    avg_readiness = sum([r.readiness_score for r in readiness_data]) / len(readiness_data) if readiness_data else 0
    avg_training_load = sum([t.training_load for t in training_data]) / len(training_data) if training_data else 0
    avg_stress = sum([p.stress_score for p in psychological_data]) / len(psychological_data) if psychological_data else 0
    
    return render_template('dashboard.html', 
                         avg_readiness=avg_readiness,
                         avg_training_load=avg_training_load,
                         avg_stress=avg_stress,
                         readiness_data=readiness_data,
                         training_data=training_data,
                         psychological_data=psychological_data)

# Rota para recuperação de senha
@app.route('/recover-password', methods=['GET', 'POST'])
def recover_password():
    if request.method == 'POST':
        email = request.form['email']
        user = User.query.filter_by(email=email).first()
        
        if user:
            # Aqui você implementaria o envio de email
            # Por enquanto, apenas uma mensagem
            flash('Se este email existe, você receberá instruções para recuperar sua senha.')
        else:
            flash('Se este email existe, você receberá instruções para recuperar sua senha.')
        
        return redirect(url_for('login'))
    
    return render_template('recover_password.html')

# API endpoints
@app.route('/api/data/<data_type>')
def api_get_data(data_type):
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    user_id = session['user_id']
    days = request.args.get('days', 30, type=int)
    start_date = datetime.now().date() - timedelta(days=days)
    
    if data_type == 'readiness':
        data = ReadinessAssessment.query.filter(
            ReadinessAssessment.user_id == user_id,
            ReadinessAssessment.date >= start_date
        ).all()
        
        return jsonify([{
            'date': d.date.isoformat(),
            'score': d.readiness_score,
            'sleep_quality': d.sleep_quality,
            'stress_level': d.stress_level,
            'energy_level': d.energy_level
        } for d in data])
    
    elif data_type == 'training':
        data = TrainingAssessment.query.filter(
            TrainingAssessment.user_id == user_id,
            TrainingAssessment.date >= start_date
        ).all()
        
        return jsonify([{
            'date': d.date.isoformat(),
            'training_load': d.training_load,
            'rpe': d.rpe,
            'duration': d.training_duration,
            'type': d.training_type
        } for d in data])
    
    elif data_type == 'psychological':
        data = PsychologicalAssessment.query.filter(
            PsychologicalAssessment.user_id == user_id,
            PsychologicalAssessment.date >= start_date
        ).all()
        
        return jsonify([{
            'date': d.date.isoformat(),
            'stress_score': d.stress_score,
            'anxiety_score': d.anxiety_score,
            'depression_score': d.depression_score,
            'flow_score': d.flow_score,
            'confidence_level': d.confidence_level
        } for d in data])
    
    return jsonify({'error': 'Invalid data type'}), 400

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)