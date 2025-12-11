"""
Database connection and operations for agent evaluation storage
"""

import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from contextlib import contextmanager

from utils.logger import get_logger

logger = get_logger(__name__)


class EvaluationDB:
    """Handles database operations for agent evaluation metrics"""
    
    def __init__(self):
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'mf_agent_eval'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'postgres')
        }
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = None
        try:
            conn = psycopg2.connect(**self.db_config)
            yield conn
            conn.commit()
        except Exception as e:
            if conn:
                conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            if conn:
                conn.close()
    
    def save_evaluation(self, data: Dict[str, Any]) -> int:
        """
        Save evaluation metrics to database
        
        Args:
            data: Dictionary containing all evaluation metrics
            
        Returns:
            ID of inserted record
        """
        query = """
            INSERT INTO agent_evaluations (
                session_id, user_id, user_name, user_prompt, agent_response,
                conversation_turn, intent_predicted, expected_intent, intent_confidence,
                intent_match, entities_extracted, threshold_used, passed_threshold,
                fallback_triggered, relevance_score, hallucination_score, faithfulness_score,
                contextual_relevance, answer_correctness, total_latency_ms, llm_latency_ms,
                tool_latency_ms, api_latency_ms, api_source, tools_used, retrieval_path,
                num_tool_calls, contains_disclaimer, risk_detection_flag, pii_detected,
                response_length, llm_model, agent_version, toolchain_version, environment,
                error_occurred, error_message, retry_count
            ) VALUES (
                %(session_id)s, %(user_id)s, %(user_name)s, %(user_prompt)s, %(agent_response)s,
                %(conversation_turn)s, %(intent_predicted)s, %(expected_intent)s, 
                %(intent_confidence)s, %(intent_match)s, %(entities_extracted)s,
                %(threshold_used)s, %(passed_threshold)s, %(fallback_triggered)s,
                %(relevance_score)s, %(hallucination_score)s, %(faithfulness_score)s,
                %(contextual_relevance)s, %(answer_correctness)s, %(total_latency_ms)s,
                %(llm_latency_ms)s, %(tool_latency_ms)s, %(api_latency_ms)s,
                %(api_source)s, %(tools_used)s, %(retrieval_path)s, %(num_tool_calls)s,
                %(contains_disclaimer)s, %(risk_detection_flag)s, %(pii_detected)s,
                %(response_length)s, %(llm_model)s, %(agent_version)s, %(toolchain_version)s,
                %(environment)s, %(error_occurred)s, %(error_message)s, %(retry_count)s
            ) RETURNING id
        """
        
        try:
            import json
            # Convert dict/list fields to JSON strings for PostgreSQL storage
            data_copy = data.copy()
            if isinstance(data_copy.get('entities_extracted'), dict):
                data_copy['entities_extracted'] = json.dumps(data_copy['entities_extracted'])
            if isinstance(data_copy.get('tools_used'), (list, dict)):
                data_copy['tools_used'] = json.dumps(data_copy['tools_used'])
            
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, data_copy)
                    eval_id = cur.fetchone()[0]
                    logger.info(f"Saved evaluation record with ID: {eval_id}")
                    return eval_id
        except Exception as e:
            logger.error(f"Database error: {e}")
            logger.error(f"Failed to save evaluation: {e}")
            return -1
    
    def get_evaluations(self, filters: Optional[Dict[str, Any]] = None, 
                       limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve evaluation records with optional filters"""
        
        query = "SELECT * FROM agent_evaluations WHERE 1=1"
        params = {}
        
        if filters:
            if 'session_id' in filters:
                query += " AND session_id = %(session_id)s"
                params['session_id'] = filters['session_id']
            if 'intent' in filters:
                query += " AND intent_predicted = %(intent)s"
                params['intent'] = filters['intent']
            if 'date_from' in filters:
                query += " AND timestamp >= %(date_from)s"
                params['date_from'] = filters['date_from']
            if 'date_to' in filters:
                query += " AND timestamp <= %(date_to)s"
                params['date_to'] = filters['date_to']
            if 'passed_threshold' in filters:
                query += " AND passed_threshold = %(passed_threshold)s"
                params['passed_threshold'] = filters['passed_threshold']
        
        query += f" ORDER BY timestamp DESC LIMIT {limit}"
        
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query, params)
                    results = cur.fetchall()
                    return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Failed to retrieve evaluations: {e}")
            return []
    
    def get_performance_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get aggregated performance metrics for the last N days"""
        
        query = """
            SELECT 
                COUNT(*) as total_queries,
                AVG(relevance_score) as avg_relevance,
                AVG(hallucination_score) as avg_hallucination,
                AVG(faithfulness_score) as avg_faithfulness,
                AVG(total_latency_ms) as avg_latency,
                SUM(CASE WHEN passed_threshold THEN 1 ELSE 0 END)::FLOAT / COUNT(*) as pass_rate,
                SUM(CASE WHEN error_occurred THEN 1 ELSE 0 END)::FLOAT / COUNT(*) as error_rate,
                intent_predicted,
                COUNT(*) as intent_count
            FROM agent_evaluations
            WHERE timestamp >= NOW() - INTERVAL '%s days'
            GROUP BY intent_predicted
            ORDER BY intent_count DESC
        """
        
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query, (days,))
                    results = cur.fetchall()
                    return {
                        'summary': dict(results[0]) if results else {},
                        'by_intent': [dict(row) for row in results]
                    }
        except Exception as e:
            logger.error(f"Failed to get performance summary: {e}")
            return {}
    
    def save_test_case(self, test_case: Dict[str, Any]) -> int:
        """Save an evaluation test case"""
        
        query = """
            INSERT INTO evaluation_test_cases (
                test_query, expected_intent, expected_entities,
                expected_response_keywords, category, difficulty
            ) VALUES (
                %(test_query)s, %(expected_intent)s, %(expected_entities)s,
                %(expected_response_keywords)s, %(category)s, %(difficulty)s
            ) RETURNING id
        """
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, test_case)
                    return cur.fetchone()[0]
        except Exception as e:
            logger.error(f"Failed to save test case: {e}")
            return -1
    
    def get_test_cases(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Retrieve test cases, optionally filtered by category"""
        
        query = "SELECT * FROM evaluation_test_cases"
        params = {}
        
        if category:
            query += " WHERE category = %(category)s"
            params['category'] = category
        
        try:
            with self.get_connection() as conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(query, params)
                    return [dict(row) for row in cur.fetchall()]
        except Exception as e:
            logger.error(f"Failed to get test cases: {e}")
            return []
    
    def create_threshold_experiment(self, name: str, threshold: float, 
                                   notes: Optional[str] = None) -> int:
        """Create a new threshold experiment"""
        
        query = """
            INSERT INTO threshold_experiments (
                experiment_name, threshold_value, notes
            ) VALUES (%(name)s, %(threshold)s, %(notes)s)
            RETURNING id
        """
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query, {
                        'name': name,
                        'threshold': threshold,
                        'notes': notes
                    })
                    return cur.fetchone()[0]
        except Exception as e:
            logger.error(f"Failed to create experiment: {e}")
            return -1
    
    def update_daily_metrics(self):
        """Update aggregated daily metrics (run as daily cron job)"""
        
        query = """
            INSERT INTO daily_metrics (
                date, total_queries, avg_relevance_score, avg_hallucination_score,
                avg_faithfulness_score, avg_latency_ms, pass_rate, error_rate, top_intents
            )
            SELECT 
                DATE(timestamp) as date,
                COUNT(*) as total_queries,
                AVG(relevance_score) as avg_relevance_score,
                AVG(hallucination_score) as avg_hallucination_score,
                AVG(faithfulness_score) as avg_faithfulness_score,
                AVG(total_latency_ms) as avg_latency_ms,
                SUM(CASE WHEN passed_threshold THEN 1 ELSE 0 END)::FLOAT / COUNT(*) as pass_rate,
                SUM(CASE WHEN error_occurred THEN 1 ELSE 0 END)::FLOAT / COUNT(*) as error_rate,
                jsonb_agg(
                    jsonb_build_object('intent', intent_predicted, 'count', COUNT(*))
                    ORDER BY COUNT(*) DESC
                ) FILTER (WHERE intent_predicted IS NOT NULL) as top_intents
            FROM agent_evaluations
            WHERE DATE(timestamp) = CURRENT_DATE - INTERVAL '1 day'
            GROUP BY DATE(timestamp)
            ON CONFLICT (date) DO UPDATE SET
                total_queries = EXCLUDED.total_queries,
                avg_relevance_score = EXCLUDED.avg_relevance_score,
                avg_hallucination_score = EXCLUDED.avg_hallucination_score,
                avg_faithfulness_score = EXCLUDED.avg_faithfulness_score,
                avg_latency_ms = EXCLUDED.avg_latency_ms,
                pass_rate = EXCLUDED.pass_rate,
                error_rate = EXCLUDED.error_rate,
                top_intents = EXCLUDED.top_intents
        """
        
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    logger.info("Daily metrics updated successfully")
        except Exception as e:
            logger.error(f"Failed to update daily metrics: {e}")


# Singleton instance
_db_instance = None

def get_eval_db() -> EvaluationDB:
    """Get or create database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = EvaluationDB()
    return _db_instance
