from .base_agent import BaseAgent, AgentState
from langchain_core.prompts import ChatPromptTemplate
import json
from datetime import datetime

class ReportGeneratorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ReportGenerator",
            description="Generates comprehensive reports from analysis results"
        )
    
    def generate_executive_summary(self, analysis_results: dict, topic: str) -> str:
        """Generate executive summary"""
        if not self.llm:
            # Fallback when LLM is not available
            overall_sentiment = analysis_results.get("overall_sentiment", {})
            fact_check = analysis_results.get("fact_check", {})
            
            summary = f"Executive Summary for {topic}:\n\n"
            summary += f"Analyzed {len(analysis_results.get('article_analyses', []))} articles.\n"
            
            if overall_sentiment:
                dominant = max(overall_sentiment, key=overall_sentiment.get)
                summary += f"Overall sentiment: {dominant}.\n"
            
            if fact_check:
                credibility = fact_check.get("overall_credibility", 0)
                summary += f"Average credibility score: {credibility:.2f}/1.0.\n"
            
            summary += f"Key themes identified: {len(analysis_results.get('key_themes', {}))}\n"
            summary += "This analysis provides insights into current trends and public opinion."
            
            return summary
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """Generate a professional executive summary for a news analysis report.
            Include:
            - Key findings
            - Overall sentiment
            - Main themes
            - Credibility assessment
            - Strategic implications
            
            Keep it concise but comprehensive."""),
            ("user", """Topic: {topic}
            
            Analysis Results: {analysis_results}
            
            Generate executive summary:""")
        ])
        
        try:
            chain = prompt | self.llm
            response = chain.invoke({
                "topic": topic,
                "analysis_results": json.dumps(analysis_results, indent=2)
            })
            return response.content
        except Exception as e:
            print(f"Executive summary generation failed: {e}")
            return f"Executive Summary for {topic}: Analysis completed with limited LLM capabilities."
    
    def generate_detailed_analysis(self, analysis_results: dict) -> str:
        """Generate detailed analysis section"""
        detailed_analysis = "## Detailed Analysis\n\n"
        
        # Sentiment Analysis
        if "overall_sentiment" in analysis_results:
            sentiment_data = analysis_results["overall_sentiment"]
            total = sum(sentiment_data.values())
            if total > 0:
                detailed_analysis += "### Sentiment Distribution\n"
                for sentiment, count in sentiment_data.items():
                    percentage = (count / total) * 100
                    detailed_analysis += f"- {sentiment.capitalize()}: {count} articles ({percentage:.1f}%)\n"
                detailed_analysis += "\n"
        
        # Key Themes
        if "key_themes" in analysis_results:
            detailed_analysis += "### Key Themes\n"
            themes = sorted(analysis_results["key_themes"].items(), 
                          key=lambda x: x[1], reverse=True)
            for theme, count in themes[:8]:
                detailed_analysis += f"- {theme}: mentioned {count} times\n"
            detailed_analysis += "\n"
        
        # Entity Analysis
        if "entities" in analysis_results:
            detailed_analysis += "### Key Entities\n"
            entities = analysis_results["entities"][:10]
            detailed_analysis += f"Identified entities: {', '.join(entities)}\n\n"
        
        # Fact-Check Results
        if "fact_check" in analysis_results:
            fact_check = analysis_results["fact_check"]
            detailed_analysis += "### Credibility Assessment\n"
            detailed_analysis += f"Overall Credibility Score: {fact_check.get('overall_credibility', 0):.2f}/1.0\n"
            detailed_analysis += f"Assessment: {fact_check.get('reliability_summary', 'No assessment available')}\n\n"
            
            if fact_check.get("common_red_flags"):
                detailed_analysis += "#### Common Issues Identified:\n"
                for flag, count in fact_check["common_red_flags"].items():
                    detailed_analysis += f"- {flag}: {count} articles\n"
                detailed_analysis += "\n"
        
        return detailed_analysis
    
    def generate_article_summaries(self, articles: list, analysis_results: dict) -> str:
        """Generate individual article summaries"""
        summaries = "## Article Summaries\n\n"
        
        article_analyses = analysis_results.get("article_analyses", [])
        fact_check_assessments = analysis_results.get("fact_check", {}).get("article_assessments", [])
        
        for i, article in enumerate(articles):
            summaries += f"### Article {i+1}: {article.get('title', 'Untitled')}\n"
            summaries += f"**URL:** {article.get('url', 'N/A')}\n"
            summaries += f"**Published:** {article.get('publish_date', 'Unknown')}\n\n"
            
            # Add sentiment analysis if available
            if i < len(article_analyses):
                analysis = article_analyses[i]
                sentiment_info = analysis.get("sentiment", {})
                summaries += f"**Sentiment:** {sentiment_info.get('sentiment', 'Unknown')} "
                summaries += f"(Confidence: {sentiment_info.get('confidence', 0):.2f})\n"
                
                if sentiment_info.get("key_themes"):
                    summaries += f"**Themes:** {', '.join(sentiment_info['key_themes'][:3])}\n"
            
            # Add credibility assessment if available
            if i < len(fact_check_assessments):
                fact_check = fact_check_assessments[i]
                summaries += f"**Credibility Score:** {fact_check.get('credibility_score', 0):.2f}/1.0\n"
                
                if fact_check.get("red_flags"):
                    summaries += f"**Issues:** {', '.join(fact_check['red_flags'][:2])}\n"
            
            # Add content preview
            content = article.get("content", "")
            preview = content[:200] + "..." if len(content) > 200 else content
            summaries += f"**Preview:** {preview}\n\n"
            summaries += "---\n\n"
        
        return summaries
    
    def execute(self, state: AgentState) -> AgentState:
        # Ensure state has proper structure
        state = self.ensure_state_structure(state)
        
        if not state["analysis_results"] or not state["news_articles"]:
            state["current_agent"] = self.name
            state["messages"].append(self.format_message("Insufficient data for report generation"))
            return state
        
        # Generate report sections
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        report = f"# News Analysis Report: {state['topic']}\n\n"
        report += f"**Generated:** {timestamp}\n"
        report += f"**Articles Analyzed:** {len(state['news_articles'])}\n\n"
        
        # Executive Summary
        exec_summary = self.generate_executive_summary(state["analysis_results"], state["topic"])
        report += "## Executive Summary\n\n"
        report += exec_summary + "\n\n"
        
        # Key Findings
        report += "## Key Findings\n\n"
        analysis_results = state["analysis_results"]
        
        # Sentiment summary
        overall_sentiment = analysis_results.get("overall_sentiment", {})
        if overall_sentiment:
            total = sum(overall_sentiment.values())
            if total > 0:
                report += "### Sentiment Analysis\n"
                for sentiment, count in overall_sentiment.items():
                    percentage = (count / total) * 100
                    report += f"- {sentiment.capitalize()}: {count} articles ({percentage:.1f}%)\n"
                report += "\n"
        
        # Top themes
        themes = analysis_results.get("key_themes", {})
        if themes:
            report += "### Top Themes\n"
            sorted_themes = sorted(themes.items(), key=lambda x: x[1], reverse=True)[:5]
            for theme, count in sorted_themes:
                report += f"- {theme}: {count} mentions\n"
            report += "\n"
        
        # Credibility assessment
        fact_check = analysis_results.get("fact_check", {})
        if fact_check:
            report += "### Credibility Assessment\n"
            credibility = fact_check.get("overall_credibility", 0)
            reliability_summary = fact_check.get("reliability_summary", "No assessment available")
            report += f"- Overall credibility score: {credibility:.2f}/1.0\n"
            report += f"- Assessment: {reliability_summary}\n\n"
        
        # Summary insights
        summary_insights = analysis_results.get("summary_insights", "")
        if summary_insights:
            report += "### Summary Insights\n"
            report += summary_insights + "\n\n"
        
        # Methodology
        report += "## Methodology\n\n"
        report += "This report was generated using a multi-agent AI system that:\n"
        report += "1. Searched for relevant news articles\n"
        report += "2. Analyzed content for sentiment, themes, and entities\n"
        report += "3. Performed fact-checking and credibility assessment\n"
        report += "4. Generated comprehensive analysis and insights\n\n"
        
        report += "**Disclaimer:** This analysis is generated by AI and should be verified with additional sources.\n"
        
        state["final_report"] = report
        state["current_agent"] = self.name
        
        message = f"Comprehensive report generated for topic: {state['topic']}"
        state["messages"].append(self.format_message(message))
        
        return state
