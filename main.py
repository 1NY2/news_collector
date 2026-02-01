#!/usr/bin/env python3
"""
News Collector - 新闻收集小助手

一个面向独立开发者的信息收集工具，自动爬取科技新闻，
通过 AI 分析生成项目建议，输出精美 PDF 报告。

使用方法:
    python main.py --help          # 查看帮助
    python main.py sources         # 列出所有新闻源
    python main.py fetch           # 抓取新闻
    python main.py run             # 完整流程
    python main.py run --send-email # 完整流程并发送邮件
"""

import asyncio
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel

# 导入模块
import config
from sources import list_sources, get_all_sources, NewsItem
from skills.news_fetcher import NewsFetcher
from skills.ai_analyzer import AIAnalyzer, AnalysisResult
from skills.report_generator import ReportGenerator
from skills.email_sender import EmailSender

# 创建 CLI 应用
app = typer.Typer(
    name="news-collector",
    help="📰 新闻收集小助手 - 独立开发者的信息情报工具",
    add_completion=False
)

console = Console()


@app.command()
def sources():
    """
    列出所有可用的新闻源
    """
    all_sources = list_sources()
    
    table = Table(title="📡 可用新闻源")
    table.add_column("名称", style="cyan")
    table.add_column("描述", style="white")
    table.add_column("状态", style="green")
    
    for source in all_sources:
        status = "✓ 启用" if source["enabled"] else "✗ 禁用"
        status_style = "green" if source["enabled"] else "red"
        table.add_row(
            source["name"],
            source["description"],
            f"[{status_style}]{status}[/{status_style}]"
        )
    
    console.print(table)
    console.print(f"\n共 {len(all_sources)} 个新闻源")


@app.command()
def fetch(
    source: Optional[str] = typer.Option(None, "--source", "-s", help="指定单个源"),
    limit: int = typer.Option(20, "--limit", "-l", help="每个源的抓取数量"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="输出到JSON文件")
):
    """
    抓取新闻
    """
    async def _fetch():
        fetcher = NewsFetcher()
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            if source:
                progress.add_task(f"正在从 {source} 抓取新闻...", total=None)
                items = await fetcher.fetch_source(source, limit=limit)
            else:
                progress.add_task("正在从所有源抓取新闻...", total=None)
                items = await fetcher.fetch_all(limit=limit)
        
        return items
    
    items = asyncio.run(_fetch())
    
    # 显示结果
    console.print(f"\n✅ 共抓取 [bold green]{len(items)}[/bold green] 条新闻\n")
    
    # 按源统计
    from collections import Counter
    source_counts = Counter(item.source for item in items)
    
    table = Table(title="抓取统计")
    table.add_column("来源", style="cyan")
    table.add_column("数量", style="green", justify="right")
    
    for src, count in source_counts.most_common():
        table.add_row(src, str(count))
    
    console.print(table)
    
    # 输出到文件
    if output:
        import json
        output_path = Path(output)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump([item.to_dict() for item in items], f, ensure_ascii=False, indent=2)
        console.print(f"\n📁 已保存到: {output_path}")


@app.command()
def analyze(
    input_file: Optional[str] = typer.Option(None, "--input", "-i", help="从JSON文件读取新闻"),
    limit: int = typer.Option(20, "--limit", "-l", help="每个源的抓取数量")
):
    """
    分析新闻（需要配置 AI API）
    """
    # 验证配置
    missing = config.validate_config()
    if missing:
        console.print(f"[red]❌ 配置不完整，缺少: {', '.join(missing)}[/red]")
        console.print("请复制 .env.example 为 .env 并填写配置")
        raise typer.Exit(1)
    
    async def _fetch():
        fetcher = NewsFetcher()
        return await fetcher.fetch_all(limit=limit)
    
    # 获取新闻
    if input_file:
        import json
        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        items = [NewsItem(**item) for item in data]
        console.print(f"从文件加载了 {len(items)} 条新闻")
    else:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            progress.add_task("正在抓取新闻...", total=None)
            items = asyncio.run(_fetch())
        console.print(f"抓取了 {len(items)} 条新闻")
    
    # 分析
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        progress.add_task("AI 正在分析...", total=None)
        analyzer = AIAnalyzer()
        result = analyzer.analyze(items)
    
    # 显示结果
    console.print(Panel(result.summary, title="📌 本周热点总结", border_style="blue"))
    
    if result.trends:
        console.print(f"\n🏷️  趋势关键词: {', '.join(result.trends)}")
    
    if result.opportunities:
        console.print(f"💡 市场机会: {', '.join(result.opportunities)}")
    
    if result.project_suggestions:
        console.print("\n📋 项目建议:")
        for i, proj in enumerate(result.project_suggestions, 1):
            console.print(f"\n  {i}. [bold cyan]{proj.name}[/bold cyan] (优先级: {proj.priority}/5)")
            console.print(f"     {proj.description}")
            console.print(f"     👥 {proj.target_users} | 📊 {proj.difficulty}")


@app.command()
def run(
    send_email: bool = typer.Option(False, "--send-email", "-e", help="发送邮件"),
    dry_run: bool = typer.Option(False, "--dry-run", "-d", help="仅生成报告，不发送"),
    limit: int = typer.Option(20, "--limit", "-l", help="每个源的抓取数量"),
    html_only: bool = typer.Option(False, "--html", help="仅生成HTML（跳过PDF）")
):
    """
    运行完整流程：抓取 -> 分析 -> 生成报告 -> (发送邮件)
    """
    # 验证配置
    missing = config.validate_config()
    if missing:
        console.print(f"[red]❌ AI 配置不完整，缺少: {', '.join(missing)}[/red]")
        console.print("请复制 .env.example 为 .env 并填写配置")
        raise typer.Exit(1)
    
    if send_email and not dry_run:
        email_missing = config.validate_email_config()
        if email_missing:
            console.print(f"[red]❌ 邮件配置不完整，缺少: {', '.join(email_missing)}[/red]")
            raise typer.Exit(1)
    
    console.print(Panel.fit("🚀 News Collector 开始运行", style="bold blue"))
    
    # Step 1: 抓取新闻
    async def _fetch():
        fetcher = NewsFetcher()
        return await fetcher.fetch_all(limit=limit)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        progress.add_task("📡 正在抓取新闻...", total=None)
        news_items = asyncio.run(_fetch())
    
    console.print(f"✅ 抓取完成: {len(news_items)} 条新闻")
    
    if not news_items:
        console.print("[yellow]⚠️ 没有抓取到新闻，退出[/yellow]")
        raise typer.Exit(0)
    
    # Step 2: AI 分析
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        progress.add_task("🤖 AI 正在分析...", total=None)
        analyzer = AIAnalyzer()
        analysis = analyzer.analyze(news_items)
    
    console.print("✅ 分析完成")
    
    # 显示简要结果
    console.print(Panel(analysis.summary[:200] + "...", title="📌 摘要预览", border_style="dim"))
    
    # Step 3: 生成报告
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        progress.add_task("📄 正在生成报告...", total=None)
        generator = ReportGenerator()
        
        if html_only:
            report_path = generator.generate_html(analysis, news_items)
        else:
            report_path = generator.generate(analysis, news_items)
    
    console.print(f"✅ 报告已生成: [bold]{report_path}[/bold]")
    
    # Step 4: 发送邮件
    if send_email and not dry_run:
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            progress.add_task("📧 正在发送邮件...", total=None)
            sender = EmailSender()
            success = sender.send_report(report_path, analysis.summary[:200])
        
        if success:
            console.print(f"✅ 邮件已发送至: [bold]{config.EMAIL_TO}[/bold]")
        else:
            console.print("[red]❌ 邮件发送失败[/red]")
    
    console.print(Panel.fit("🎉 完成!", style="bold green"))


@app.command()
def version():
    """
    显示版本信息
    """
    console.print(Panel.fit(
        "[bold]News Collector[/bold] v1.0.0\n"
        "独立开发者的信息情报工具\n\n"
        "GitHub: https://github.com/your-repo/news-collector",
        title="📰 关于",
        border_style="blue"
    ))


if __name__ == "__main__":
    app()
