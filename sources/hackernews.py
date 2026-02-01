"""
Hacker News 新闻源

使用 Hacker News 官方 Firebase API（免费，无需 API Key）
API文档: https://github.com/HackerNews/API
"""

import aiohttp
import asyncio
from datetime import datetime
from typing import List, Optional

from .base import NewsSource, NewsItem, register_source


@register_source
class HackerNewsSource(NewsSource):
    """
    Hacker News 新闻源
    
    从 Hacker News 获取热门技术新闻和讨论
    """
    
    name = "HackerNews"
    description = "Hacker News 热门技术新闻"
    enabled = True
    
    BASE_URL = "https://hacker-news.firebaseio.com/v0"
    
    async def fetch(self, limit: int = 20) -> List[NewsItem]:
        """
        抓取 Hacker News Top Stories
        
        Args:
            limit: 最大抓取数量
            
        Returns:
            NewsItem 列表
        """
        items = []
        
        async with aiohttp.ClientSession() as session:
            # 获取 Top Stories ID 列表
            async with session.get(f"{self.BASE_URL}/topstories.json") as resp:
                if resp.status != 200:
                    return items
                story_ids = await resp.json()
            
            # 限制数量
            story_ids = story_ids[:limit]
            
            # 并发获取每个 story 的详情
            tasks = [self._fetch_story(session, sid) for sid in story_ids]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in results:
                if isinstance(result, NewsItem):
                    items.append(result)
        
        return items
    
    async def _fetch_story(self, session: aiohttp.ClientSession, story_id: int) -> Optional[NewsItem]:
        """获取单个 story 详情"""
        try:
            async with session.get(f"{self.BASE_URL}/item/{story_id}.json") as resp:
                if resp.status != 200:
                    return None
                data = await resp.json()
                
                if not data or data.get("type") != "story":
                    return None
                
                # 转换时间戳
                timestamp = data.get("time", 0)
                published_at = datetime.fromtimestamp(timestamp).isoformat() if timestamp else ""
                
                return NewsItem(
                    title=data.get("title", ""),
                    url=data.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
                    summary=f"Points: {data.get('score', 0)} | Comments: {data.get('descendants', 0)}",
                    source=self.name,
                    published_at=published_at,
                    score=data.get("score", 0),
                    extra={
                        "id": story_id,
                        "by": data.get("by", ""),
                        "comments": data.get("descendants", 0),
                        "hn_url": f"https://news.ycombinator.com/item?id={story_id}"
                    }
                )
        except Exception:
            return None
