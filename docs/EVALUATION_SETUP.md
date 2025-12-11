# Evaluation Pipeline Setup Guide

## 📚 Overview

This evaluation pipeline automatically logs, evaluates, and stores metrics for every agent interaction using DeepEval and PostgreSQL.

## 🗄️ Database Setup

### 1. Install PostgreSQL

**macOS:**
```bash
brew install postgresql@15
brew services start postgresql@15
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Windows:**
Download from https://www.postgresql.org/download/windows/

### 2. Create Database

```bash
# Connect to PostgreSQL
psql postgres

# Create database and user
CREATE DATABASE mf_agent_eval;
CREATE USER mf_agent WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE mf_agent_eval TO mf_agent;
\q
```

### 3. Initialize Schema

```bash
# Run schema file
psql -U mf_agent -d mf_agent_eval -f database/schema.sql
```

### 4. Configure Environment

Create or update `.env` file:

```bash
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mf_agent_eval
DB_USER=mf_agent
DB_PASSWORD=your_secure_password

# Agent Configuration
GROQ_API_KEY=your_groq_api_key
CONFIDENCE_THRESHOLD=0.75
AGENT_VERSION=1.0.0
ENVIRONMENT=development  # or production
```

## 📦 Install Dependencies

```bash
# Install all dependencies including evaluation tools
pip install -r requirements.txt

# Or install individually
pip install psycopg2-binary deepeval tabulate
```

## 🧪 DeepEval Setup

### 1. Initialize DeepEval (Optional for Advanced Features)

```bash
deepeval login
```

### 2. Configure DeepEval Metrics

The pipeline uses these metrics:
- **Answer Relevancy**: How relevant the answer is to the question
- **Faithfulness**: How accurate the answer is to retrieved context
- **Contextual Relevancy**: Quality of retrieved context
- **Hallucination**: Detection of fabricated information

## 🚀 Usage

### Basic Usage (With Evaluation)

```python
from evaluation.agent_wrapper import get_evaluated_agent

# Get agent with evaluation
agent = get_evaluated_agent()

# Process request (automatically logs and evaluates)
result = await agent.process_request_with_evaluation(
    user_prompt="What is the NAV of HDFC Top 100 Fund?",
    session_id="user-123-session",
    user_name="Sweatha",
    expected_intent="nav_request"  # Optional for supervised eval
)

# Access response and metrics
print(f"Response: {result['response']}")
print(f"Intent Confidence: {result['evaluation']['intent_confidence']}")
print(f"Relevance Score: {result['evaluation']['relevance_score']}")
print(f"Latency: {result['latency_ms']}ms")
```

### Run Test Suite

```bash
# Run all test cases
python run_evaluation.py

# Run specific category
python run_evaluation.py --category NAV_QUERY

# Show performance report
python run_evaluation.py --report --days 7
```

### Manual Evaluation

```python
from evaluation.pipeline import get_evaluation_pipeline

pipeline = get_evaluation_pipeline()

# Evaluate a single interaction
evaluation = pipeline.evaluate_interaction(
    user_prompt="What is mutual fund?",
    agent_response="A mutual fund is...",
    session_id="test-session",
    intent_data={
        'intent': 'general_concept',
        'confidence': 0.95,
        'entities': {}
    },
    retrieval_context=["context string 1", "context string 2"],
    latency_data={
        'total_ms': 1500,
        'llm_ms': 1200,
        'tool_ms': 200,
        'api_ms': 100
    },
    metadata={
        'tools_used': ['search_tavily_data'],
        'api_source': 'GROQ_LLM',
        'llm_model': 'KIMI-K2'
    },
    user_name="Sweatha"
)

print(f"Evaluation ID: {evaluation['eval_id']}")
print(f"Relevance: {evaluation['relevance_score']}")
```

## 📊 Querying Evaluation Data

### Using Python

```python
from database.db import get_eval_db

db = get_eval_db()

# Get recent evaluations
recent = db.get_evaluations(limit=10)

# Get evaluations for specific session
session_evals = db.get_evaluations(
    filters={'session_id': 'user-123-session'}
)

# Get performance summary
summary = db.get_performance_summary(days=7)
print(f"Average Relevance: {summary['summary']['avg_relevance']}")
print(f"Pass Rate: {summary['summary']['pass_rate']}")
```

### Using SQL Directly

```sql
-- Get recent evaluations
SELECT 
    user_prompt,
    intent_predicted,
    intent_confidence,
    relevance_score,
    passed_threshold,
    total_latency_ms,
    timestamp
FROM agent_evaluations
ORDER BY timestamp DESC
LIMIT 20;

-- Performance by intent
SELECT 
    intent_predicted,
    COUNT(*) as total,
    AVG(relevance_score) as avg_relevance,
    AVG(hallucination_score) as avg_hallucination,
    SUM(CASE WHEN passed_threshold THEN 1 ELSE 0 END)::FLOAT / COUNT(*) as pass_rate
FROM agent_evaluations
WHERE timestamp >= NOW() - INTERVAL '7 days'
GROUP BY intent_predicted
ORDER BY total DESC;

-- Use the performance overview view
SELECT * FROM performance_overview;
```

## 📈 Metrics Explained

### Intent Metrics
- **intent_predicted**: Classified intent type
- **intent_confidence**: Model confidence (0-1)
- **intent_match**: Boolean - predicted matches expected
- **passed_threshold**: Boolean - confidence >= threshold

### DeepEval Metrics
- **relevance_score**: 0-1, higher = more relevant
- **hallucination_score**: 0-1, lower = less hallucination
- **faithfulness_score**: 0-1, higher = more faithful to context
- **contextual_relevance**: 0-1, quality of retrieved context
- **answer_correctness**: Composite score (relevance + faithfulness)

### Performance Metrics
- **total_latency_ms**: End-to-end response time
- **llm_latency_ms**: LLM inference time
- **tool_latency_ms**: Tool execution time
- **api_latency_ms**: External API calls time

### Quality Metrics
- **contains_disclaimer**: Has risk/compliance disclaimer
- **risk_detection_flag**: Detected risky language
- **pii_detected**: Detected personal information request
- **response_length**: Length of response

## 🔧 Integration with Existing Code

### Update Your API Server

```python
# In api_server.py
from evaluation.agent_wrapper import get_evaluated_agent

# Replace regular agent with evaluated agent
agent = get_evaluated_agent()

@app.post("/chat")
async def chat(request: ChatRequest):
    result = await agent.process_request_with_evaluation(
        user_prompt=request.message,
        session_id=request.session_id,
        user_name=request.user_name
    )
    
    return {
        "response": result['response'],
        "session_id": result['session_id'],
        "metrics": {
            "confidence": result['evaluation']['intent_confidence'],
            "latency_ms": result['latency_ms']
        }
    }
```

### Add Test Cases

```python
from database.db import get_eval_db

db = get_eval_db()

test_cases = [
    {
        'test_query': 'What is the NAV of SBI Bluechip Fund?',
        'expected_intent': 'nav_request',
        'category': 'NAV_QUERY',
        'difficulty': 'EASY'
    },
    {
        'test_query': 'Compare HDFC Top 100 with ICICI Prudential Bluechip',
        'expected_intent': 'comparison',
        'category': 'COMPARISON',
        'difficulty': 'HARD'
    }
]

for tc in test_cases:
    db.save_test_case(tc)
```

## 🎯 Threshold Tuning

### Run Threshold Experiment

```python
from database.db import get_eval_db

db = get_eval_db()

# Create experiment
exp_id = db.create_threshold_experiment(
    name="Threshold 0.8 Test",
    threshold=0.8,
    notes="Testing higher threshold for better precision"
)

# Run tests with this threshold
# ... your test runs ...

# Analyze results
results = db.get_evaluations(filters={
    'date_from': '2025-12-09'
})

# Calculate metrics for this threshold
```

## 📊 Monitoring & Dashboards

### Daily Metrics Update (Cron Job)

```bash
# Add to crontab (run daily at midnight)
0 0 * * * cd /path/to/persagent-main && python -c "from database.db import get_eval_db; get_eval_db().update_daily_metrics()"
```

### Example Dashboard Queries

```sql
-- Daily trend
SELECT 
    date,
    total_queries,
    avg_relevance_score,
    pass_rate,
    error_rate
FROM daily_metrics
ORDER BY date DESC
LIMIT 30;

-- Intent distribution
SELECT 
    intent_predicted,
    COUNT(*) as count,
    AVG(relevance_score) as avg_relevance
FROM agent_evaluations
WHERE timestamp >= NOW() - INTERVAL '7 days'
GROUP BY intent_predicted;
```

## 🚨 Troubleshooting

### Database Connection Issues

```bash
# Test connection
psql -U mf_agent -d mf_agent_eval -c "SELECT 1;"

# Check if PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list  # macOS
```

### DeepEval Not Working

```bash
# Reinstall
pip uninstall deepeval
pip install deepeval --upgrade

# Check installation
python -c "import deepeval; print(deepeval.__version__)"
```

### Missing Tables

```bash
# Recreate schema
psql -U mf_agent -d mf_agent_eval -f database/schema.sql
```

## 🏭 Production Deployment

### 1. Use Production Database

Update `.env`:
```bash
DB_HOST=your-production-db.amazonaws.com
DB_PORT=5432
DB_NAME=mf_agent_prod
ENVIRONMENT=production
```

### 2. Enable Connection Pooling

```python
# In database/db.py, add connection pool
from psycopg2 import pool

connection_pool = pool.SimpleConnectionPool(
    minconn=1,
    maxconn=20,
    **db_config
)
```

### 3. Set Up Monitoring

- Use Grafana + PostgreSQL datasource
- Monitor daily_metrics table
- Set up alerts for error_rate > 5%
- Monitor avg_latency_ms trends

### 4. Backup Strategy

```bash
# Daily backup
pg_dump -U mf_agent mf_agent_eval > backup_$(date +%Y%m%d).sql

# Automated backup (crontab)
0 2 * * * pg_dump -U mf_agent mf_agent_eval > /backups/mf_agent_$(date +\%Y\%m\%d).sql
```

## 📝 Best Practices

1. **Always use evaluated agent wrapper** in production
2. **Set expected_intent** for supervised evaluation when possible
3. **Monitor daily_metrics** for trends
4. **Run test suite** before deploying updates
5. **Tune thresholds** based on precision/recall needs
6. **Archive old data** periodically (>90 days)
7. **Index frequently queried columns** for performance

## 🔗 Resources

- [DeepEval Documentation](https://docs.confident-ai.com/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)
- [LangChain Evaluation](https://python.langchain.com/docs/guides/evaluation)
