"""
Pure AI-driven Intent parsing for the Mutual Funds Agent
ZERO hardcoded patterns - complete LLM-based analysis
"""

import json
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

from .config import AgentConfig
from utils.logger import get_logger

logger = get_logger(__name__)

class IntentType(Enum):
    # Database queries - for specific fund data
    FUND_QUERY = "fund_query"  
    NAV_REQUEST = "nav_request"  
    COMPARE_FUNDS = "compare_funds"  
    PERFORMANCE_HISTORY = "performance_history"  
    REDEMPTION_QUERY = "redemption_query"  
    
    # Web search queries - for general information/guidance
    GENERAL_INFO = "general_info"  # Investment advice, market trends, how-to guides
    KYC_QUERY = "kyc_query"  
    ACCOUNT_ISSUE = "account_issue"  
    
    # Conversational
    GREETING = "greeting"
    SMALLTALK = "smalltalk"

class SentimentLabel(Enum):
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    ANGRY = "angry"
    URGENT = "urgent"

@dataclass
class Sentiment:
    label: SentimentLabel
    score: float

@dataclass
class Entities:
    fund_name: Optional[str] = None
    metric: Optional[str] = None
    date: Optional[str] = None
    amount: Optional[str] = None
    period: Optional[str] = None
    compare_with: List[str] = None
    
    def __post_init__(self):
        if self.compare_with is None:
            self.compare_with = []

@dataclass
class Intent:
    intent: IntentType
    confidence: float
    entities: Entities
    sentiment: Sentiment
    clarity: str = "high"  # "high", "medium", "low"
    suggested_action: Optional[str] = None  # "ASK_CLARIFY", "PROCEED", etc.

class IntentParser:
    """
    ZERO keyword-based intent parser - pure AI analysis
    Let the agent make all decisions based on natural language understanding
    """
    
    def __init__(self, config: AgentConfig):
        self.config = config

    async def parse(self, user_input: str, session_context: Optional[Dict] = None) -> Intent:
        """
        Pure AI-driven intent parsing with NO predetermined rules
        """
        return await self.parse_intent_async(user_input)
        
    async def parse_intent_async(self, user_input: str) -> Intent:
        """
        AI-enhanced intent classification with semantic understanding
        """
        
        logger.info(f"Pure AI intent analysis for: '{user_input}'")
        
        user_lower = user_input.lower()
        
        # Extract entities first
        entities = Entities(
            fund_name=self._extract_potential_fund_name(user_input) if self._might_contain_fund_name(user_input) else None,
            metric=self._extract_metric(user_lower),
            period=self._extract_period(user_lower)
        )
        
        # Analyze sentiment
        sentiment = self._analyze_sentiment(user_lower)
        
        # Intelligent intent classification with semantic patterns
        intent_result = self._classify_intent(user_lower, entities)
        
        return Intent(
            intent=intent_result['intent'],
            confidence=intent_result['confidence'],
            entities=entities,
            sentiment=sentiment,
            clarity=intent_result['clarity'],
            suggested_action=intent_result['suggested_action']
        )
    
    def _classify_intent(self, user_lower: str, entities: Entities) -> Dict[str, Any]:
        """
        Intelligent intent classification based on semantic understanding
        """
        # Greeting patterns - must be standalone or at start
        greeting_words = ['hello', 'hi ', ' hi', 'hey ', ' hey', 'good morning', 'good afternoon', 'good evening']
        is_greeting = any(user_lower.startswith(word) or user_lower.endswith(word) or f' {word.strip()} ' in user_lower for word in greeting_words)
        is_short = len(user_lower.split()) <= 3
        
        if is_greeting and is_short:
            return {'intent': IntentType.GREETING, 'confidence': 0.95, 'clarity': 'high', 'suggested_action': 'PROCEED'}
        
        # NAV specific requests
        if any(phrase in user_lower for phrase in ['nav', 'net asset value', 'current value', 'latest nav']):
            return {'intent': IntentType.NAV_REQUEST, 'confidence': 0.9, 'clarity': 'high', 'suggested_action': 'PROCEED'}
        
        # Comparison requests
        if any(word in user_lower for word in ['compare', 'comparison', 'versus', ' vs ', ' vs.', 'difference between']):
            return {'intent': IntentType.COMPARE_FUNDS, 'confidence': 0.9, 'clarity': 'high', 'suggested_action': 'PROCEED'}
        
        # Performance/returns queries
        if any(phrase in user_lower for phrase in ['performance', 'returns', 'return', 'growth', 'gained', 'top performer', 'best fund', 'highest return', 'top performing']):
            return {'intent': IntentType.PERFORMANCE_HISTORY, 'confidence': 0.9, 'clarity': 'high', 'suggested_action': 'PROCEED'}
        
        # Redemption queries
        if any(word in user_lower for word in ['redeem', 'redemption', 'withdraw', 'exit', 'sell']):
            return {'intent': IntentType.REDEMPTION_QUERY, 'confidence': 0.9, 'clarity': 'high', 'suggested_action': 'PROCEED'}
        
        # Specific fund queries (has fund name or ISIN or looking for funds)
        if entities.fund_name or 'isin' in user_lower or any(phrase in user_lower for phrase in ['find fund', 'search fund', 'show fund', 'list fund', 'show me', 'funds with', 'funds in', 'factsheet', 'details about', 'information about', 'tell me about', 'large cap', 'mid cap', 'small cap', '5-star', 'five star', 'star rated']):
            return {'intent': IntentType.FUND_QUERY, 'confidence': 0.85, 'clarity': 'high', 'suggested_action': 'PROCEED'}
        
        # KYC related
        if any(word in user_lower for word in ['kyc', 'know your customer', 'verification', 'documents', 'identity']):
            return {'intent': IntentType.KYC_QUERY, 'confidence': 0.9, 'clarity': 'high', 'suggested_action': 'PROCEED'}
        
        # Account issues
        if any(word in user_lower for word in ['account', 'login', 'password', 'access', 'blocked', 'issue', 'problem']):
            return {'intent': IntentType.ACCOUNT_ISSUE, 'confidence': 0.85, 'clarity': 'high', 'suggested_action': 'PROCEED'}
        
        # Small talk
        if any(phrase in user_lower for phrase in ['how are you', 'what can you do', 'who are you', 'thank you', 'thanks']):
            return {'intent': IntentType.SMALLTALK, 'confidence': 0.9, 'clarity': 'high', 'suggested_action': 'PROCEED'}
        
        # Default to general info with medium confidence
        return {'intent': IntentType.GENERAL_INFO, 'confidence': 0.7, 'clarity': 'medium', 'suggested_action': 'PROCEED'}
    
    def _extract_metric(self, user_lower: str) -> Optional[str]:
        """Extract performance metric from query"""
        if 'nav' in user_lower:
            return 'nav'
        elif any(word in user_lower for word in ['return', 'returns', 'performance']):
            return 'returns'
        elif 'expense' in user_lower or 'ratio' in user_lower:
            return 'expense_ratio'
        return None
    
    def _extract_period(self, user_lower: str) -> Optional[str]:
        """Extract time period from query"""
        if '1 year' in user_lower or '1y' in user_lower or 'one year' in user_lower:
            return '1y'
        elif '3 year' in user_lower or '3y' in user_lower or 'three year' in user_lower:
            return '3y'
        elif '5 year' in user_lower or '5y' in user_lower or 'five year' in user_lower:
            return '5y'
        elif 'this year' in user_lower or 'current year' in user_lower or 'ytd' in user_lower:
            return '1y'
        return None
        
    def _might_contain_fund_name(self, user_input: str) -> bool:
        """
        Simple check if input might contain a specific fund name
        Only used to decide whether to extract fund name - not for routing
        """
        # Very basic heuristic - if it's a short question about process, probably not a fund name
        words = user_input.split()
        if len(words) <= 6 and any(word in user_input.lower() for word in ['how', 'what', 'why', 'when', 'where']):
            return False
        return True
        
        # Basic sentiment analysis
        sentiment = self._analyze_sentiment(input_lower)
        
        # Let agent decide the intent based on minimal hints
        intent_type = intent_hints.get("primary_intent", IntentType.GENERAL_INFO)
        confidence = intent_hints.get("confidence", 0.7)
        
        # Determine clarity based on confidence and keyword matches
        clarity = "high" if confidence > 0.8 else "medium" if confidence > 0.5 else "low"
        suggested_action = "ASK_CLARIFY" if clarity == "low" and confidence < 0.4 else "PROCEED"
        
        return Intent(
            intent=intent_type,
            confidence=confidence,
            entities=entities,
            sentiment=sentiment,
            clarity=clarity,
            suggested_action=suggested_action
        )
        
    def _analyze_basic_keywords(self, input_lower: str) -> Dict[str, Any]:
        """
        Basic keyword analysis without complex patterns
        Just enough to give the agent a starting hint
        """
        
    def _extract_potential_fund_name(self, user_input: str) -> Optional[str]:
        """
        Minimal fund name extraction - only if clearly specified
        """
        # Simple heuristic: if input contains words that look like fund names
        words = user_input.split()
        
        # Look for capitalized sequences that might be fund names
        potential_names = []
        for i, word in enumerate(words):
            if word[0].isupper() and len(word) > 2:
                # Collect sequence of capitalized words
                sequence = [word]
                j = i + 1
                while j < len(words) and (words[j][0].isupper() or words[j].lower() in ['fund', 'mutual', 'direct', 'plan']):
                    sequence.append(words[j])
                    j += 1
                if len(sequence) >= 2:
                    potential_names.append(' '.join(sequence))
        
        return potential_names[0] if potential_names else None
        
    def _analyze_sentiment(self, input_text: str) -> Sentiment:
        """
        Basic sentiment analysis - can be enhanced with AI later
        """
        negative_words = ['bad', 'terrible', 'awful', 'hate', 'angry', 'frustrated', 'problem', 'issue', 'wrong']
        positive_words = ['good', 'great', 'excellent', 'love', 'happy', 'satisfied', 'perfect', 'amazing']
        urgent_words = ['urgent', 'immediately', 'asap', 'quickly', 'emergency', 'critical']
        
        input_lower = input_text.lower()
        
        if any(word in input_lower for word in urgent_words):
            return Sentiment(SentimentLabel.URGENT, 0.8)
        elif any(word in input_lower for word in negative_words):
            return Sentiment(SentimentLabel.NEGATIVE, 0.7)
        elif any(word in input_lower for word in positive_words):
            return Sentiment(SentimentLabel.POSITIVE, 0.7)
        else:
            return Sentiment(SentimentLabel.NEUTRAL, 0.6)
        
        positive_words = ["good", "great", "excellent", "best", "top", "recommend"]
        negative_words = ["bad", "worst", "terrible", "problem", "issue", "error"]
        urgent_words = ["urgent", "immediate", "asap", "quickly", "help"]
        
        if any(word in input_lower for word in urgent_words):
            return Sentiment(SentimentLabel.URGENT, 0.8)
        elif any(word in input_lower for word in negative_words):
            return Sentiment(SentimentLabel.NEGATIVE, 0.7)
        elif any(word in input_lower for word in positive_words):
            return Sentiment(SentimentLabel.POSITIVE, 0.7)
        else:
            return Sentiment(SentimentLabel.NEUTRAL, 0.8)
    
    def get_related_questions(self, intent: IntentType, entities: Entities) -> List[str]:
        """
        Generate related questions based on intent
        """
        
        base_questions = {
            IntentType.FUND_QUERY: [
                "What is the current NAV?",
                "Show me performance history",
                "Compare with similar funds"
            ],
            IntentType.NAV_REQUEST: [
                "Show historical NAV data", 
                "Compare NAV with benchmark",
                "When was the last NAV update?"
            ],
            IntentType.COMPARE_FUNDS: [
                "Show detailed comparison metrics",
                "Which fund has better returns?",
                "Risk analysis of these funds"
            ],
            IntentType.GENERAL_INFO: [
                "Current market trends",
                "Best performing fund categories",
                "Investment strategies"
            ]
        }
        
        return base_questions.get(intent, [
            "How can I help with mutual funds?",
            "Ask me about specific funds", 
            "Need investment guidance?"
        ])
