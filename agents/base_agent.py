from abc import ABC, abstractmethod
from typing import Dict, Any, List, TypedDict
from langchain_groq import ChatGroq
from pydantic import BaseModel
import os
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Use TypedDict for LangGraph compatibility
class AgentState(TypedDict):
    messages: List[Dict[str, Any]]
    current_agent: str
    topic: str
    news_articles: List[Dict[str, Any]]
    analysis_results: Dict[str, Any]
    final_report: str
    next_agent: str

class BaseAgent(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        try:
            self.llm = ChatGroq(
                model="gemma2-9b-it",
                temperature=0.1,
                groq_api_key=os.getenv("GROQ_API_KEY")
            )
        except Exception as e:
            print(f"Warning: Could not initialize Groq LLM for {name}: {e}")
            self.llm = None
    
    def execute_with_state_check(self, state: Any) -> AgentState:
        """Execute with proper state structure validation"""
        validated_state = self.ensure_state_structure(state)
        return self.execute(validated_state)
    
    @abstractmethod
    def execute(self, state: AgentState) -> AgentState:
        pass
    
    def format_message(self, content: str, agent_name: str = None) -> Dict[str, Any]:
        return {
            "agent": agent_name or self.name,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
    
    def ensure_state_structure(self, state: Any) -> AgentState:
        """Ensure the state has the correct structure for AgentState"""
        if isinstance(state, dict):
            # Initialize missing keys with default values
            default_state = {
                "messages": [],
                "current_agent": "",
                "topic": "",
                "news_articles": [],
                "analysis_results": {},
                "final_report": "",
                "next_agent": ""
            }
            
            # Update with existing state values
            for key, default_value in default_state.items():
                if key not in state:
                    state[key] = default_value
            
            return state
        else:
            # Handle case where state is not a dict
            return {
                "messages": [],
                "current_agent": "",
                "topic": str(getattr(state, 'topic', '')),
                "news_articles": [],
                "analysis_results": {},
                "final_report": "",
                "next_agent": ""
            }
