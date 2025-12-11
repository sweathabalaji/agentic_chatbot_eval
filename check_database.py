#!/usr/bin/env python3
"""
Quick script to check database evaluation results
Usage: python3 check_database.py
"""

import psycopg2
from tabulate import tabulate
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection
conn = psycopg2.connect(
    dbname="mf_agent_eval",
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", ""),
    host=os.getenv("DB_HOST", "localhost"),
    port=os.getenv("DB_PORT", "5432")
)

def show_recent_evaluations(limit=10):
    """Show recent evaluation results"""
    cursor = conn.cursor()
    
    query = """
    SELECT 
        id,
        session_id,
        intent_predicted,
        ROUND(intent_confidence::numeric, 2) as confidence,
        ROUND(relevance_score::numeric, 2) as relevance,
        ROUND(faithfulness_score::numeric, 2) as faithfulness,
        ROUND(answer_correctness::numeric, 2) as correctness,
        total_latency_ms,
        TO_CHAR(timestamp, 'MM-DD HH24:MI') as time
    FROM agent_evaluations
    ORDER BY timestamp DESC
    LIMIT %s;
    """
    
    cursor.execute(query, (limit,))
    rows = cursor.fetchall()
    
    headers = ['ID', 'Session', 'Intent', 'Conf', 'Rel', 'Faith', 'Correct', 'Latency(ms)', 'Time']
    print(f"\n📊 Recent {limit} Evaluations:")
    print("=" * 120)
    print(tabulate(rows, headers=headers, tablefmt='grid'))
    
    cursor.close()

def show_evaluation_stats():
    """Show overall statistics"""
    cursor = conn.cursor()
    
    query = """
    SELECT 
        COUNT(*) as total_evals,
        ROUND(AVG(relevance_score)::numeric, 3) as avg_relevance,
        ROUND(AVG(faithfulness_score)::numeric, 3) as avg_faithfulness,
        ROUND(AVG(answer_correctness)::numeric, 3) as avg_correctness,
        ROUND(AVG(total_latency_ms)::numeric, 0) as avg_latency_ms,
        COUNT(DISTINCT session_id) as unique_sessions
    FROM agent_evaluations;
    """
    
    cursor.execute(query)
    row = cursor.fetchone()
    
    print("\n📈 Overall Statistics:")
    print("=" * 60)
    print(f"Total Evaluations: {row[0]}")
    print(f"Average Relevance: {row[1]}")
    print(f"Average Faithfulness: {row[2]}")
    print(f"Average Correctness: {row[3]}")
    print(f"Average Latency: {row[4]} ms")
    print(f"Unique Sessions: {row[5]}")
    
    cursor.close()

def show_intent_breakdown():
    """Show evaluation breakdown by intent type"""
    cursor = conn.cursor()
    
    query = """
    SELECT 
        intent_predicted,
        COUNT(*) as count,
        ROUND(AVG(relevance_score)::numeric, 2) as avg_relevance,
        ROUND(AVG(faithfulness_score)::numeric, 2) as avg_faithfulness
    FROM agent_evaluations
    WHERE intent_predicted IS NOT NULL
    GROUP BY intent_predicted
    ORDER BY count DESC;
    """
    
    cursor.execute(query)
    rows = cursor.fetchall()
    
    headers = ['Intent Type', 'Count', 'Avg Relevance', 'Avg Faithfulness']
    print("\n🎯 Intent Type Breakdown:")
    print("=" * 80)
    print(tabulate(rows, headers=headers, tablefmt='grid'))
    
    cursor.close()

def show_specific_evaluation(eval_id):
    """Show detailed information for a specific evaluation"""
    cursor = conn.cursor()
    
    query = """
    SELECT 
        id,
        session_id,
        user_prompt,
        agent_response,
        intent_predicted,
        intent_confidence,
        relevance_score,
        faithfulness_score,
        hallucination_score,
        contextual_relevance,
        answer_correctness,
        total_latency_ms,
        tools_used,
        timestamp
    FROM agent_evaluations
    WHERE id = %s;
    """
    
    cursor.execute(query, (eval_id,))
    row = cursor.fetchone()
    
    if row:
        print(f"\n🔍 Evaluation #{row[0]} Details:")
        print("=" * 100)
        print(f"Session ID: {row[1]}")
        print(f"Created: {row[13]}")
        print(f"\nUser Query: {row[2]}")
        print(f"\nAgent Response: {row[3]}")  # Show full response
        print(f"\n📊 Metrics:")
        print(f"  Intent: {row[4]} (confidence: {row[5]})")
        print(f"  Relevance: {row[6]}")
        print(f"  Faithfulness: {row[7]}")
        print(f"  Hallucination: {row[8]}")
        print(f"  Contextual Relevance: {row[9]}")
        print(f"  Answer Correctness: {row[10]}")
        print(f"  Latency: {row[11]} ms")
        print(f"  Tools Used: {row[12]}")
    else:
        print(f"❌ No evaluation found with ID {eval_id}")
    
    cursor.close()

if __name__ == "__main__":
    try:
        print("\n" + "="*120)
        print("🗄️  MUTUAL FUNDS AGENT - EVALUATION DATABASE VIEWER")
        print("="*120)
        
        # Show statistics
        show_evaluation_stats()
        
        # Show intent breakdown
        show_intent_breakdown()
        
        # Show recent evaluations
        show_recent_evaluations(10)
        
        # Show latest evaluation in detail
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(id) FROM agent_evaluations;")
        latest_id = cursor.fetchone()[0]
        cursor.close()
        
        if latest_id:
            show_specific_evaluation(latest_id)
        
        print("\n" + "="*120)
        print("✅ Database check complete!")
        print("\n💡 To check specific evaluation: show_specific_evaluation(eval_id)")
        print("="*120 + "\n")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        conn.close()
