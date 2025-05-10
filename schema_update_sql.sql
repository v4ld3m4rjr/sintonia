-- Schema update for Athlete Monitoring System

-- Create tables if they don't exist
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(128),
    name VARCHAR(80) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS readiness_assessment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date DATE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sleep_quality INTEGER NOT NULL,
    sleep_duration FLOAT NOT NULL,
    stress_level INTEGER NOT NULL,
    muscle_soreness INTEGER NOT NULL,
    energy_level INTEGER NOT NULL,
    motivation INTEGER NOT NULL,
    nutrition_quality INTEGER NOT NULL,
    hydration INTEGER NOT NULL,
    readiness_score FLOAT NOT NULL,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE IF NOT EXISTS training_assessment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date DATE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    training_load FLOAT NOT NULL,
    training_duration FLOAT NOT NULL,
    rpe INTEGER NOT NULL,
    intensity_zone VARCHAR(20) NOT NULL,
    training_type VARCHAR(50) NOT NULL,
    fatigue_level INTEGER NOT NULL,
    performance_feeling INTEGER NOT NULL,
    chronic_load FLOAT,
    acute_load FLOAT,
    training_strain FLOAT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE IF NOT EXISTS psychological_assessment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date DATE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    depression_score INTEGER NOT NULL,
    anxiety_score INTEGER NOT NULL,
    stress_score INTEGER NOT NULL,
    intrinsic_motivation INTEGER NOT NULL,
    extrinsic_motivation INTEGER NOT NULL,
    amotivation INTEGER NOT NULL,
    flow_score FLOAT NOT NULL,
    confidence_level INTEGER NOT NULL,
    focus_ability INTEGER NOT NULL,
    emotional_state VARCHAR(50),
    pre_competition_anxiety INTEGER,
    satisfaction_with_training INTEGER NOT NULL,
    team_cohesion INTEGER,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE IF NOT EXISTS training_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date DATE NOT NULL,
    training_type VARCHAR(50) NOT NULL,
    duration FLOAT NOT NULL,
    distance FLOAT,
    pace VARCHAR(20),
    heart_rate_avg INTEGER,
    heart_rate_max INTEGER,
    calories_burned INTEGER,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE IF NOT EXISTS training_session (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date TIMESTAMP NOT NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    training_type VARCHAR(50),
    planned_duration FLOAT,
    actual_duration FLOAT,
    completed BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE IF NOT EXISTS goal (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title VARCHAR(100) NOT NULL,
    description TEXT,
    target_date DATE,
    metric_type VARCHAR(50),
    target_value FLOAT,
    current_value FLOAT,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (id)
);

CREATE TABLE IF NOT EXISTS performance_metric (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    date DATE NOT NULL,
    metric_type VARCHAR(50) NOT NULL,
    value FLOAT NOT NULL,
    unit VARCHAR(20),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user (id)
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_readiness_user_date ON readiness_assessment(user_id, date);
CREATE INDEX IF NOT EXISTS idx_training_user_date ON training_assessment(user_id, date);
CREATE INDEX IF NOT EXISTS idx_psychological_user_date ON psychological_assessment(user_id, date);
CREATE INDEX IF NOT EXISTS idx_training_log_user_date ON training_log(user_id, date);
CREATE INDEX IF NOT EXISTS idx_training_session_user_date ON training_session(user_id, date);
CREATE INDEX IF NOT EXISTS idx_goal_user_status ON goal(user_id, status);
CREATE INDEX IF NOT EXISTS idx_performance_user_date ON performance_metric(user_id, date);

-- Add any missing columns (for existing databases)
ALTER TABLE readiness_assessment ADD COLUMN IF NOT EXISTS notes TEXT;
ALTER TABLE training_assessment ADD COLUMN IF NOT EXISTS notes TEXT;
ALTER TABLE psychological_assessment ADD COLUMN IF NOT EXISTS notes TEXT;

-- Create view for combined data analysis
CREATE VIEW IF NOT EXISTS athlete_data_combined AS
SELECT 
    r.user_id,
    r.date,
    r.readiness_score,
    r.sleep_quality,
    r.sleep_duration,
    r.stress_level as readiness_stress,
    r.energy_level,
    t.training_load,
    t.rpe,
    t.chronic_load as ctl,
    t.acute_load as atl,
    t.training_strain,
    p.stress_score as psychological_stress,
    p.anxiety_score,
    p.depression_score,
    p.flow_score,
    p.confidence_level,
    p.satisfaction_with_training
FROM readiness_assessment r
LEFT JOIN training_assessment t ON r.user_id = t.user_id AND r.date = t.date
LEFT JOIN psychological_assessment p ON r.user_id = p.user_id AND r.date = p.date
ORDER BY r.user_id, r.date;