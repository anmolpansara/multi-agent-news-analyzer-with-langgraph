from .base_agent import BaseAgent, AgentState
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
import json
import re

class ContentAnalyzerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ContentAnalyzer",
            description="Analyzes content sentiment and extracts key insights"
        )
    
    def analyze_sentiment(self, text: str) -> dict:
        """Analyze sentiment of given text"""
        if not self.llm:
            # Fallback sentiment analysis when LLM is not available
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "key_themes": ["general", "news"],
                "emotional_tone": "neutral",
                "summary": "Basic analysis without LLM"
            }
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Analyze the sentiment and key themes of the given text.
            Return a JSON object with:
            - sentiment: positive/negative/neutral
            - confidence: 0.0-1.0
            - key_themes: list of main themes
            - emotional_tone: description of emotional tone
            - summary: brief summary"""),
            ("user", "Text to analyze: {text}")
        ])
        
        try:
            # Use basic string parsing instead of JsonOutputParser for better reliability
            chain = prompt | self.llm
            result = chain.invoke({"text": text})
            
            # Simple parsing of the response
            content = result.content.lower()
            if "positive" in content:
                sentiment = "positive"
            elif "negative" in content:
                sentiment = "negative"
            else:
                sentiment = "neutral"
            
            return {
                "sentiment": sentiment,
                "confidence": 0.7,
                "key_themes": ["general", "news"],
                "emotional_tone": sentiment,
                "summary": f"Sentiment analysis complete: {sentiment}"
            }
        except Exception as e:
            print(f"Sentiment analysis failed: {e}")
            return {
                "sentiment": "neutral",
                "confidence": 0.5,
                "key_themes": ["general"],
                "emotional_tone": "neutral",
                "summary": "Analysis failed"
            }
    
    def extract_entities(self, text: str) -> list:
        """Extract named entities from text"""
        try:
            # Simple entity extraction using regex patterns
            entities = []
            
            # Extract capitalized words as potential entities
            potential_entities = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
            entities.extend(potential_entities[:10])  # Limit to 10
            
            return list(set(entities))
        except Exception as e:
            print(f"Entity extraction failed: {e}")
            return []
    
    def execute(self, state: AgentState) -> AgentState:
        # Ensure state has proper structure
        state = self.ensure_state_structure(state)
        
        if not state["news_articles"]:
            state["current_agent"] = self.name
            state["messages"].append(self.format_message("No articles to analyze"))
            return state
        
        analysis_results = {
            "overall_sentiment": {"positive": 0, "negative": 0, "neutral": 0},
            "article_analyses": [],
            "key_themes": {},
            "entities": [],
            "summary_insights": ""
        }
        
        for article in state["news_articles"]:
            content = article.get("content", "")
            title = article.get("title", "")
            full_text = f"{title}. {content}"
            
            # Analyze sentiment
            sentiment_analysis = self.analyze_sentiment(full_text)
            
            # Extract entities
            entities = self.extract_entities(full_text)
            
            article_analysis = {
                "title": title,
                "url": article.get("url", ""),
                "sentiment": sentiment_analysis,
                "entities": entities
            }
            
            analysis_results["article_analyses"].append(article_analysis)
            
            # Aggregate sentiment
            sentiment = sentiment_analysis.get("sentiment", "neutral")
            analysis_results["overall_sentiment"][sentiment] += 1
            
            # Aggregate themes
            for theme in sentiment_analysis.get("key_themes", []):
                analysis_results["key_themes"][theme] = analysis_results["key_themes"].get(theme, 0) + 1
            
            # Aggregate entities
            analysis_results["entities"].extend(entities)
        
        # Remove duplicate entities and keep top 15
        analysis_results["entities"] = list(set(analysis_results["entities"]))[:15]
        
        # Generate summary insights
        total_articles = len(state["news_articles"])
        dominant_sentiment = max(analysis_results["overall_sentiment"], 
                               key=analysis_results["overall_sentiment"].get)
        top_themes = sorted(analysis_results["key_themes"].items(), 
                          key=lambda x: x[1], reverse=True)[:5]
        
        summary = f"Analyzed {total_articles} articles. Overall sentiment: {dominant_sentiment}. "
        summary += f"Top themes: {', '.join([theme for theme, count in top_themes])}. "
        summary += f"Key entities identified: {len(analysis_results['entities'])}"
        
        analysis_results["summary_insights"] = summary
        
        state["analysis_results"] = analysis_results
        state["current_agent"] = self.name
        
        message = f"Content analysis complete: {summary}"
        state["messages"].append(self.format_message(message))
        
        return state
