"""
新闻源基类与注册机制

这是新闻收集系统的核心架构，采用插件式设计：
- NewsItem: 统一的新闻条目数据结构
- NewsSource: 所有新闻源必须继承的抽象基类
- register_source: 装饰器，用于自动注册新闻源

添加新源只需3步：
1. 创建新文件，继承 NewsSource
2. 使用 @register_source 装饰器
3. 实现 fetch() 方法
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Dict, Type, List, Optional
from datetime import datetime


@dataclass
class NewsItem:
    """
    统一的新闻条目结构
    
    所有新闻源抓取的数据都应转换为此格式，便于后续处理
    
    Attributes:
        title: 新闻标题
        url: 原文链接
        summary: 摘要/描述（可选）
        source: 来源名称
        published_at: 发布时间（ISO格式字符串）
        score: 热度分数（可选，用于排序）
        extra: 额外信息（可选，存储源特有的数据）
    """
    title: str
    url: str
    summary: str = ""
    source: str = ""
    published_at: str = ""
    score: int = 0
    extra: dict = field(default_factory=dict)
    
    def __post_init__(self):
        """数据清洗"""
        self.title = self.title.strip() if self.title else ""
        self.summary = self.summary.strip() if self.summary else ""
        
    def to_dict(self) -> dict:
        """转换为字典格式"""
        return {
            "title": self.title,
            "url": self.url,
            "summary": self.summary,
            "source": self.source,
            "published_at": self.published_at,
            "score": self.score,
            "extra": self.extra
        }


class NewsSource(ABC):
    """
    新闻源抽象基类
    
    所有新闻源都必须继承此类并实现 fetch() 方法
    
    Class Attributes:
        name: 源名称（用于显示和配置）
        description: 源描述
        enabled: 是否启用
        
    Example:
        @register_source
        class MySource(NewsSource):
            name = "MySource"
            description = "My custom news source"
            enabled = True
            
            async def fetch(self, limit: int = 20) -> list[NewsItem]:
                # 实现抓取逻辑
                return items
    """
    
    name: str = "Unknown"
    description: str = ""
    enabled: bool = True
    
    @abstractmethod
    async def fetch(self, limit: int = 20) -> List[NewsItem]:
        """
        抓取新闻
        
        Args:
            limit: 最大抓取数量
            
        Returns:
            NewsItem列表
        """
        pass
    
    def __repr__(self) -> str:
        status = "✓" if self.enabled else "✗"
        return f"<{self.name} [{status}]>"


# ========== 源注册机制 ==========

# 全局注册表
_registry: Dict[str, Type[NewsSource]] = {}


def register_source(cls: Type[NewsSource]) -> Type[NewsSource]:
    """
    装饰器：注册新闻源到全局注册表
    
    使用此装饰器后，源会被自动发现和使用
    
    Example:
        @register_source
        class HackerNewsSource(NewsSource):
            name = "HackerNews"
            ...
    """
    if not issubclass(cls, NewsSource):
        raise TypeError(f"{cls.__name__} 必须继承 NewsSource")
    
    _registry[cls.name] = cls
    return cls


def get_all_sources() -> Dict[str, Type[NewsSource]]:
    """获取所有已注册的新闻源类"""
    return _registry.copy()


def get_enabled_sources() -> Dict[str, Type[NewsSource]]:
    """获取所有已启用的新闻源类"""
    return {name: cls for name, cls in _registry.items() if cls.enabled}


def get_source(name: str) -> Optional[Type[NewsSource]]:
    """根据名称获取新闻源类"""
    return _registry.get(name)


def list_sources() -> List[dict]:
    """列出所有源的信息"""
    return [
        {
            "name": cls.name,
            "description": cls.description,
            "enabled": cls.enabled
        }
        for cls in _registry.values()
    ]
