"""
Configuration settings for the Mutual Funds Agent
"""

import os
from dataclasses import dataclass
from typing import List, Dict, Any
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

@dataclass
class AgentConfig:
    """Configuration for the Mutual Funds Agent"""
    
    # API Configurations
    PRODUCTION_API_BASE: str = os.getenv("PRODUCTION_API_BASE", "https://tokenn.in")
    MOONSHOT_API_KEY: str = os.getenv("MOONSHOT_API_KEY", "")
    MOONSHOT_MODEL: str = os.getenv("MOONSHOT_MODEL", "moonshotai/kimi-k2-instruct")
    MOONSHOT_BASE_URL: str = os.getenv("MOONSHOT_BASE_URL", "https://api.groq.com/openai/v1")
    MOONSHOT_TEMPERATURE: float = float(os.getenv("MOONSHOT_TEMPERATURE", "0.0"))
    
    # Tavily API Configuration
    TAVILY_API_KEY: str = os.getenv("TAVILY_API_KEY", "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")
    
    # Request timeouts - Removed for full agentic processing
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "300"))  # 5 minutes for thorough processing  
    WEB_SCRAPE_TIMEOUT: int = int(os.getenv("WEB_SCRAPE_TIMEOUT", "180"))  # 3 minutes for web search
    
    # Agent behavior settings
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.75"))
    MAX_WEB_SOURCES: int = 5
    
    # Intent detection settings
    INTENT_CONFIDENCE_THRESHOLD: float = 0.7
    
    # Database Configuration (Evaluation Pipeline)
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "mf_agent_eval")
    DB_USER: str = os.getenv("DB_USER", "mf_agent")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    
    # Evaluation Settings
    ENABLE_DEEPEVAL: bool = os.getenv("ENABLE_DEEPEVAL", "true").lower() == "true"
    AUTO_EVALUATE: bool = os.getenv("AUTO_EVALUATE", "true").lower() == "true"
    AGENT_VERSION: str = os.getenv("AGENT_VERSION", "1.0.0")
    environment: str = os.getenv("ENVIRONMENT", "development")
    
    def __post_init__(self):
        if not hasattr(self, "PREFERRED_DOMAINS") or self.PREFERRED_DOMAINS is None:
            self.PREFERRED_DOMAINS = [
                "sebi.gov.in", 
                "axismutualfund.com",
                "morningstar.in",
                "valueresearchonline.com"
            ]
    
    @classmethod
    def from_env(cls) -> 'AgentConfig':
        """Create config from environment variables"""
        return cls()

# Default configuration instance
DEFAULT_CONFIG = AgentConfig()
