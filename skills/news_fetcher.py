"""
新闻抓取技能

Skill: 从多个源并发抓取新闻
输入: 源配置、数量限制
输出: List[NewsItem]

学习要点:
1. 异步并发编程 (asyncio)
2. 插件式架构调用
3. 数据聚合与去重
"""

import asyncio
from typing import Optional, List

from sources import NewsItem, get_enabled_sources, get_source


class NewsFetcher:
    """
    新闻抓取器
    
    从配置的新闻源并发抓取新闻，支持：
    - 抓取所有启用的源
    - 抓取指定的单个源
    - 设置每个源的抓取数量限制
    
    Example:
        fetcher = NewsFetcher()
        
        # 抓取所有源
        items = await fetcher.fetch_all(limit=20)
        
        # 抓取单个源
        items = await fetcher.fetch_source("HackerNews", limit=10)
    """
    
    async def fetch_all(self, limit: int = 20) -> List[NewsItem]:
        """
        从所有启用的源抓取新闻
        
        Args:
            limit: 每个源的最大抓取数量
            
        Returns:
            聚合后的 NewsItem 列表
        """
        sources = get_enabled_sources()
        
        if not sources:
            print("警告: 没有启用的新闻源")
            return []
        
        # 创建所有源的实例
        source_instances = [cls() for cls in sources.values()]
        
        # 并发抓取
        tasks = [source.fetch(limit=limit) for source in source_instances]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 聚合结果
        all_items = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                print(f"源 {source_instances[i].name} 抓取失败: {result}")
                continue
            if isinstance(result, list):
                all_items.extend(result)
        
        # 去重（基于URL）
        seen_urls = set()
        unique_items = []
        for item in all_items:
            if item.url and item.url not in seen_urls:
                seen_urls.add(item.url)
                unique_items.append(item)
        
        return unique_items
    
    async def fetch_source(self, source_name: str, limit: int = 20) -> List[NewsItem]:
        """
        从指定源抓取新闻
        
        Args:
            source_name: 源名称
            limit: 最大抓取数量
            
        Returns:
            NewsItem 列表
        """
        source_cls = get_source(source_name)
        
        if not source_cls:
            print(f"错误: 未找到源 '{source_name}'")
            return []
        
        source = source_cls()
        return await source.fetch(limit=limit)
    
    async def fetch_sources(self, source_names: List[str], limit: int = 20) -> List[NewsItem]:
        """
        从指定的多个源抓取新闻
        
        Args:
            source_names: 源名称列表
            limit: 每个源的最大抓取数量
            
        Returns:
            聚合后的 NewsItem 列表
        """
        tasks = [self.fetch_source(name, limit) for name in source_names]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_items = []
        for result in results:
            if isinstance(result, list):
                all_items.extend(result)
        
        # 去重
        seen_urls = set()
        unique_items = []
        for item in all_items:
            if item.url and item.url not in seen_urls:
                seen_urls.add(item.url)
                unique_items.append(item)
        
        return unique_items


# 便捷函数
async def fetch_news(
    source: Optional[str] = None,
    sources: Optional[List[str]] = None,
    limit: int = 20
) -> List[NewsItem]:
    """
    便捷函数：抓取新闻
    
    Args:
        source: 单个源名称（可选）
        sources: 多个源名称（可选）
        limit: 抓取数量限制
        
    Returns:
        NewsItem 列表
    """
    fetcher = NewsFetcher()
    
    if source:
        return await fetcher.fetch_source(source, limit)
    elif sources:
        return await fetcher.fetch_sources(sources, limit)
    else:
        return await fetcher.fetch_all(limit)
