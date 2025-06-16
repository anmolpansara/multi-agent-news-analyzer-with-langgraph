from .base_agent import BaseAgent, AgentState
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

class SupervisorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="Supervisor",
            description="Orchestrates the multi-agent workflow for news analysis"
        )
        self.agents = ["NewsResearcher", "ContentAnalyzer", "FactChecker", "ReportGenerator"]
    
    def execute(self, state: AgentState) -> AgentState:
        # Ensure state has proper structure
        state = self.ensure_state_structure(state)
        
        articles_count = len(state["news_articles"])
        analysis_done = bool(state["analysis_results"])
        report_done = bool(state["final_report"])
        
        if not self.llm:
            # Simple fallback logic when LLM is not available
            if articles_count == 0:
                next_agent = "NewsResearcher"
            elif not analysis_done:
                next_agent = "ContentAnalyzer"
            elif not report_done:
                next_agent = "ReportGenerator"
            else:
                next_agent = "FINISH"
        else:
            try:
                prompt = ChatPromptTemplate.from_messages([
                    ("system", """You are a supervisor managing a team of AI agents for news analysis.
                    
                    Available agents:
                    - NewsResearcher: Searches and gathers relevant news articles
                    - ContentAnalyzer: Analyzes sentiment and extracts insights
                    - FactChecker: Verifies information accuracy
                    - ReportGenerator: Creates comprehensive reports
                    
                    Current state:
                    - Topic: {topic}
                    - Articles found: {articles_count}
                    - Analysis completed: {analysis_done}
                    - Report generated: {report_done}
                    
                    Determine the next agent to execute or 'FINISH' if complete.
                    Return only the agent name or 'FINISH'."""),
                    ("user", "What should be the next step?")
                ])
                
                chain = prompt | self.llm | StrOutputParser()
                next_agent = chain.invoke({
                    "topic": state["topic"],
                    "articles_count": articles_count,
                    "analysis_done": analysis_done,
                    "report_done": report_done
                })
            except Exception as e:
                print(f"Supervisor decision failed: {e}")
                # Fallback logic
                if articles_count == 0:
                    next_agent = "NewsResearcher"
                elif not analysis_done:
                    next_agent = "ContentAnalyzer"
                elif not report_done:
                    next_agent = "ReportGenerator"
                else:
                    next_agent = "FINISH"
        
        state["current_agent"] = self.name
        state["next_agent"] = next_agent.strip()
        
        message = f"Supervisor decided next agent: {state['next_agent']}"
        state["messages"].append(self.format_message(message))
        
        return state
