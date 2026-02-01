"""
Skills 模块

提供独立的、可复用的技能模块，便于学习和扩展
"""

from .news_fetcher import NewsFetcher
from .ai_analyzer import AIAnalyzer, AnalysisResult
from .report_generator import ReportGenerator
from .email_sender import EmailSender

__all__ = [
    "NewsFetcher",
    "AIAnalyzer",
    "AnalysisResult",
    "ReportGenerator",
    "EmailSender",
]
