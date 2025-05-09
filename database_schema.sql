
-- New Database Schema

-- 1. Readiness Assessment Table
CREATE TABLE readiness_assessments (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    sleep_quality INTEGER CHECK (sleep_quality BETWEEN 1 AND 10),
    muscle_soreness INTEGER CHECK (muscle_soreness BETWEEN 1 AND 10),
    fatigue_level INTEGER CHECK (fatigue_level BETWEEN 1 AND 10),
    stress_level INTEGER CHECK (stress_level BETWEEN 1 AND 10),
    mood INTEGER CHECK (mood BETWEEN 1 AND 10),
    appetite INTEGER CHECK (appetite BETWEEN 1 AND 10),
    motivation INTEGER CHECK (motivation BETWEEN 1 AND 10),
    recovery_perception INTEGER CHECK (recovery_perception BETWEEN 1 AND 10),
    total_score INTEGER,
    readiness_percentage DECIMAL
);

-- 2. Training Assessment Table
CREATE TABLE training_assessments (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    session_duration INTEGER, -- in minutes
    session_rpe INTEGER CHECK (session_rpe BETWEEN 0 AND 10),
    trimp_score DECIMAL,
    training_load DECIMAL,
    fatigue_score INTEGER CHECK (fatigue_score BETWEEN 1 AND 10),
    recovery_score INTEGER CHECK (recovery_score BETWEEN 1 AND 10),
    injury_risk_factor DECIMAL,
    notes TEXT
);

-- 3. Psychological Assessment Table
CREATE TABLE psychological_assessments (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    -- DASS-21 Anxiety subscale (7 items)
    anxiety_score INTEGER,
    -- PSS-10 (Perceived Stress Scale)
    stress_score INTEGER,
    -- FANTASTIC Lifestyle Assessment
    lifestyle_score INTEGER,
    total_score INTEGER,
    recommendations TEXT
);

-- 4. Training Load History Table
CREATE TABLE training_load_history (
    id SERIAL PRIMARY KEY,
    user_id UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    acute_load DECIMAL, -- 7-day rolling average
    chronic_load DECIMAL, -- 28-day rolling average
    acwr DECIMAL, -- Acute:Chronic Workload Ratio
    monotony DECIMAL,
    strain DECIMAL
);
