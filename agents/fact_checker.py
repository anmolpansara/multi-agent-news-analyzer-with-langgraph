from .base_agent import BaseAgent, AgentState
from langchain_core.prompts import ChatPromptTemplate
import re

class FactCheckerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="FactChecker",
            description="Verifies factual accuracy and identifies potential misinformation"
        )
    
    def check_claims(self, text: str) -> dict:
        """Check factual claims in the text"""
        if not self.llm:
            # Fallback when LLM is not available
            return {
                "credibility_score": 0.7,
                "assessment": "LLM not available for fact checking",
                "red_flags": self._identify_red_flags(text)
            }
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a fact-checker. Analyze the text for:
            1. Factual claims that can be verified
            2. Potential misinformation or bias
            3. Sources credibility
            4. Consistency of information
            
            Return assessment of reliability and any red flags."""),
            ("user", "Text to fact-check: {text}")
        ])
        
        try:
            chain = prompt | self.llm
            response = chain.invoke({"text": text})
            
            # Simple credibility scoring
            credibility_score = 0.7  # Default moderate credibility
            
            content = response.content.lower()
            if any(word in content for word in ["unreliable", "false", "misleading", "biased"]):
                credibility_score = 0.3
            elif any(word in content for word in ["credible", "accurate", "verified", "reliable"]):
                credibility_score = 0.8
            
            return {
                "credibility_score": credibility_score,
                "assessment": response.content,
                "red_flags": self._identify_red_flags(text)
            }
        except Exception as e:
            print(f"Fact checking failed: {e}")
            return {
                "credibility_score": 0.5,
                "assessment": "Fact checking failed",
                "red_flags": self._identify_red_flags(text)
            }
    
    def _identify_red_flags(self, text: str) -> list:
        """Identify potential red flags in the content"""
        red_flags = []
        
        # Check for sensational language
        sensational_words = ["shocking", "unbelievable", "incredible", "amazing", "devastating"]
        if any(word in text.lower() for word in sensational_words):
            red_flags.append("Contains sensational language")
        
        # Check for lack of sources
        if "source" not in text.lower() and "according to" not in text.lower():
            red_flags.append("Limited source attribution")
        
        # Check for absolute statements
        absolute_words = ["always", "never", "all", "none", "everyone", "nobody"]
        if any(word in text.lower() for word in absolute_words):
            red_flags.append("Contains absolute statements")
        
        return red_flags
    
    def execute(self, state: AgentState) -> AgentState:
        # Ensure state has proper structure
        state = self.ensure_state_structure(state)
        
        if not state["news_articles"]:
            state["current_agent"] = self.name
            state["messages"].append(self.format_message("No articles to fact-check"))
            return state
        
        fact_check_results = {
            "overall_credibility": 0.0,
            "article_assessments": [],
            "common_red_flags": {},
            "reliability_summary": ""
        }
        
        total_credibility = 0
        
        for article in state["news_articles"]:
            content = article.get("content", "")
            title = article.get("title", "")
            full_text = f"{title}. {content}"
            
            # Fact-check the article
            fact_check = self.check_claims(full_text)
            
            article_assessment = {
                "title": title,
                "url": article.get("url", ""),
                "credibility_score": fact_check["credibility_score"],
                "assessment": fact_check["assessment"],
                "red_flags": fact_check["red_flags"]
            }
            
            fact_check_results["article_assessments"].append(article_assessment)
            total_credibility += fact_check["credibility_score"]
            
            # Aggregate red flags
            for flag in fact_check["red_flags"]:
                fact_check_results["common_red_flags"][flag] = \
                    fact_check_results["common_red_flags"].get(flag, 0) + 1
        
        # Calculate overall credibility
        if state["news_articles"]:
            fact_check_results["overall_credibility"] = total_credibility / len(state["news_articles"])
        
        # Generate reliability summary
        credibility = fact_check_results["overall_credibility"]
        if credibility >= 0.7:
            reliability_level = "High"
        elif credibility >= 0.5:
            reliability_level = "Moderate"
        else:
            reliability_level = "Low"
        
        common_flags = sorted(fact_check_results["common_red_flags"].items(), 
                            key=lambda x: x[1], reverse=True)[:3]
        
        summary = f"Overall reliability: {reliability_level} (Score: {credibility:.2f}). "
        if common_flags:
            summary += f"Common issues: {', '.join([flag for flag, count in common_flags])}"
        
        fact_check_results["reliability_summary"] = summary
        
        # Add fact-check results to analysis results
        if not state["analysis_results"]:
            state["analysis_results"] = {}
        state["analysis_results"]["fact_check"] = fact_check_results
        
        state["current_agent"] = self.name
        
        message = f"Fact-checking complete: {summary}"
        state["messages"].append(self.format_message(message))
        
        return state
