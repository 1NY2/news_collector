"""
报告生成技能

Skill: 将分析结果生成精美的 PDF 报告
输入: AnalysisResult + NewsItem 列表
输出: PDF 文件路径

学习要点:
1. Jinja2 模板引擎
2. WeasyPrint HTML 转 PDF (可选)
3. 数据分组与格式化
"""

from datetime import datetime
from pathlib import Path
from collections import defaultdict
from typing import Optional, List

from jinja2 import Environment, FileSystemLoader

import config
from sources import NewsItem
from .ai_analyzer import AnalysisResult

# WeasyPrint 是可选依赖，需要系统级库支持
# 如果不可用，将自动回退到仅生成 HTML
try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except (ImportError, OSError):
    WEASYPRINT_AVAILABLE = False


class ReportGenerator:
    """
    报告生成器
    
    将 AI 分析结果和新闻数据渲染为精美的 PDF 报告
    
    Example:
        generator = ReportGenerator()
        pdf_path = generator.generate(analysis_result, news_items)
        print(f"报告已生成: {pdf_path}")
    """
    
    def __init__(self, template_dir: Optional[Path] = None, output_dir: Optional[Path] = None):
        """
        初始化报告生成器
        
        Args:
            template_dir: 模板目录（默认 templates/）
            output_dir: 输出目录（默认 output/）
        """
        self.template_dir = template_dir or config.BASE_DIR / "templates"
        self.output_dir = output_dir or config.OUTPUT_DIR
        
        # 确保目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # 初始化 Jinja2 环境
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            autoescape=True
        )
    
    @staticmethod
    def is_pdf_available() -> bool:
        """检查 PDF 生成功能是否可用"""
        return WEASYPRINT_AVAILABLE
    
    def generate(
        self,
        analysis: AnalysisResult,
        news_items: List[NewsItem],
        filename: Optional[str] = None
    ) -> Path:
        """
        生成 PDF 报告
        
        如果 WeasyPrint 不可用，将自动回退到生成 HTML
        
        Args:
            analysis: AI 分析结果
            news_items: 新闻列表
            filename: 输出文件名（可选，默认按日期生成）
            
        Returns:
            生成的报告文件路径
        """
        if not WEASYPRINT_AVAILABLE:
            print("警告: WeasyPrint 不可用，将生成 HTML 报告")
            print("提示: 安装 PDF 支持请运行: brew install pango gdk-pixbuf libffi")
            return self.generate_html(analysis, news_items, filename)
        
        # 准备模板数据
        template_data = self._prepare_data(analysis, news_items)
        
        # 渲染 HTML
        html_content = self._render_html(template_data)
        
        # 生成文件名
        if not filename:
            date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"report_{date_str}.pdf"
        
        output_path = self.output_dir / filename
        
        # 生成 PDF
        self._generate_pdf(html_content, output_path)
        
        return output_path
    
    def _prepare_data(
        self,
        analysis: AnalysisResult,
        news_items: List[NewsItem]
    ) -> dict:
        """准备模板数据"""
        # 按来源分组新闻
        news_by_source = defaultdict(list)
        for item in news_items:
            news_by_source[item.source].append(item)
        
        # 排序（按新闻数量降序）
        news_by_source = dict(
            sorted(news_by_source.items(), key=lambda x: len(x[1]), reverse=True)
        )
        
        return {
            "date": datetime.now().strftime("%Y年%m月%d日"),
            "analysis": analysis,
            "news_by_source": news_by_source,
            "total_news": len(news_items),
            "source_count": len(news_by_source)
        }
    
    def _render_html(self, data: dict) -> str:
        """渲染 HTML 模板"""
        template = self.env.get_template("report.html")
        return template.render(**data)
    
    def _generate_pdf(self, html_content: str, output_path: Path) -> None:
        """生成 PDF 文件"""
        if not WEASYPRINT_AVAILABLE:
            raise RuntimeError("WeasyPrint 不可用")
        html = HTML(string=html_content, base_url=str(self.template_dir))
        html.write_pdf(str(output_path))
    
    def generate_html(
        self,
        analysis: AnalysisResult,
        news_items: List[NewsItem],
        filename: Optional[str] = None
    ) -> Path:
        """
        仅生成 HTML 文件（用于预览）
        
        Args:
            analysis: AI 分析结果
            news_items: 新闻列表
            filename: 输出文件名
            
        Returns:
            生成的 HTML 文件路径
        """
        template_data = self._prepare_data(analysis, news_items)
        html_content = self._render_html(template_data)
        
        if not filename:
            date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"report_{date_str}.html"
        elif filename.endswith('.pdf'):
            filename = filename.replace('.pdf', '.html')
        
        output_path = self.output_dir / filename
        output_path.write_text(html_content, encoding="utf-8")
        
        return output_path


# 便捷函数
def generate_report(
    analysis: AnalysisResult,
    news_items: List[NewsItem],
    output_format: str = "pdf"
) -> Path:
    """
    便捷函数：生成报告
    
    Args:
        analysis: 分析结果
        news_items: 新闻列表
        output_format: 输出格式 "pdf" 或 "html"
        
    Returns:
        报告文件路径
    """
    generator = ReportGenerator()
    
    if output_format == "html":
        return generator.generate_html(analysis, news_items)
    else:
        return generator.generate(analysis, news_items)
