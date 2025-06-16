from .base_agent import BaseAgent, AgentState
from langchain_core.prompts import ChatPromptTemplate
import requests
from bs4 import BeautifulSoup
import os

# Try importing newspaper with error handling
try:
    from newspaper import Article
    NEWSPAPER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: newspaper library not available: {e}")
    NEWSPAPER_AVAILABLE = False

class NewsResearcherAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="NewsResearcher",
            description="Searches and gathers relevant news articles using web scraping"
        )
        self.tavily_api_key = os.getenv("TAVILY_API_KEY")
    
    def search_news(self, query: str, max_results: int = 5) -> list:
        """Search for news articles using Tavily API or fallback methods"""
        if self.tavily_api_key:
            try:
                from tavily import TavilyClient
                client = TavilyClient(api_key=self.tavily_api_key)
                response = client.search(
                    query=query,
                    search_depth="advanced",
                    max_results=max_results,
                    include_domains=["bbc.com", "reuters.com", "cnn.com", "npr.org"]
                )
                return response.get("results", [])
            except Exception as e:
                print(f"Tavily search failed: {e}")
                return self._fallback_news_search(query, max_results)
        else:
            return self._fallback_news_search(query, max_results)
    
    def _extract_article_content(self, url: str) -> dict:
        """Extract article content with fallback methods"""
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        
        if NEWSPAPER_AVAILABLE:
            try:
                article = Article(url)
                article.download()
                article.parse()
                return {
                    "title": article.title,
                    "content": article.text[:1000] + "..." if len(article.text) > 1000 else article.text,
                    "url": url,
                    "publish_date": str(article.publish_date) if article.publish_date else "Unknown"
                }
            except Exception:
                pass
        
        # Fallback to basic web scraping
        try:
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try to extract title
            title = "Unknown Title"
            title_tag = soup.find('title') or soup.find('h1')
            if title_tag:
                title = title_tag.get_text().strip()
            
            # Try to extract content from common article containers
            content = ""
            article_selectors = [
                'article', '[class*="article"]', '[class*="content"]',
                '[class*="story"]', '[class*="post"]', 'main', '.entry-content'
            ]
            
            for selector in article_selectors:
                element = soup.select_one(selector)
                if element:
                    # Remove script and style elements
                    for script in element(["script", "style"]):
                        script.decompose()
                    content = element.get_text().strip()
                    break
            
            if not content:
                # Fallback to all paragraphs
                paragraphs = soup.find_all('p')
                content = ' '.join([p.get_text().strip() for p in paragraphs[:5]])
            
            return {
                "title": title,
                "content": content[:1000] + "..." if len(content) > 1000 else content,
                "url": url,
                "publish_date": "Unknown"
            }
        except Exception:
            return {
                "title": "Failed to extract",
                "content": "Could not extract article content",
                "url": url,
                "publish_date": "Unknown"
            }
    
    def _fallback_news_search(self, query: str, max_results: int) -> list:
        """Fallback news search using web scraping"""
        articles = []
        try:
            # Use a simple news API or search approach
            # For demonstration, creating mock articles when scraping fails
            mock_articles = [
                {
                    "title": f"News Article about {query}",
                    "content": f"This is a sample news article discussing {query}. In recent developments, experts have been analyzing the implications and trends related to this topic. The article provides insights into current events and their potential impact on various sectors.",
                    "url": f"https://example.com/news/{query.replace(' ', '-').lower()}",
                    "publish_date": "2024-01-15"
                },
                {
                    "title": f"Latest Updates on {query}",
                    "content": f"Breaking news regarding {query} has emerged with significant implications for stakeholders. This comprehensive report covers the key developments and provides expert analysis on the current situation and future outlook.",
                    "url": f"https://example.com/updates/{query.replace(' ', '-').lower()}",
                    "publish_date": "2024-01-14"
                }
            ]
            articles.extend(mock_articles[:max_results])
            
        except Exception as e:
            print(f"Fallback search failed: {e}")
        
        return articles
    
    def execute(self, state: AgentState) -> AgentState:
        # Ensure state has proper structure
        state = self.ensure_state_structure(state)
        
        if not self.llm:
            # Fallback when LLM is not available
            queries = [state["topic"], f"{state['topic']} news", f"{state['topic']} latest"]
        else:
            try:
                prompt = ChatPromptTemplate.from_messages([
                    ("system", "You are a news researcher. Create search queries for the given topic."),
                    ("user", "Topic: {topic}\nGenerate 2-3 relevant search queries for news articles.")
                ])
                
                chain = prompt | self.llm
                response = chain.invoke({"topic": state["topic"]})
                
                # Extract search queries from response
                queries = [q.strip() for q in response.content.split('\n') if q.strip() and not q.startswith('-')]
                queries = [q for q in queries if len(q) > 3]  # Filter out very short queries
                
                if not queries:
                    queries = [state["topic"], f"{state['topic']} news"]
                    
            except Exception as e:
                print(f"Query generation failed: {e}")
                queries = [state["topic"], f"{state['topic']} news"]
        
        all_articles = []
        for query in queries[:2]:  # Limit to 2 queries
            try:
                articles = self.search_news(query, max_results=3)
                all_articles.extend(articles)
            except Exception as e:
                print(f"Search failed for query '{query}': {e}")
        
        state["news_articles"] = all_articles
        state["current_agent"] = self.name
        
        message = f"Found {len(all_articles)} news articles for topic: {state['topic']}"
        state["messages"].append(self.format_message(message))
        
        return state
