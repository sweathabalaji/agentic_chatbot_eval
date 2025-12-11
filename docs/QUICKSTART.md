# Quick Start Guide - Mutual Funds Agent Evaluation Pipeline

## 🚀 5-Minute Setup

### 1. Install PostgreSQL

```bash
# macOS
brew install postgresql@15
brew services start postgresql@15

# Ubuntu/Debian  
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### 2. Create Database

```bash
# Connect to PostgreSQL
psql postgres

# Run these commands
CREATE DATABASE mf_agent_eval;
CREATE USER mf_agent WITH PASSWORD 'changeme123';
GRANT ALL PRIVILEGES ON DATABASE mf_agent_eval TO mf_agent;
\q

# Initialize schema
psql -U mf_agent -d mf_agent_eval -f database/schema.sql
```

### 3. Configure Environment

```bash
# Copy template
cp .env.example .env

# Edit .env with your values
nano .env  # or use your preferred editor
```

**Minimum required:**
```bash
GROQ_API_KEY=your_groq_api_key
DB_PASSWORD=changeme123
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Test the Setup

```bash
# Run test suite
python run_evaluation.py

# You should see formatted output with metrics
```

## 📝 Example Usage

### Python Script

```python
from evaluation.agent_wrapper import get_evaluated_agent
import asyncio

async def test_agent():
    agent = get_evaluated_agent()
    
    result = await agent.process_request_with_evaluation(
        user_prompt="What is the NAV of HDFC Top 100 Fund?",
        session_id="test-session-1",
        user_name="Test User"
    )
    
    print(f"Response: {result['response']}")
    print(f"Confidence: {result['evaluation']['intent_confidence']}")
    print(f"Relevance: {result['evaluation']['relevance_score']}")
    print(f"Latency: {result['latency_ms']}ms")

asyncio.run(test_agent())
```

### Integrate with API Server

```python
# In api_server.py
from evaluation.agent_wrapper import get_evaluated_agent

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
        "metrics": {
            "confidence": result['evaluation']['intent_confidence'],
            "relevance": result['evaluation']['relevance_score']
        }
    }
```

## 📊 View Results

### CLI Reports

```bash
# View summary
python run_evaluation.py --report --days 7

# Run specific category
python run_evaluation.py --category NAV_QUERY
```

### SQL Queries

```sql
-- Connect to database
psql -U mf_agent -d mf_agent_eval

-- View recent evaluations
SELECT 
    user_prompt,
    intent_predicted,
    relevance_score,
    passed_threshold,
    timestamp
FROM agent_evaluations
ORDER BY timestamp DESC
LIMIT 10;

-- Performance overview
SELECT * FROM performance_overview;
```

### Python Queries

```python
from database.db import get_eval_db

db = get_eval_db()

# Get performance summary
summary = db.get_performance_summary(days=7)
print(f"Pass Rate: {summary['summary']['pass_rate']:.2%}")
print(f"Avg Relevance: {summary['summary']['avg_relevance']:.2f}")

# Get recent evaluations
recent = db.get_evaluations(limit=10)
for eval in recent:
    print(f"{eval['timestamp']}: {eval['user_prompt'][:50]}...")
```

## 🎯 What Gets Tracked

Every interaction logs:
- ✅ User prompt & agent response
- ✅ Intent prediction & confidence
- ✅ DeepEval metrics (relevance, hallucination, faithfulness)
- ✅ Latency breakdown (total, LLM, tool, API)
- ✅ Tools used & API sources
- ✅ Safety checks (disclaimer, PII, risk keywords)
- ✅ Session tracking & conversation turns

## 🔍 Common Commands

```bash
# View test cases
python -c "from database.db import get_eval_db; cases = get_eval_db().get_test_cases(); print(len(cases), 'test cases')"

# Check database connection
psql -U mf_agent -d mf_agent_eval -c "SELECT COUNT(*) FROM agent_evaluations;"

# Run single test
python run_evaluation.py --category GENERAL_CONCEPT

# View logs
tail -f logs/agent.log
```

## 🚨 Troubleshooting

### "Connection refused" error
```bash
# Check if PostgreSQL is running
sudo systemctl status postgresql  # Linux
brew services list  # macOS
```

### "No module named 'deepeval'" error
```bash
pip install deepeval --upgrade
```

### "Permission denied" database error
```bash
# Reconnect as postgres user
psql postgres
GRANT ALL PRIVILEGES ON DATABASE mf_agent_eval TO mf_agent;
\q
```

## 📖 Next Steps

1. Read full documentation: `docs/EVALUATION_SETUP.md`
2. Add custom test cases (see integration examples)
3. Set up monitoring dashboards
4. Configure cron jobs for daily metrics
5. Tune confidence thresholds based on results

## 💡 Tips

- Use `expected_intent` parameter for supervised evaluation
- Monitor `passed_threshold` rate to tune confidence threshold
- Check `hallucination_score` for quality issues
- Track `latency_ms` to optimize performance
- Review failed test cases in `evaluation_test_cases` table
