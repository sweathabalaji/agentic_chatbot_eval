# How Evaluation Metrics Are Calculated
## Authoritative vs Non-Authoritative Methods Explained

---

## 📊 Overview: Two-Tier Calculation System

The evaluation system uses **TWO different approaches**:

### 1. **Authoritative (LLM-Based Judgment)** 
Used for: Quality Metrics (Relevance, Faithfulness, Hallucination, Contextual Relevance)
- Groq LLM acts as an "expert judge"
- Evaluates subjective quality aspects
- Returns scores 0.0-1.0 based on criteria

### 2. **Non-Authoritative (Mathematical Calculation)**
Used for: Performance Metrics, Composite Scores
- Direct measurement (timestamps, counters)
- Mathematical formulas
- Objective, deterministic values

---

## 🎯 Quality Metrics (AUTHORITATIVE - LLM-Based)

These metrics use **Groq LLM as an authoritative judge** to evaluate quality aspects that require understanding and reasoning.

### 1. Relevance Score (0.0 - 1.0)

**Question:** "How relevant is the response to the user's query?"

**Method:** AUTHORITATIVE (Groq LLM Judgment)

**How it works:**
```python
# Step 1: Create evaluation prompt
relevance_prompt = f"""
Evaluate how relevant the response is to the query. 
Rate on a scale of 0.0 to 1.0.

QUERY: {user_query}
RESPONSE: {agent_response}

EVALUATION CRITERIA:
- 1.0 = Directly answers the question with complete information
- 0.8-0.9 = Answers the question well with good detail
- 0.6-0.7 = Answers the question but could be more complete
- 0.4-0.5 = Partially answers, missing some key points
- 0.0-0.3 = Does not address the question

YOUR SCORE (respond with ONLY a decimal number like 0.85):
"""

# Step 2: Send to Groq LLM
llm = ChatOpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=GROQ_API_KEY,
    model="moonshotai/kimi-k2-instruct",
    temperature=0.0  # Deterministic
)

relevance_result = llm.invoke(relevance_prompt)

# Step 3: Extract score from LLM response
# LLM might respond: "0.85" or "The score is 0.85"
import re
score_match = re.search(r'([0-1](?:\.\d+)?)', relevance_result.content)
relevance_score = float(score_match.group(1))

# Step 4: Ensure score is in valid range
relevance_score = max(0.0, min(1.0, relevance_score))
```

**Example:**
```
Query: "What is the NAV of HDFC Top 100 Fund?"
Response: "The current NAV of HDFC Top 100 Fund is ₹842.50 as of Dec 9, 2025."

Groq LLM evaluates:
- Does response answer the query? YES ✓
- Is it complete? YES ✓
- Is it accurate? YES ✓

Groq LLM returns: "1.0"
Final Relevance Score: 1.0
```

**Why Authoritative?**
- Requires understanding of semantic meaning
- Needs to judge if response "addresses" the query
- Subjective evaluation that humans would do
- LLM acts as expert evaluator

---

### 2. Faithfulness Score (0.0 - 1.0)

**Question:** "Is the response grounded in the retrieved context?"

**Method:** AUTHORITATIVE (Groq LLM Judgment)

**How it works:**
```python
# Step 1: Create evaluation prompt with context
context_text = "\n".join(retrieval_context)

faithfulness_prompt = f"""
Evaluate if the response is faithful to the provided context.
Rate on a scale of 0.0 to 1.0.

CONTEXT: {context_text}
RESPONSE: {agent_response}

EVALUATION CRITERIA:
- 1.0 = Every fact/number in response is directly from context
- 0.8-0.9 = Well-grounded, minor reasonable inferences
- 0.6-0.7 = Mostly grounded but has some unsupported details
- 0.4-0.5 = Mix of grounded and ungrounded information
- 0.0-0.3 = Contains many claims not supported by context

YOUR SCORE (respond with ONLY a decimal number like 0.95):
"""

# Step 2: Send to Groq LLM
faithfulness_result = llm.invoke(faithfulness_prompt)

# Step 3: Extract and validate score
faithfulness_score = extract_score(faithfulness_result.content)
```

**Example:**
```
Context: {"nav": 842.50, "date": "2025-12-09", "fund_name": "HDFC Top 100"}
Response: "The NAV is ₹842.50 as of Dec 9, 2025."

Groq LLM checks:
- Is ₹842.50 in context? YES ✓ (matches "nav": 842.50)
- Is Dec 9, 2025 in context? YES ✓ (matches "date": "2025-12-09")
- Any fabricated info? NO ✓

Groq LLM returns: "1.0"
Final Faithfulness Score: 1.0
```

**Why Authoritative?**
- Needs to understand semantic equivalence (₹842.50 = "nav": 842.50)
- Must detect subtle fabrications
- Requires reasoning about what's "grounded"
- LLM can understand context better than regex

---

### 3. Hallucination Score (0.0 - 1.0, lower is better)

**Question:** "Does the response contain fabricated information?"

**Method:** AUTHORITATIVE (Groq LLM Judgment)

**How it works:**
```python
# Step 1: Create evaluation prompt
hallucination_prompt = f"""
Evaluate if the response contains hallucinated (fabricated) information.
Rate on a scale of 0.0 to 1.0 (LOWER is better).

CONTEXT: {context_text}
RESPONSE: {agent_response}

EVALUATION CRITERIA:
- 0.0 = No hallucination, everything is from context
- 0.1-0.2 = Minor reasonable inferences, no fabrication
- 0.3-0.5 = Some unsupported details or assumptions
- 0.6-0.8 = Significant fabricated information
- 0.9-1.0 = Mostly or completely fabricated

YOUR SCORE (respond with ONLY a decimal number like 0.15):
"""

# Step 2: Send to Groq LLM
hallucination_result = llm.invoke(hallucination_prompt)

# Step 3: Extract score (inverse of faithfulness)
hallucination_score = extract_score(hallucination_result.content)
```

**Example:**
```
Context: {"nav": 842.50, "date": "2025-12-09"}
Response: "The NAV is ₹842.50 and the fund manager is John Doe."

Groq LLM checks:
- Is ₹842.50 fabricated? NO ✓ (in context)
- Is "John Doe" fabricated? YES ✗ (not in context)

Groq LLM returns: "0.5" (50% hallucination)
Final Hallucination Score: 0.5
```

**Why Authoritative?**
- Inverse of faithfulness but evaluated separately
- Can catch subtle fabrications
- Understands what's "reasonable inference" vs "fabrication"
- LLM judgment more nuanced than simple matching

---

### 4. Contextual Relevance (0.0 - 1.0)

**Question:** "Is the retrieved context relevant for answering the query?"

**Method:** AUTHORITATIVE (Groq LLM Judgment)

**How it works:**
```python
# Step 1: Create evaluation prompt
contextual_relevance_prompt = f"""
Evaluate if the retrieved context is relevant for answering the query.
Rate on a scale of 0.0 to 1.0.

QUERY: {user_query}
CONTEXT: {context_text}

EVALUATION CRITERIA:
- 1.0 = Context directly contains information needed to answer
- 0.8-0.9 = Context is highly relevant and useful
- 0.6-0.7 = Context is somewhat relevant
- 0.4-0.5 = Context is marginally relevant
- 0.0-0.3 = Context is irrelevant or unhelpful

YOUR SCORE (respond with ONLY a decimal number like 0.90):
"""

# Step 2: Send to Groq LLM
contextual_result = llm.invoke(contextual_relevance_prompt)

# Step 3: Extract score
contextual_relevance_score = extract_score(contextual_result.content)
```

**Example:**
```
Query: "What is the NAV of HDFC Fund?"
Context: {"nav": 842.50, "date": "2025-12-09", "fund_name": "HDFC Top 100"}

Groq LLM checks:
- Does context have NAV info? YES ✓
- Is it for the right fund? YES ✓
- Can this answer the query? YES ✓

Groq LLM returns: "1.0"
Final Contextual Relevance Score: 1.0
```

**Why Authoritative?**
- Evaluates quality of retrieval system
- Needs to understand if context "helps" answer query
- Subjective judgment of relevance
- LLM can assess information utility

---

## 🧮 Composite Metrics (MATHEMATICAL - Formula-Based)

These metrics use **mathematical formulas** on the authoritative scores.

### 5. Answer Correctness (Composite Score)

**Question:** "Overall, how correct is the answer?"

**Method:** NON-AUTHORITATIVE (Mathematical Formula)

**How it works:**
```python
# Formula: Weighted average of Relevance and Faithfulness
answer_correctness = (relevance_score * 0.7) + (faithfulness_score * 0.3)

# Why this formula?
# - Relevance (70%): Most important - does it answer the question?
# - Faithfulness (30%): Important - is it grounded in facts?
```

**Example:**
```
Relevance Score: 0.90 (from Groq LLM)
Faithfulness Score: 1.00 (from Groq LLM)

Calculation:
answer_correctness = (0.90 × 0.7) + (1.00 × 0.3)
                   = 0.63 + 0.30
                   = 0.93

Final Answer Correctness: 0.93
```

**Why Non-Authoritative?**
- Simple weighted average
- Deterministic calculation
- No LLM judgment needed
- Combines two authoritative scores mathematically

---

## ⏱️ Performance Metrics (NON-AUTHORITATIVE - Direct Measurement)

These metrics use **direct measurement** with timestamps and counters.

### 1. Total Latency (milliseconds)

**Method:** NON-AUTHORITATIVE (Timestamp Measurement)

**How it works:**
```python
# Step 1: Record start time
start_time = time.time()

# Step 2: Process user request
response = agent.process_request(user_input)

# Step 3: Record end time
end_time = time.time()

# Step 4: Calculate latency
total_latency_ms = int((end_time - start_time) * 1000)
```

**Example:**
```
Start: 12:00:00.000
End:   12:00:04.230

Calculation:
total_latency_ms = (4.230 - 0.000) × 1000
                 = 4,230 milliseconds

Final Total Latency: 4,230ms
```

**Why Non-Authoritative?**
- Objective measurement
- No judgment needed
- Simple arithmetic
- Deterministic

---

### 2. LLM Latency (milliseconds)

**Method:** NON-AUTHORITATIVE (Timestamp Measurement)

**How it works:**
```python
# Step 1: Record start before LLM call
llm_start = time.time()

# Step 2: Call Groq LLM
response = llm.invoke(prompt)

# Step 3: Record end after LLM call
llm_end = time.time()

# Step 4: Calculate LLM latency
llm_latency_ms = int((llm_end - llm_start) * 1000)
```

**Example:**
```
LLM Start: 12:00:01.000
LLM End:   12:00:02.200

Calculation:
llm_latency_ms = (2.200 - 1.000) × 1000
               = 1,200 milliseconds

Final LLM Latency: 1,200ms (28% of total)
```

---

### 3. Tool Latency (milliseconds)

**Method:** NON-AUTHORITATIVE (Timestamp Measurement)

**How it works:**
```python
# Step 1: Record start before tool execution
tool_start = time.time()

# Step 2: Execute tool (e.g., API call)
result = tool_orchestrator.search_funds_db(fund_name)

# Step 3: Record end after tool execution
tool_end = time.time()

# Step 4: Calculate tool latency
tool_latency_ms = int((tool_end - tool_start) * 1000)
```

**Example:**
```
Tool Start: 12:00:01.500
Tool End:   12:00:04.300

Calculation:
tool_latency_ms = (4.300 - 1.500) × 1000
                = 2,800 milliseconds

Final Tool Latency: 2,800ms (66% of total)
```

---

### 4. API Latency (milliseconds)

**Method:** NON-AUTHORITATIVE (Timestamp Measurement)

**How it works:**
```python
# Step 1: Record start before API call
api_start = time.time()

# Step 2: Make HTTP request to external API
response = requests.get(f"{API_BASE}/api/funds/{isin}")

# Step 3: Record end after API response
api_end = time.time()

# Step 4: Calculate API latency
api_latency_ms = int((api_end - api_start) * 1000)
```

**Example:**
```
API Start: 12:00:02.000
API End:   12:00:02.230

Calculation:
api_latency_ms = (2.230 - 2.000) × 1000
               = 230 milliseconds

Final API Latency: 230ms (5% of total)
```

---

### 5. Tool Call Count

**Method:** NON-AUTHORITATIVE (Counter)

**How it works:**
```python
# Initialize counter
tool_call_count = 0

# Increment for each tool call
def execute_tool(tool_name, args):
    global tool_call_count
    tool_call_count += 1
    return tool.run(args)

# Final count
num_tool_calls = tool_call_count
```

**Example:**
```
Query: "Compare HDFC and Axis funds"

Tools called:
1. search_funds_db("HDFC") → tool_call_count = 1
2. search_funds_db("Axis") → tool_call_count = 2
3. compare_funds(hdfc, axis) → tool_call_count = 3

Final Tool Call Count: 3
```

---

## 📊 Summary: Authoritative vs Non-Authoritative

| Metric | Type | Method | Why? |
|--------|------|--------|------|
| **Relevance** | Authoritative | Groq LLM judgment | Needs semantic understanding |
| **Faithfulness** | Authoritative | Groq LLM judgment | Needs to detect fabrication |
| **Hallucination** | Authoritative | Groq LLM judgment | Inverse of faithfulness |
| **Contextual Relevance** | Authoritative | Groq LLM judgment | Evaluates retrieval quality |
| **Answer Correctness** | Non-Authoritative | Math formula | Weighted average |
| **Total Latency** | Non-Authoritative | Timestamp diff | Direct measurement |
| **LLM Latency** | Non-Authoritative | Timestamp diff | Direct measurement |
| **Tool Latency** | Non-Authoritative | Timestamp diff | Direct measurement |
| **API Latency** | Non-Authoritative | Timestamp diff | Direct measurement |
| **Tool Call Count** | Non-Authoritative | Counter | Simple counting |

---

## 🔍 Why Use Groq LLM as Authoritative Judge?

### Advantages:
1. **Semantic Understanding**: Can understand meaning, not just keywords
2. **Nuanced Evaluation**: Distinguishes "reasonable inference" from "fabrication"
3. **Consistent Criteria**: Uses explicit evaluation rubrics
4. **Deterministic**: Temperature=0.0 for consistent scoring
5. **Cost-Effective**: Groq is 69% cheaper than OpenAI

### Example of LLM Advantage:
```
Context: {"nav": 842.50}
Response: "The NAV is ₹842.50"

Simple regex matching: FAIL (₹842.50 ≠ 842.50)
Groq LLM judgment: PASS (understands ₹842.50 = 842.50)
```

---

## 🎯 Real Example: Complete Evaluation

**User Query:** "What is the NAV of HDFC Top 100 Fund?"

**Agent Response:** "The current NAV of HDFC Top 100 Fund is ₹842.50 as of December 9, 2025. This fund has shown consistent performance with a 3-year return of 15.2%."

**Retrieved Context:** 
```json
{
  "nav": 842.50,
  "date": "2025-12-09",
  "fund_name": "HDFC Top 100 Fund",
  "returns_3y": 15.2
}
```

### Evaluation Results:

**1. Relevance (Authoritative - Groq LLM):**
- Groq evaluates: "Response directly answers NAV query with complete info"
- **Score: 1.0** ✅

**2. Faithfulness (Authoritative - Groq LLM):**
- Groq checks: All facts (₹842.50, Dec 9, 15.2%) are in context
- **Score: 1.0** ✅

**3. Hallucination (Authoritative - Groq LLM):**
- Groq checks: No fabricated information
- **Score: 0.0** ✅ (low is good)

**4. Contextual Relevance (Authoritative - Groq LLM):**
- Groq evaluates: Context directly contains NAV info needed
- **Score: 1.0** ✅

**5. Answer Correctness (Non-Authoritative - Math):**
- Formula: (1.0 × 0.7) + (1.0 × 0.3) = 0.7 + 0.3 = **1.0** ✅

**6. Total Latency (Non-Authoritative - Measurement):**
- Start: 12:00:00.000, End: 12:00:03.500
- **3,500ms**

**7. LLM Latency (Non-Authoritative - Measurement):**
- LLM call took **1,200ms** (34% of total)

**8. Tool Latency (Non-Authoritative - Measurement):**
- Tool execution took **2,100ms** (60% of total)

**9. API Latency (Non-Authoritative - Measurement):**
- API call took **200ms** (6% of total)

**10. Tool Call Count (Non-Authoritative - Counter):**
- **2 tools** called (search_funds_db, get_fund_by_isin)

---

## 🎓 Key Takeaways for Your Presentation

1. **Quality Metrics = Authoritative (Groq LLM)**
   - Requires understanding and judgment
   - LLM acts as expert evaluator
   - Subjective but consistent

2. **Performance Metrics = Non-Authoritative (Math/Measurement)**
   - Direct measurement with timestamps
   - Objective and deterministic
   - Simple arithmetic

3. **Best of Both Worlds:**
   - Authoritative for quality (needs intelligence)
   - Non-authoritative for performance (needs precision)
   - Combined for comprehensive evaluation

4. **Why This Matters:**
   - Can't use simple regex for "relevance" (needs understanding)
   - Can't use LLM for "latency" (needs precise measurement)
   - Right tool for the right job

---

**For your presentation, emphasize:**
- Groq LLM provides **authoritative judgment** on quality (like a human expert)
- Timestamps provide **objective measurement** on performance (like a stopwatch)
- This hybrid approach gives **comprehensive evaluation** with both intelligence and precision
