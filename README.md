# 🤖 Multi-Agent News Analysis System

A sophisticated multi-agent system built with LangGraph that performs comprehensive news analysis using specialized AI agents. This project showcases advanced AI orchestration, real-time analysis, and professional reporting capabilities.

## 🌟 Features

- **Multi-Agent Architecture**: Specialized agents for different tasks
- **Real-time News Analysis**: Automated article gathering and analysis
- **Sentiment Analysis**: Advanced sentiment and emotion detection
- **Fact Checking**: Credibility assessment and misinformation detection
- **Interactive Dashboard**: Professional Streamlit interface
- **Comprehensive Reports**: Generated in multiple formats
- **Visualizations**: Charts, graphs, and word clouds

## 🏗️ Architecture

### Agents Overview
1. **Supervisor Agent**: Orchestrates the entire workflow
2. **News Researcher Agent**: Searches and gathers news articles
3. **Content Analyzer Agent**: Performs sentiment and thematic analysis
4. **Fact Checker Agent**: Verifies information credibility
5. **Report Generator Agent**: Creates comprehensive reports

### Technology Stack
- **LangGraph**: Multi-agent orchestration
- **LangChain**: LLM integration and tooling
- **Groq**: High-performance LLM inference
- **Streamlit**: Interactive web interface
- **Plotly**: Advanced data visualizations
- **Beautiful Soup**: Web scraping capabilities

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Groq API key
- Tavily API key (optional, for enhanced search)

### Installation

1. Clone the repository:
```bash
git clone <your-repo-url>
cd multi_agent
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. Run the application:
```bash
streamlit run app.py
```

## 📖 Usage

1. **Launch the Application**: Start the Streamlit interface
2. **Enter Topic**: Input your analysis topic in the sidebar
3. **Configure Settings**: Adjust analysis parameters
4. **Start Analysis**: Click "Start Analysis" to begin
5. **View Results**: Explore reports, visualizations, and insights

## 🔧 Configuration

### API Keys Required
- `GROQ_API_KEY`: For LLM inference
- `TAVILY_API_KEY`: For enhanced web search (optional)

### Customization Options
- Maximum articles to analyze
- Enable/disable specific analysis components
- Adjust agent behavior parameters

## 📊 Output Examples

The system generates:
- **Executive Summaries**: Key findings and insights
- **Sentiment Analysis**: Emotional tone assessment
- **Theme Extraction**: Main topics and trends
- **Credibility Scores**: Information reliability assessment
- **Interactive Visualizations**: Charts and graphs
- **Downloadable Reports**: Markdown and PDF formats

## 🛠️ Development

### Project Structure
```
multi_agent/
├── agents/                 # Agent implementations
│   ├── base_agent.py      # Base agent class
│   ├── supervisor.py      # Supervisor agent
│   ├── news_researcher.py # News research agent
│   ├── content_analyzer.py # Content analysis agent
│   ├── fact_checker.py    # Fact checking agent
│   └── report_generator.py # Report generation agent
├── workflow.py            # LangGraph workflow
├── app.py                # Streamlit interface
├── requirements.txt       # Dependencies
└── README.md             # Documentation
```

### Adding New Agents
1. Inherit from `BaseAgent` class
2. Implement the `execute` method
3. Add to workflow in `workflow.py`
4. Update UI in `app.py`

## 🎯 Use Cases

- **Media Monitoring**: Track news sentiment and trends
- **Market Research**: Analyze industry developments
- **Crisis Management**: Monitor public perception
- **Academic Research**: Gather and analyze information
- **Competitive Intelligence**: Track competitor mentions

## 🔍 Technical Highlights

- **Asynchronous Processing**: Efficient multi-agent execution
- **Error Handling**: Robust failure recovery
- **Scalable Architecture**: Easy to extend and modify
- **Professional UI**: Production-ready interface
- **Comprehensive Logging**: Full workflow traceability
