from langgraph.graph import StateGraph, END
from agents.base_agent import AgentState
from agents.supervisor import SupervisorAgent
from agents.news_researcher import NewsResearcherAgent
from agents.content_analyzer import ContentAnalyzerAgent
from agents.fact_checker import FactCheckerAgent
from agents.report_generator import ReportGeneratorAgent
from typing import Dict, Any

class NewsAnalysisWorkflow:
    def __init__(self):
        self.supervisor = SupervisorAgent()
        self.news_researcher = NewsResearcherAgent()
        self.content_analyzer = ContentAnalyzerAgent()
        self.fact_checker = FactCheckerAgent()
        self.report_generator = ReportGeneratorAgent()
        
        self.workflow = self._build_workflow()
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AgentState)
        
        # Add nodes - use regular execute methods instead of execute_with_state_check
        workflow.add_node("supervisor", self.supervisor.execute)
        workflow.add_node("news_researcher", self.news_researcher.execute)
        workflow.add_node("content_analyzer", self.content_analyzer.execute)
        workflow.add_node("fact_checker", self.fact_checker.execute)
        workflow.add_node("report_generator", self.report_generator.execute)
        
        # Add edges
        workflow.set_entry_point("supervisor")
        
        # Conditional routing based on supervisor decisions
        workflow.add_conditional_edges(
            "supervisor",
            self._route_next,
            {
                "NewsResearcher": "news_researcher",
                "ContentAnalyzer": "content_analyzer", 
                "FactChecker": "fact_checker",
                "ReportGenerator": "report_generator",
                "FINISH": END
            }
        )
        
        # All agents return to supervisor
        workflow.add_edge("news_researcher", "supervisor")
        workflow.add_edge("content_analyzer", "supervisor")
        workflow.add_edge("fact_checker", "supervisor")
        workflow.add_edge("report_generator", "supervisor")
        
        return workflow.compile()
    
    def _route_next(self, state: AgentState) -> str:
        """Route to next agent based on supervisor decision"""
        return state.get("next_agent", "FINISH")
    
    def run(self, topic: str) -> Dict[str, Any]:
        """Run the complete workflow"""
        initial_state = {
            "topic": topic,
            "messages": [],
            "news_articles": [],
            "analysis_results": {},
            "final_report": "",
            "current_agent": "",
            "next_agent": ""
        }
        
        try:
            # Simple sequential execution instead of complex workflow
            print(f"Starting analysis for topic: {topic}")
            
            # Step 1: News Research
            print("Step 1: Researching news articles...")
            state = self.news_researcher.execute(initial_state)
            
            # Step 2: Content Analysis (if articles found)
            if state["news_articles"]:
                print("Step 2: Analyzing content...")
                state = self.content_analyzer.execute(state)
            
            # Step 3: Report Generation
            if state["analysis_results"]:
                print("Step 3: Generating report...")
                state = self.report_generator.execute(state)
            
            return {
                "topic": state.get("topic", topic),
                "messages": state.get("messages", []),
                "articles_found": len(state.get("news_articles", [])),
                "analysis_results": state.get("analysis_results", {}),
                "final_report": state.get("final_report", "No report generated"),
                "workflow_trace": [msg.get("content", "") for msg in state.get("messages", [])]
            }
            
        except Exception as e:
            print(f"Workflow execution failed: {e}")
            return {
                "topic": topic,
                "messages": [{"agent": "System", "content": f"Workflow failed: {e}", "timestamp": ""}],
                "articles_found": 0,
                "analysis_results": {},
                "final_report": f"Analysis failed for topic: {topic}. Error: {str(e)}",
                "workflow_trace": [f"Error: {e}"]
            }
