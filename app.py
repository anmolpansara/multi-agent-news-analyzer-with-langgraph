import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from workflow import NewsAnalysisWorkflow
import pandas as pd
import json
from datetime import datetime
import time

# Page config
st.set_page_config(
    page_title="Multi-Agent News Analysis System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .agent-card {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">🤖 Multi-Agent News Analysis System</h1>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🎯 Analysis Configuration")
        
        # Topic input
        topic = st.text_input(
            "Enter Analysis Topic",
            placeholder="e.g., Climate Change, AI Technology, Global Economy",
            help="Enter the topic you want to analyze"
        )
        
        # Analysis options
        st.subheader("Analysis Options")
        max_articles = st.slider("Maximum Articles", 3, 15, 8)
        include_sentiment = st.checkbox("Include Sentiment Analysis", True)
        include_factcheck = st.checkbox("Include Fact Checking", True)
        
        # Agent status
        st.subheader("🤖 Agent Status")
        if 'workflow_running' not in st.session_state:
            st.session_state.workflow_running = False
        
        if st.session_state.workflow_running:
            st.info("Agents are working...")
        else:
            st.success("Agents ready")
    
    # Main content
    if not topic:
        st.info("👋 Welcome! Enter a topic in the sidebar to start analysis.")
        
        # Show agent overview
        st.subheader("🤖 Meet Our AI Agents")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="agent-card">
                <h4>🔍 News Researcher</h4>
                <p>Searches and gathers relevant news articles from multiple sources using web scraping and APIs.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="agent-card">
                <h4>📊 Content Analyzer</h4>
                <p>Analyzes sentiment, extracts key themes, and identifies important entities in the content.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="agent-card">
                <h4>✅ Fact Checker</h4>
                <p>Verifies information accuracy and identifies potential misinformation or bias.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="agent-card">
                <h4>📝 Report Generator</h4>
                <p>Creates comprehensive reports with insights, visualizations, and recommendations.</p>
            </div>
            """, unsafe_allow_html=True)
        
        return
    
    # Analysis button
    if st.button("🚀 Start Analysis", type="primary", use_container_width=True):
        run_analysis(topic, max_articles, include_sentiment, include_factcheck)

def run_analysis(topic, max_articles, include_sentiment, include_factcheck):
    """Run the multi-agent analysis"""
    st.session_state.workflow_running = True
    
    # Progress tracking
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Initialize workflow
        workflow = NewsAnalysisWorkflow()
        
        # Create container for real-time updates
        update_container = st.container()
        
        with update_container:
            st.subheader(f"🔄 Analyzing: {topic}")
            
            # Agent activity log
            activity_log = st.empty()
            
            # Simulate workflow steps with progress updates
            steps = [
                ("Initializing supervisor agent", 10),
                ("Searching for news articles", 30),
                ("Analyzing content and sentiment", 60),
                ("Fact-checking information", 80),
                ("Generating comprehensive report", 95),
                ("Finalizing results", 100)
            ]
            
            for step_name, progress in steps:
                status_text.text(f"🤖 {step_name}...")
                progress_bar.progress(progress)
                time.sleep(1)  # Simulate processing time
            
            # Run actual workflow
            results = workflow.run(topic)
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        activity_log.empty()
        
        st.session_state.workflow_running = False
        
        # Display results
        display_results(results, topic)
        
    except Exception as e:
        st.session_state.workflow_running = False
        st.error(f"Analysis failed: {str(e)}")
        st.info("Please check your API keys and try again.")

def display_results(results, topic):
    """Display analysis results"""
    st.success("✅ Analysis Complete!")
    
    # Metrics overview
    st.subheader("📊 Analysis Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>{}</h3>
            <p>Articles Analyzed</p>
        </div>
        """.format(results.get("articles_found", 0)), unsafe_allow_html=True)
    
    analysis_results = results.get("analysis_results", {})
    
    with col2:
        sentiment_data = analysis_results.get("overall_sentiment", {})
        dominant_sentiment = max(sentiment_data, key=sentiment_data.get) if sentiment_data else "Unknown"
        st.markdown(f"""
        <div class="metric-card">
            <h3>{dominant_sentiment.title()}</h3>
            <p>Dominant Sentiment</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        themes_count = len(analysis_results.get("key_themes", {}))
        st.markdown(f"""
        <div class="metric-card">
            <h3>{themes_count}</h3>
            <p>Key Themes</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        fact_check = analysis_results.get("fact_check", {})
        credibility = fact_check.get("overall_credibility", 0)
        st.markdown(f"""
        <div class="metric-card">
            <h3>{credibility:.2f}</h3>
            <p>Credibility Score</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Report", "📊 Visualizations", "🔍 Detailed Analysis", "⚙️ Workflow Trace"])
    
    with tab1:
        display_report(results)
    
    with tab2:
        display_visualizations(analysis_results)
    
    with tab3:
        display_detailed_analysis(analysis_results)
    
    with tab4:
        display_workflow_trace(results)

def display_report(results):
    """Display the final report"""
    report = results.get("final_report", "No report generated")
    
    # Download button
    st.download_button(
        label="📥 Download Report",
        data=report,
        file_name=f"news_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
        mime="text/markdown"
    )
    
    # Display report
    st.markdown(report)

def display_visualizations(analysis_results):
    """Display visualizations"""
    col1, col2 = st.columns(2)
    
    with col1:
        # Sentiment pie chart
        sentiment_data = analysis_results.get("overall_sentiment", {})
        if sentiment_data:
            fig = px.pie(
                values=list(sentiment_data.values()),
                names=list(sentiment_data.keys()),
                title="Sentiment Distribution",
                color_discrete_map={
                    'positive': '#28a745',
                    'negative': '#dc3545',
                    'neutral': '#6c757d'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Themes bar chart
        themes_data = analysis_results.get("key_themes", {})
        if themes_data:
            themes_df = pd.DataFrame(
                list(themes_data.items())[:8],
                columns=['Theme', 'Frequency']
            )
            fig = px.bar(
                themes_df,
                x='Frequency',
                y='Theme',
                orientation='h',
                title="Top Themes",
                color='Frequency',
                color_continuous_scale='viridis'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Word cloud
    if themes_data:
        st.subheader("☁️ Themes Word Cloud")
        wordcloud = WordCloud(
            width=800,
            height=400,
            background_color='white',
            colormap='viridis'
        ).generate_from_frequencies(themes_data)
        
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.imshow(wordcloud, interpolation='bilinear')
        ax.axis('off')
        st.pyplot(fig)
    
    # Credibility assessment
    fact_check = analysis_results.get("fact_check", {})
    if fact_check:
        st.subheader("🎯 Credibility Assessment")
        
        assessments = fact_check.get("article_assessments", [])
        if assessments:
            credibility_scores = [a.get("credibility_score", 0) for a in assessments]
            titles = [a.get("title", f"Article {i+1}")[:30] + "..." 
                     for i, a in enumerate(assessments)]
            
            fig = px.bar(
                x=credibility_scores,
                y=titles,
                orientation='h',
                title="Article Credibility Scores",
                color=credibility_scores,
                color_continuous_scale='RdYlGn',
                range_color=[0, 1]
            )
            st.plotly_chart(fig, use_container_width=True)

def display_detailed_analysis(analysis_results):
    """Display detailed analysis"""
    # Entity analysis
    entities = analysis_results.get("entities", [])
    if entities:
        st.subheader("🏷️ Key Entities Identified")
        
        # Display entities as tags
        entity_html = ""
        for entity in entities[:15]:
            entity_html += f'<span style="background-color: #e1f5fe; padding: 0.2rem 0.5rem; margin: 0.2rem; border-radius: 15px; font-size: 0.8rem;">{entity}</span>'
        
        st.markdown(entity_html, unsafe_allow_html=True)
    
    # Article-level analysis
    article_analyses = analysis_results.get("article_analyses", [])
    if article_analyses:
        st.subheader("📄 Article-Level Analysis")
        
        for i, analysis in enumerate(article_analyses[:5]):  # Show top 5
            with st.expander(f"Article {i+1}: {analysis.get('title', 'Untitled')[:50]}..."):
                sentiment = analysis.get("sentiment", {})
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write("**Sentiment:**", sentiment.get("sentiment", "Unknown"))
                    st.write("**Confidence:**", f"{sentiment.get('confidence', 0):.2f}")
                    
                with col2:
                    themes = sentiment.get("key_themes", [])
                    if themes:
                        st.write("**Key Themes:**", ", ".join(themes[:3]))
                
                entities = analysis.get("entities", [])
                if entities:
                    st.write("**Entities:**", ", ".join(entities[:5]))
    
    # Summary insights
    summary = analysis_results.get("summary_insights", "")
    if summary:
        st.subheader("💡 Summary Insights")
        st.info(summary)

def display_workflow_trace(results):
    """Display workflow execution trace"""
    st.subheader("🔄 Agent Workflow Trace")
    
    workflow_trace = results.get("workflow_trace", [])
    
    for i, step in enumerate(workflow_trace):
        st.write(f"**Step {i+1}:** {step}")
    
    # Agent messages
    messages = results.get("messages", [])
    if messages:
        st.subheader("💬 Agent Communications")
        
        for msg in messages:
            agent = msg.get("agent", "Unknown")
            content = msg.get("content", "")
            timestamp = msg.get("timestamp", "")
            
            st.write(f"**{agent}** ({timestamp}): {content}")

if __name__ == "__main__":
    main()
