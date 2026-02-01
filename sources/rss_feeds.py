"""
通用 RSS 新闻源

支持任意 RSS/Atom feed 的抓取，可配置多个源
"""

import aiohttp
import feedparser
from datetime import datetime
from typing import ClassVar, List, Optional

from .base import NewsSource, NewsItem, register_source


class RSSSourceBase(NewsSource):
    """
    RSS 源基类
    
    继承此类可快速创建新的 RSS 源，只需设置 name 和 feed_url
    
    Example:
        @register_source
        class MyRSSSource(RSSSourceBase):
            name = "MySource"
            description = "My RSS feed"
            feed_url = "https://example.com/feed.xml"
    """
    
    feed_url: ClassVar[str] = ""
    
    async def fetch(self, limit: int = 20) -> List[NewsItem]:
        """
        抓取 RSS feed
        
        Args:
            limit: 最大抓取数量
            
        Returns:
            NewsItem 列表
        """
        if not self.feed_url:
            return []
        
        items = []
        
        headers = {
            "User-Agent": "NewsCollector/1.0"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.feed_url, headers=headers, timeout=30) as resp:
                    if resp.status != 200:
                        return items
                    content = await resp.text()
            
            # 使用 feedparser 解析
            feed = feedparser.parse(content)
            
            for entry in feed.entries[:limit]:
                item = self._parse_entry(entry)
                if item:
                    items.append(item)
                    
        except Exception as e:
            print(f"RSS 抓取失败 [{self.name}]: {e}")
        
        return items
    
    def _parse_entry(self, entry) -> Optional[NewsItem]:
        """解析单个 RSS 条目"""
        title = entry.get("title", "").strip()
        if not title:
            return None
        
        # 获取链接
        link = entry.get("link", "")
        
        # 获取摘要
        summary = ""
        if "summary" in entry:
            summary = entry.summary
        elif "description" in entry:
            summary = entry.description
        
        # 清理 HTML 标签（简单处理）
        if summary:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(summary, "lxml")
            summary = soup.get_text(strip=True)[:500]  # 限制长度
        
        # 获取发布时间
        published_at = ""
        if "published_parsed" in entry and entry.published_parsed:
            try:
                published_at = datetime(*entry.published_parsed[:6]).isoformat()
            except Exception:
                pass
        elif "updated_parsed" in entry and entry.updated_parsed:
            try:
                published_at = datetime(*entry.updated_parsed[:6]).isoformat()
            except Exception:
                pass
        
        return NewsItem(
            title=title,
            url=link,
            summary=summary,
            source=self.name,
            published_at=published_at,
            score=0,
            extra={
                "author": entry.get("author", ""),
                "tags": [tag.term for tag in entry.get("tags", [])]
            }
        )


# ========== 预配置的 RSS 源 ==========

@register_source
class TechCrunchSource(RSSSourceBase):
    """TechCrunch 科技资讯"""
    name = "TechCrunch"
    description = "TechCrunch 科技新闻"
    feed_url = "https://techcrunch.com/feed/"
    enabled = True


@register_source
class Kr36Source(RSSSourceBase):
    """36氪创投资讯"""
    name = "36Kr"
    description = "36氪 创投资讯"
    feed_url = "https://36kr.com/feed"
    enabled = True


@register_source
class SSPAISource(RSSSourceBase):
    """少数派"""
    name = "SSPAI"
    description = "少数派 效率工具与科技"
    feed_url = "https://sspai.com/feed"
    enabled = True


@register_source
class V2EXSource(RSSSourceBase):
    """V2EX 技术社区"""
    name = "V2EX"
    description = "V2EX 技术社区热帖"
    feed_url = "https://www.v2ex.com/index.xml"
    enabled = True


@register_source
class HNRSSSource(RSSSourceBase):
    """Hacker News RSS版本"""
    name = "HNRSS"
    description = "Hacker News RSS (备用源)"
    feed_url = "https://hnrss.org/frontpage"
    enabled = False  # 默认禁用，避免与 HackerNews API 源重复
