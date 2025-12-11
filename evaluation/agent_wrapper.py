"""
Agent wrapper with integrated evaluation pipeline
Automatically logs and evaluates every interaction
"""

import time
import uuid
from typing import Dict, Any, Optional, List

from agent.core import MutualFundsAgent
from agent.config import AgentConfig
from evaluation.pipeline import get_evaluation_pipeline
from utils.logger import get_logger

logger = get_logger(__name__)


class EvaluatedAgent:
    """
    Wrapper around MutualFundsAgent that automatically evaluates
    and stores metrics for every interaction
    """
    
    def __init__(self, config: Optional[AgentConfig] = None):
        self.config = config or AgentConfig()
        self.agent = MutualFundsAgent(self.config)
        self.evaluation_pipeline = get_evaluation_pipeline()
        self.session_conversations = {}  # Track conversation turns per session
        
    async def process_request_with_evaluation(
        self,
        user_prompt: str,
        session_id: Optional[str] = None,
        user_name: Optional[str] = None,
        expected_intent: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Process user request through agent and evaluate the interaction
        
        Args:
            user_prompt: User's query
            session_id: Session identifier (generated if not provided)
            user_name: User's name for personalization
            expected_intent: Expected intent for supervised evaluation
            **kwargs: Additional parameters for agent
            
        Returns:
            Dict containing response and evaluation metrics
        """
        
        # Generate session ID if not provided
        if session_id is None:
            session_id = str(uuid.uuid4())
        
        # Track conversation turn
        if session_id not in self.session_conversations:
            self.session_conversations[session_id] = 0
        self.session_conversations[session_id] += 1
        conversation_turn = self.session_conversations[session_id]
        
        logger.info(f"📨 Processing request for session {session_id}, turn {conversation_turn}")
        
        # Start timing
        start_time = time.time()
        llm_start = start_time
        
        try:
            # Parse intent first
            intent_data = await self.agent.intent_parser.parse(user_prompt)
            
            intent_info = {
                'intent': intent_data.intent.value if hasattr(intent_data.intent, 'value') else str(intent_data.intent),
                'confidence': getattr(intent_data, 'confidence', 0.0),
                'entities': {
                    'fund_names': getattr(intent_data, 'fund_names', []),
                    'metrics': getattr(intent_data, 'metrics_requested', []),
                    'time_periods': getattr(intent_data, 'time_periods', [])
                }
            }
            
            # Process through agent
            agent_response = await self.agent.process_request(
                user_input=user_prompt,
                user_name=user_name,
                **kwargs
            )
            
            # Calculate latencies
            total_time = (time.time() - start_time) * 1000  # ms
            llm_time = (time.time() - llm_start) * 1000
            
            # Extract retrieval context (placeholder - adjust based on your agent's implementation)
            retrieval_context = self._extract_retrieval_context(agent_response)
            
            # Prepare latency data
            latency_data = {
                'total_ms': int(total_time),
                'llm_ms': int(llm_time),
                'tool_ms': 0,  # TODO: Extract from agent if available
                'api_ms': 0   # TODO: Extract from agent if available
            }
            
            # Prepare metadata
            metadata = {
                'conversation_turn': conversation_turn,
                'tools_used': self._extract_tools_used(agent_response),
                'api_source': self._extract_api_source(agent_response),
                'retrieval_path': 'LANGCHAIN_AGENT',
                'llm_model': 'KIMI-K2',
                'toolchain_version': '1.0.0',
                'error_occurred': False,
                'fallback_triggered': False,
                'user_id': kwargs.get('user_id')
            }
            
            # Run evaluation
            evaluation_results = self.evaluation_pipeline.evaluate_interaction(
                user_prompt=user_prompt,
                agent_response=agent_response,
                session_id=session_id,
                intent_data=intent_info,
                retrieval_context=retrieval_context,
                latency_data=latency_data,
                metadata=metadata,
                user_name=user_name,
                expected_intent=expected_intent
            )
            
            return {
                'response': agent_response,
                'session_id': session_id,
                'conversation_turn': conversation_turn,
                'evaluation': evaluation_results,
                'intent': intent_info,
                'latency_ms': int(total_time)
            }
            
        except Exception as e:
            error_time = (time.time() - start_time) * 1000
            logger.error(f"❌ Agent processing failed: {e}")
            
            # Log error to evaluation
            error_metadata = {
                'conversation_turn': conversation_turn,
                'error_occurred': True,
                'error_message': str(e),
                'llm_model': 'KIMI-K2',
                'user_id': kwargs.get('user_id')
            }
            
            error_response = f"I encountered an error: {str(e)}. Please try rephrasing your question."
            
            evaluation_results = self.evaluation_pipeline.evaluate_interaction(
                user_prompt=user_prompt,
                agent_response=error_response,
                session_id=session_id,
                intent_data={'intent': 'ERROR', 'confidence': 0.0, 'entities': {}},
                retrieval_context=[],
                latency_data={'total_ms': int(error_time), 'llm_ms': 0, 'tool_ms': 0, 'api_ms': 0},
                metadata=error_metadata,
                user_name=user_name
            )
            
            return {
                'response': error_response,
                'session_id': session_id,
                'conversation_turn': conversation_turn,
                'evaluation': evaluation_results,
                'error': str(e),
                'latency_ms': int(error_time)
            }
    
    def _extract_retrieval_context(self, response: str) -> List[str]:
        """Extract retrieval context from agent response"""
        # This is a placeholder - adjust based on how your agent stores context
        # You might want to modify the agent to return this information
        return [response[:500]]  # Use first 500 chars as context for now
    
    def _extract_tools_used(self, response: str) -> List[str]:
        """Extract which tools were used from response"""
        # Placeholder - you can enhance this to parse from agent's intermediate steps
        tools = []
        if 'NAV' in response or 'Net Asset Value' in response:
            tools.append('search_funds_db')
        if 'mutual fund' in response.lower() and len(response) > 500:
            tools.append('search_tavily_data')
        return tools
    
    def _extract_api_source(self, response: str) -> str:
        """Determine which API source was primarily used"""
        # Placeholder - enhance based on agent's actual source tracking
        if 'API' in response:
            return 'PRODUCTION_API'
        elif 'AMFI' in response:
            return 'AMFI'
        elif 'BSE' in response:
            return 'BSE'
        else:
            return 'GROQ_LLM'
    
    def get_session_metrics(self, session_id: str) -> Dict[str, Any]:
        """Get evaluation metrics for a specific session"""
        return self.evaluation_pipeline.db.get_evaluations(
            filters={'session_id': session_id}
        )
    
    def get_performance_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get aggregated performance metrics"""
        return self.evaluation_pipeline.db.get_performance_summary(days)


# Singleton instance
_evaluated_agent_instance = None

def get_evaluated_agent(config: Optional[AgentConfig] = None) -> EvaluatedAgent:
    """Get or create evaluated agent instance"""
    global _evaluated_agent_instance
    if _evaluated_agent_instance is None:
        _evaluated_agent_instance = EvaluatedAgent(config)
    return _evaluated_agent_instance
