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

# Custom CSS with better colors and visibility
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        background: linear-gradient(90deg, #FF6B6B 0%, #4ECDC4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    
    .agent-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border: none;
    }
    
    .agent-card h4 {
        color: white !important;
        margin-bottom: 1rem;
        font-size: 1.3rem;
    }
    
    .agent-card p {
        color: #f0f0f0 !important;
        font-size: 1rem;
        line-height: 1.5;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(255, 107, 107, 0.3);
        border: none;
    }
    
    .metric-card h3 {
        color: white !important;
        font-size: 2rem;
        margin-bottom: 0.5rem;
    }
    
    .metric-card p {
        color: #f0f0f0 !important;
        font-size: 1rem;
        margin: 0;
    }
    
    .stProgress .st-bo {
        background-color: #FF6B6B;
    }
    
    .article-link {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    
    .article-link:hover {
        background: #e9ecef;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .status-running {
        background: linear-gradient(90deg, #56CCF2, #2F80ED);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        text-align: center;
    }
    
    .status-ready {
        background: linear-gradient(90deg, #56CCF2, #2F80ED);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
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
        st.subheader("⚙️ Analysis Options")
        max_articles = st.slider("Maximum Articles", 3, 15, 8)
        include_sentiment = st.checkbox("Include Sentiment Analysis", True)
        include_factcheck = st.checkbox("Include Fact Checking", True)
        
        # Agent status
        st.subheader("🤖 Agent Status")
        if 'workflow_running' not in st.session_state:
            st.session_state.workflow_running = False
        
        if st.session_state.workflow_running:
            st.markdown('<div class="status-running">🔄 Agents Working...</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="status-ready">✅ Agents Ready</div>', unsafe_allow_html=True)
    
    # Main content
    if not topic:
        st.info("👋 Welcome! Enter a topic in the sidebar to start analysis.")
        
        # Show agent overview with better styling
        st.subheader("🤖 Meet Our AI Agents")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            <div class="agent-card">
                <h4>🔍 News Researcher</h4>
                <p>Searches and gathers relevant news articles from multiple sources using advanced web scraping and APIs. Finds the most current and relevant information.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="agent-card">
                <h4>📊 Content Analyzer</h4>
                <p>Analyzes sentiment, extracts key themes, and identifies important entities in the content. Provides deep insights into the emotional tone and main topics.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="agent-card">
                <h4>✅ Fact Checker</h4>
                <p>Verifies information accuracy and identifies potential misinformation or bias. Ensures the reliability and credibility of news sources.</p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("""
            <div class="agent-card">
                <h4>📝 Report Generator</h4>
                <p>Creates comprehensive reports with insights, visualizations, and recommendations. Synthesizes all analysis into actionable intelligence.</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Add sample topics
        st.subheader("💡 Sample Topics to Try")
        sample_topics = [
            "Artificial Intelligence", "Climate Change", "Cryptocurrency", 
            "Space Exploration", "Renewable Energy", "Global Economy"
        ]
        
        cols = st.columns(3)
        for i, sample_topic in enumerate(sample_topics):
            with cols[i % 3]:
                if st.button(f"🎯 {sample_topic}", key=f"sample_{i}"):
                    st.session_state.sample_topic = sample_topic
                    st.rerun()
        
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
            
            # Simulate workflow steps with progress updates
            steps = [
                ("🤖 Initializing supervisor agent", 10),
                ("🔍 Searching for news articles", 30),
                ("📊 Analyzing content and sentiment", 60),
                ("✅ Fact-checking information", 80),
                ("📝 Generating comprehensive report", 95),
                ("✨ Finalizing results", 100)
            ]
            
            for step_name, progress in steps:
                status_text.markdown(f"**{step_name}...**")
                progress_bar.progress(progress)
                time.sleep(1)
            
            # Run actual workflow
            results = workflow.run(topic)
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        st.session_state.workflow_running = False
        
        # Display results
        display_results(results, topic)
        
    except Exception as e:
        st.session_state.workflow_running = False
        st.error(f"❌ Analysis failed: {str(e)}")
        st.info("💡 Please check your API keys and try again.")

def display_results(results, topic):
    """Display analysis results with enhanced UI"""
    st.success("✅ Analysis Complete!")
    
    # Enhanced metrics overview
    st.subheader("📊 Analysis Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{results.get("articles_found", 0)}</h3>
            <p>Articles Analyzed</p>
        </div>
        """, unsafe_allow_html=True)
    
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
        entities_count = len(analysis_results.get("entities", []))
        st.markdown(f"""
        <div class="metric-card">
            <h3>{entities_count}</h3>
            <p>Entities Found</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Enhanced tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["📋 Report", "📊 Visualizations", "🔗 Articles", "🔍 Detailed Analysis", "⚙️ Workflow Trace"])
    
    with tab1:
        display_report(results)
    
    with tab2:
        display_visualizations(analysis_results)
    
    with tab3:
        display_articles(results)
    
    with tab4:
        display_detailed_analysis(analysis_results)
    
    with tab5:
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

def display_articles(results):
    """Display article links and information"""
    st.subheader("📰 Analyzed Articles")
    
    # Get articles from results
    articles = []
    if 'analysis_results' in results and 'article_analyses' in results['analysis_results']:
        articles = results['analysis_results']['article_analyses']
    
    if not articles:
        st.info("No articles found in the analysis results.")
        return
    
    for i, article in enumerate(articles, 1):
        title = article.get('title', f'Article {i}')
        url = article.get('url', '#')
        sentiment_info = article.get('sentiment', {})
        entities = article.get('entities', [])
        
        # Create expandable article card
        with st.expander(f"📄 Article {i}: {title[:60]}{'...' if len(title) > 60 else ''}"):
            col1, col2 = st.columns([2, 1])
            
            with col1:
                if url and url != '#':
                    st.markdown(f"🔗 **[Read Full Article]({url})**")
                else:
                    st.markdown("🔗 **Link not available**")
                
                st.markdown(f"**Title:** {title}")
                
                # Sentiment information
                sentiment = sentiment_info.get('sentiment', 'Unknown')
                confidence = sentiment_info.get('confidence', 0)
                
                # Color code sentiment
                sentiment_color = {
                    'positive': '🟢',
                    'negative': '🔴', 
                    'neutral': '🟡'
                }.get(sentiment.lower(), '⚪')
                
                st.markdown(f"**Sentiment:** {sentiment_color} {sentiment.title()} (Confidence: {confidence:.2f})")
            
            with col2:
                # Key themes
                themes = sentiment_info.get('key_themes', [])
                if themes:
                    st.markdown("**Key Themes:**")
                    for theme in themes[:3]:
                        st.markdown(f"• {theme}")
                
                # Entities
                if entities:
                    st.markdown("**Entities:**")
                    entity_text = ", ".join(entities[:5])
                    if len(entities) > 5:
                        entity_text += f" and {len(entities) - 5} more..."
                    st.markdown(entity_text)
            
            # Summary
            summary = sentiment_info.get('summary', '')
            if summary:
                st.markdown(f"**Summary:** {summary}")

def display_visualizations(analysis_results):
    """Display enhanced visualizations"""
    if not analysis_results:
        st.info("No analysis data available for visualization.")
        return
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Enhanced sentiment pie chart
        sentiment_data = analysis_results.get("overall_sentiment", {})
        if sentiment_data:
            fig = px.pie(
                values=list(sentiment_data.values()),
                names=list(sentiment_data.keys()),
                title="📊 Sentiment Distribution",
                color_discrete_map={
                    'positive': '#2E8B57',
                    'negative': '#DC143C',
                    'neutral': '#FFD700'
                }
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(
                font=dict(size=14),
                title_font_size=18,
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Enhanced themes bar chart
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
                title="🏷️ Top Themes",
                color='Frequency',
                color_continuous_scale='Viridis'
            )
            fig.update_layout(
                font=dict(size=14),
                title_font_size=18,
                yaxis={'categoryorder': 'total ascending'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Enhanced entities display
    entities = analysis_results.get("entities", [])
    if entities:
        st.subheader("🏷️ Key Entities Found")
        
        # Display entities as colored tags
        entity_html = "<div style='margin: 1rem 0;'>"
        colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD', '#98D8C8', '#F7DC6F']
        
        for i, entity in enumerate(entities[:15]):
            color = colors[i % len(colors)]
            entity_html += f'''
            <span style="
                background-color: {color}; 
                color: white; 
                padding: 0.3rem 0.8rem; 
                margin: 0.2rem; 
                border-radius: 20px; 
                font-size: 0.9rem;
                font-weight: bold;
                display: inline-block;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            ">{entity}</span>
            '''
        
        entity_html += "</div>"
        st.markdown(entity_html, unsafe_allow_html=True)

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
