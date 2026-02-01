"""
新闻源模块

自动发现并导入所有新闻源，实现插件式架构
"""

import importlib
import pkgutil
from pathlib import Path

from .base import (
    NewsItem,
    NewsSource,
    register_source,
    get_all_sources,
    get_enabled_sources,
    get_source,
    list_sources,
)

# 导出公共接口
__all__ = [
    "NewsItem",
    "NewsSource",
    "register_source",
    "get_all_sources",
    "get_enabled_sources",
    "get_source",
    "list_sources",
]


def _auto_discover_sources():
    """
    自动发现并导入当前包下的所有源模块
    
    这样新添加的源文件会被自动加载，无需手动导入
    """
    package_dir = Path(__file__).parent
    
    for module_info in pkgutil.iter_modules([str(package_dir)]):
        if module_info.name.startswith("_"):
            continue
        if module_info.name == "base":
            continue
            
        try:
            importlib.import_module(f".{module_info.name}", package=__name__)
        except ImportError as e:
            print(f"警告: 无法加载源模块 {module_info.name}: {e}")


# 自动发现所有源
_auto_discover_sources()
