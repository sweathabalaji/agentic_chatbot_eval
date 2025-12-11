-- Agent Evaluations Database Schema
-- This stores all interaction data, evaluation metrics, and system metadata

CREATE TABLE IF NOT EXISTS agent_evaluations (
    id SERIAL PRIMARY KEY,
    
    -- Session & Interaction Data
    session_id VARCHAR(255) NOT NULL,
    user_id VARCHAR(255),
    user_name VARCHAR(100),
    user_prompt TEXT NOT NULL,
    agent_response TEXT NOT NULL,
    conversation_turn INT DEFAULT 1,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Intent & Classification
    intent_predicted VARCHAR(100),
    expected_intent VARCHAR(100),  -- For supervised evaluation
    intent_confidence FLOAT,
    intent_match BOOLEAN,  -- If expected_intent matches predicted
    entities_extracted JSONB,  -- Fund names, metrics, time periods
    
    -- Threshold Management
    threshold_used FLOAT,
    passed_threshold BOOLEAN,
    fallback_triggered BOOLEAN DEFAULT FALSE,
    
    -- DeepEval Metrics
    relevance_score FLOAT,
    hallucination_score FLOAT,
    faithfulness_score FLOAT,
    contextual_relevance FLOAT,
    answer_correctness FLOAT,
    
    -- Performance Metrics
    total_latency_ms INT,
    llm_latency_ms INT,
    tool_latency_ms INT,
    api_latency_ms INT,
    
    -- Data Source & Tools
    api_source VARCHAR(50),  -- API, AMFI, BSE, WEB_SCRAPE, GROQ_LLM
    tools_used JSONB,  -- Array of tools invoked
    retrieval_path VARCHAR(255),
    num_tool_calls INT DEFAULT 0,
    
    -- Quality & Safety
    contains_disclaimer BOOLEAN,
    risk_detection_flag BOOLEAN DEFAULT FALSE,
    pii_detected BOOLEAN DEFAULT FALSE,
    response_length INT,
    
    -- System Metadata
    llm_model VARCHAR(100),
    agent_version VARCHAR(50),
    toolchain_version VARCHAR(50),
    environment VARCHAR(50) DEFAULT 'development',
    
    -- Error Handling
    error_occurred BOOLEAN DEFAULT FALSE,
    error_message TEXT,
    retry_count INT DEFAULT 0
);

-- Create indexes for fast querying
CREATE INDEX IF NOT EXISTS idx_session_id ON agent_evaluations(session_id);
CREATE INDEX IF NOT EXISTS idx_timestamp ON agent_evaluations(timestamp);
CREATE INDEX IF NOT EXISTS idx_intent ON agent_evaluations(intent_predicted);
CREATE INDEX IF NOT EXISTS idx_passed_threshold ON agent_evaluations(passed_threshold);

-- Table for storing evaluation test cases
CREATE TABLE IF NOT EXISTS evaluation_test_cases (
    id SERIAL PRIMARY KEY,
    test_query TEXT NOT NULL,
    expected_intent VARCHAR(100),
    expected_entities JSONB,
    expected_response_keywords TEXT[],
    category VARCHAR(100),  -- NAV_QUERY, COMPARISON, CONCEPT, etc.
    difficulty VARCHAR(50),  -- EASY, MEDIUM, HARD
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Table for threshold experiments
CREATE TABLE IF NOT EXISTS threshold_experiments (
    id SERIAL PRIMARY KEY,
    experiment_name VARCHAR(255) NOT NULL,
    threshold_value FLOAT NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    total_queries INT DEFAULT 0,
    passed_queries INT DEFAULT 0,
    avg_relevance FLOAT,
    avg_hallucination FLOAT,
    avg_latency_ms INT,
    notes TEXT
);

-- Table for aggregated daily metrics
CREATE TABLE IF NOT EXISTS daily_metrics (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    total_queries INT DEFAULT 0,
    avg_relevance_score FLOAT,
    avg_hallucination_score FLOAT,
    avg_faithfulness_score FLOAT,
    avg_latency_ms INT,
    pass_rate FLOAT,
    error_rate FLOAT,
    top_intents JSONB,  -- Top 5 intents with counts
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- View for quick performance overview
CREATE OR REPLACE VIEW performance_overview AS
SELECT 
    DATE(timestamp) as date,
    COUNT(*) as total_queries,
    AVG(relevance_score) as avg_relevance,
    AVG(hallucination_score) as avg_hallucination,
    AVG(total_latency_ms) as avg_latency,
    SUM(CASE WHEN passed_threshold THEN 1 ELSE 0 END)::FLOAT / COUNT(*) as pass_rate,
    SUM(CASE WHEN error_occurred THEN 1 ELSE 0 END)::FLOAT / COUNT(*) as error_rate
FROM agent_evaluations
GROUP BY DATE(timestamp)
ORDER BY date DESC;

-- Insert sample test cases
INSERT INTO evaluation_test_cases (test_query, expected_intent, category, difficulty) VALUES
('What is the current NAV of Edelweiss Liquid Fund - Direct Plan weekly - IDCW Option', 'nav_request', 'NAV_QUERY', 'MEDIUM'),
('Compare Groww Multicap Fund - Direct - IDCW and HDFC Multi Cap Fund - IDCW Option - Direct Plan', 'comparison', 'COMPARISON', 'HARD'),
('Expense ratio of Axis CRISIL IBX SDL June 2034 Debt Index Fund - Direct Plan - IDCW Option', 'fund_details', 'METRICS', 'MEDIUM'),
('Suggest me top 10 funds to invest', 'recommendation', 'RECOMMENDATION', 'EASY'),
('What is the fund manager name of BANK OF INDIA Large & Mid Cap Equity Fund Direct Plan-Regular IDCW', 'fund_details', 'FUND_INFO', 'MEDIUM'),
('Show me 5-star rated large cap funds', 'search_by_criteria', 'SEARCH', 'MEDIUM'),
('What are the top performing funds this year?', 'top_performers', 'PERFORMANCE', 'EASY'),
('Get the factsheet for ISIN INF200K01180', 'factsheet', 'DETAILED_INFO', 'EASY'),
('Show me technology sector funds', 'search_by_sector', 'SEARCH', 'EASY'),
('What is mutual fund?', 'general_concept', 'CONCEPT', 'EASY');
