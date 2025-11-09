"""
뉴스 수집 모듈: 뉴스 API 또는 RSS 피드에서 암호화폐 뉴스 수집
"""

import requests
import feedparser
from typing import List, Dict
from datetime import datetime
from config import NEWS_API_KEY, RSS_FEED_URLS
import logging

logger = logging.getLogger(__name__)


class NewsScraper:
    """뉴스 수집 클래스"""
    
    def __init__(self, news_api_key: str = None, rss_urls: List[str] = None):
        """
        Args:
            news_api_key: News API 키 (옵션)
            rss_urls: RSS 피드 URL 목록 (옵션)
        """
        self.news_api_key = news_api_key or NEWS_API_KEY
        self.rss_urls = rss_urls or RSS_FEED_URLS
    
    def fetch_news_api(self, query: str = "cryptocurrency", 
                      language: str = "en", max_results: int = 10) -> List[Dict]:
        """
        News API에서 뉴스 가져오기
        
        Args:
            query: 검색 쿼리
            language: 언어 코드
            max_results: 최대 결과 수
            
        Returns:
            뉴스 목록
        """
        if not self.news_api_key:
            logger.warning("News API 키가 설정되지 않았습니다.")
            return []
        
        try:
            url = "https://newsapi.org/v2/everything"
            params = {
                "q": query,
                "language": language,
                "sortBy": "publishedAt",
                "pageSize": max_results,
                "apiKey": self.news_api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            articles = data.get("articles", [])
            
            news_list = []
            for article in articles:
                news_list.append({
                    "title": article.get("title", ""),
                    "description": article.get("description", ""),
                    "url": article.get("url", ""),
                    "published_at": article.get("publishedAt", ""),
                    "source": article.get("source", {}).get("name", "")
                })
            
            logger.info(f"News API에서 {len(news_list)}개의 뉴스를 가져왔습니다.")
            return news_list
            
        except Exception as e:
            logger.error(f"News API 뉴스 수집 실패: {e}")
            return []
    
    def fetch_rss_feeds(self, max_results: int = 10) -> List[Dict]:
        """
        RSS 피드에서 뉴스 가져오기
        
        Args:
            max_results: 최대 결과 수
            
        Returns:
            뉴스 목록
        """
        if not self.rss_urls:
            logger.warning("RSS 피드 URL이 설정되지 않았습니다.")
            return []
        
        news_list = []
        
        for rss_url in self.rss_urls:
            try:
                feed = feedparser.parse(rss_url)
                
                for entry in feed.entries[:max_results]:
                    news_list.append({
                        "title": entry.get("title", ""),
                        "description": entry.get("description", ""),
                        "url": entry.get("link", ""),
                        "published_at": entry.get("published", ""),
                        "source": feed.feed.get("title", "RSS Feed")
                    })
                
                logger.info(f"RSS 피드에서 {len(feed.entries)}개의 뉴스를 가져왔습니다: {rss_url}")
                
            except Exception as e:
                logger.error(f"RSS 피드 수집 실패 ({rss_url}): {e}")
                continue
        
        return news_list
    
    def get_crypto_news(self, method: str = "rss", max_results: int = 10) -> List[Dict]:
        """
        암호화폐 뉴스 가져오기
        
        Args:
            method: 수집 방법 ("rss" 또는 "api")
            max_results: 최대 결과 수
            
        Returns:
            뉴스 목록
        """
        if method == "api":
            return self.fetch_news_api(query="cryptocurrency OR bitcoin OR ethereum", 
                                     max_results=max_results)
        else:
            return self.fetch_rss_feeds(max_results=max_results)
    
    def format_news_for_ai(self, news_list: List[Dict]) -> str:
        """
        AI 분석을 위한 뉴스 포맷팅
        
        Args:
            news_list: 뉴스 목록
            
        Returns:
            포맷팅된 뉴스 텍스트
        """
        if not news_list:
            return "뉴스가 없습니다."
        
        formatted_text = "최근 암호화폐 뉴스:\n\n"
        
        for i, news in enumerate(news_list, 1):
            formatted_text += f"{i}. {news['title']}\n"
            if news.get('description'):
                formatted_text += f"   {news['description'][:200]}...\n"
            formatted_text += f"   출처: {news.get('source', 'Unknown')}\n"
            formatted_text += f"   발행일: {news.get('published_at', 'Unknown')}\n\n"
        
        return formatted_text

