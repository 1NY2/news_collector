"""
GitHub Trending 新闻源

爬取 GitHub Trending 页面获取热门开源项目（免费）
"""

import aiohttp
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Optional

from .base import NewsSource, NewsItem, register_source


@register_source
class GitHubTrendingSource(NewsSource):
    """
    GitHub Trending 新闻源
    
    获取 GitHub 上的热门开源项目
    """
    
    name = "GitHubTrending"
    description = "GitHub 热门开源项目"
    enabled = True
    
    BASE_URL = "https://github.com/trending"
    
    async def fetch(self, limit: int = 20) -> List[NewsItem]:
        """
        抓取 GitHub Trending 项目
        
        Args:
            limit: 最大抓取数量
            
        Returns:
            NewsItem 列表
        """
        items = []
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
        }
        
        async with aiohttp.ClientSession() as session:
            # 获取今日趋势
            async with session.get(self.BASE_URL, headers=headers) as resp:
                if resp.status != 200:
                    return items
                html = await resp.text()
            
            items = self._parse_trending_page(html, limit)
        
        return items
    
    def _parse_trending_page(self, html: str, limit: int) -> List[NewsItem]:
        """解析 Trending 页面 HTML"""
        items = []
        soup = BeautifulSoup(html, "lxml")
        
        # 查找所有仓库条目
        articles = soup.select("article.Box-row")
        
        for article in articles[:limit]:
            try:
                item = self._parse_repo_article(article)
                if item:
                    items.append(item)
            except Exception:
                continue
        
        return items
    
    def _parse_repo_article(self, article) -> Optional[NewsItem]:
        """解析单个仓库条目"""
        # 仓库名称和链接
        h2 = article.select_one("h2 a")
        if not h2:
            return None
        
        repo_path = h2.get("href", "").strip("/")
        if not repo_path:
            return None
        
        repo_url = f"https://github.com/{repo_path}"
        repo_name = repo_path.replace("/", " / ")
        
        # 描述
        desc_elem = article.select_one("p")
        description = desc_elem.get_text(strip=True) if desc_elem else ""
        
        # 语言
        lang_elem = article.select_one("[itemprop='programmingLanguage']")
        language = lang_elem.get_text(strip=True) if lang_elem else ""
        
        # 星标数
        stars_elem = article.select_one("a[href$='/stargazers']")
        stars = stars_elem.get_text(strip=True).replace(",", "") if stars_elem else "0"
        try:
            stars_count = int(stars)
        except ValueError:
            stars_count = 0
        
        # 今日星标
        today_stars_elem = article.select_one("span.d-inline-block.float-sm-right")
        today_stars = today_stars_elem.get_text(strip=True) if today_stars_elem else ""
        
        # 构建摘要
        summary_parts = []
        if language:
            summary_parts.append(f"Language: {language}")
        summary_parts.append(f"Stars: {stars}")
        if today_stars:
            summary_parts.append(f"({today_stars})")
        if description:
            summary_parts.append(f"- {description}")
        
        return NewsItem(
            title=repo_name,
            url=repo_url,
            summary=" ".join(summary_parts),
            source=self.name,
            published_at=datetime.now().isoformat(),
            score=stars_count,
            extra={
                "language": language,
                "stars": stars_count,
                "today_stars": today_stars,
                "description": description
            }
        )
