-- Script de inicialização do banco de dados

-- Criar extensões úteis
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Criar tabela de usuários
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar índices
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- Criar tabela de perfis de clientes
CREATE TABLE IF NOT EXISTS customer_profiles (
    customer_id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    age INTEGER NOT NULL CHECK (age >= 18 AND age <= 100),
    gender VARCHAR(20) NOT NULL,
    marital_status VARCHAR(20) NOT NULL,
    profession VARCHAR(100) NOT NULL,
    monthly_income DECIMAL(12, 2) NOT NULL,
    net_income DECIMAL(12, 2) NOT NULL,
    employment_time_months INTEGER NOT NULL,
    credit_score INTEGER NOT NULL CHECK (credit_score >= 0 AND credit_score <= 1000),
    has_bacen_restrictions BOOLEAN NOT NULL DEFAULT FALSE,
    has_bureau_restrictions BOOLEAN NOT NULL DEFAULT FALSE,
    late_payments_count INTEGER NOT NULL DEFAULT 0,
    distance_from_branch_km DECIMAL(10, 2) NOT NULL,
    existing_debt DECIMAL(12, 2) NOT NULL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar tabela de solicitações de crédito
CREATE TABLE IF NOT EXISTS credit_requests (
    request_id VARCHAR(50) PRIMARY KEY,
    customer_id VARCHAR(50) NOT NULL REFERENCES customer_profiles(customer_id),
    product_type VARCHAR(50) NOT NULL,
    requested_amount DECIMAL(12, 2) NOT NULL,
    requested_installments INTEGER NOT NULL,
    request_date TIMESTAMP NOT NULL,
    purpose TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar tabela de resultados de análise
CREATE TABLE IF NOT EXISTS credit_analysis_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    request_id VARCHAR(50) NOT NULL REFERENCES credit_requests(request_id),
    customer_id VARCHAR(50) NOT NULL REFERENCES customer_profiles(customer_id),
    analysis_date TIMESTAMP NOT NULL,
    
    -- Etapa 1: Filtro por Persona (DFS)
    persona_filter_passed BOOLEAN NOT NULL,
    persona_rejection_reason TEXT,
    persona_decision_path JSONB,
    
    -- Etapa 2: Limite de Crédito (BFS)
    credit_limit_amount DECIMAL(12, 2),
    max_installment_value DECIMAL(12, 2),
    max_installments INTEGER,
    interest_rate DECIMAL(6, 4),
    
    -- Etapa 3: Avaliação de Risco (Fuzzy Logic)
    risk_level VARCHAR(20),
    risk_score DECIMAL(5, 3),
    credit_score_factor DECIMAL(5, 3),
    debt_ratio_factor DECIMAL(5, 3),
    late_payments_factor DECIMAL(5, 3),
    employment_factor DECIMAL(5, 3),
    distance_factor DECIMAL(5, 3),
    bacen_restrictions_factor DECIMAL(5, 3),
    bureau_restrictions_factor DECIMAL(5, 3),
    
    -- Etapa 4: Decisão Final (RNA)
    approval_status VARCHAR(20) NOT NULL,
    rejection_reason VARCHAR(50),
    neural_network_confidence DECIMAL(5, 3),
    
    -- Valores aprovados
    approved_amount DECIMAL(12, 2) DEFAULT 0,
    approved_installments INTEGER DEFAULT 0,
    approved_interest_rate DECIMAL(6, 4),
    monthly_payment DECIMAL(12, 2) DEFAULT 0,
    
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Criar índices para análises
CREATE INDEX IF NOT EXISTS idx_analysis_request ON credit_analysis_results(request_id);
CREATE INDEX IF NOT EXISTS idx_analysis_customer ON credit_analysis_results(customer_id);
CREATE INDEX IF NOT EXISTS idx_analysis_date ON credit_analysis_results(analysis_date);
CREATE INDEX IF NOT EXISTS idx_analysis_status ON credit_analysis_results(approval_status);
CREATE INDEX IF NOT EXISTS idx_analysis_risk ON credit_analysis_results(risk_level);

-- Criar índices para solicitações
CREATE INDEX IF NOT EXISTS idx_requests_customer ON credit_requests(customer_id);
CREATE INDEX IF NOT EXISTS idx_requests_date ON credit_requests(request_date);
CREATE INDEX IF NOT EXISTS idx_requests_product ON credit_requests(product_type);

-- Log de sucesso
DO $$
BEGIN
    RAISE NOTICE 'Database initialized successfully!';
    RAISE NOTICE 'Credit Analysis tables created!';
END $$;
