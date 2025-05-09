
    -- Novas tabelas para o sistema atualizado

    -- 1. Readiness Assessments (já existe, será expandida)
    ALTER TABLE assessments
    ADD COLUMN trimp DECIMAL,
    ADD COLUMN training_load DECIMAL,
    ADD COLUMN acute_load DECIMAL,
    ADD COLUMN chronic_load DECIMAL,
    ADD COLUMN monotony DECIMAL,
    ADD COLUMN strain DECIMAL,
    ADD COLUMN injury_risk DECIMAL;

    -- 2. Psychological Assessments
    CREATE TABLE psychological_assessments (
        id SERIAL PRIMARY KEY,
        user_id UUID REFERENCES users(id),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        anxiety_score INTEGER,
        stress_score INTEGER,
        lifestyle_score INTEGER,
        anxiety_responses JSONB,
        stress_responses JSONB,
        lifestyle_responses JSONB,
        recommendations TEXT
    );

    -- 3. Training Assessments
    CREATE TABLE training_assessments (
        id SERIAL PRIMARY KEY,
        user_id UUID REFERENCES users(id),
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        duration INTEGER,
        rpe INTEGER,
        heart_rate INTEGER,
        trimp DECIMAL,
        training_load DECIMAL,
        fatigue_score INTEGER,
        notes TEXT
    );
    