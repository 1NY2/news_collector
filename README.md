# News Collector - 新闻收集小助手

一个面向独立开发者的信息收集工具，自动爬取科技新闻，通过 AI 分析生成项目建议，输出精美报告并发送到邮箱。

## 特性

- **多源聚合**: 支持 Hacker News、GitHub Trending、TechCrunch、36氪、少数派等多个免费新闻源
- **插件式架构**: 轻松添加新的新闻源，无需修改核心代码
- **AI 智能分析**: 使用通义千问（或其他 OpenAI 兼容接口）分析新闻，提取趋势和项目建议
- **精美报告**: 自动生成 HTML/PDF 格式的周报
- **邮件推送**: 支持 SMTP 发送报告到邮箱
- **定时执行**: 支持 cron 定时任务，每周自动运行

## 快速开始

### 1. 安装依赖

```bash
cd news-collector
pip3 install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入必要配置：

```bash
# AI配置（必填）
DASHSCOPE_API_KEY=your_dashscope_api_key
AI_MODEL=qwen-plus

# 邮件配置（发送邮件时必填）
SMTP_HOST=smtp.qq.com
SMTP_PORT=465
SMTP_USER=your_email@qq.com
SMTP_PASSWORD=your_smtp_password
EMAIL_TO=recipient@example.com
```

### 3. 运行

```bash
# 查看帮助
python3 main.py --help

# 列出所有新闻源
python3 main.py sources

# 抓取新闻
python3 main.py fetch --limit 20

# 完整流程（抓取 -> 分析 -> 生成报告）
python3 main.py run --html

# 完整流程并发送邮件
python3 main.py run --send-email
```

## 命令说明

| 命令 | 说明 |
|------|------|
| `python3 main.py sources` | 列出所有可用的新闻源 |
| `python3 main.py fetch` | 抓取新闻 |
| `python3 main.py fetch --source HackerNews` | 从指定源抓取 |
| `python3 main.py fetch --limit 10` | 限制每个源的抓取数量 |
| `python3 main.py analyze` | 分析新闻（需配置 AI API） |
| `python3 main.py run` | 运行完整流程 |
| `python3 main.py run --html` | 生成 HTML 报告 |
| `python3 main.py run --send-email` | 完整流程并发送邮件 |
| `python3 main.py run --dry-run` | 仅生成报告，不发送 |
| `python3 main.py version` | 显示版本信息 |

## 项目结构

```
news-collector/
├── main.py                 # CLI入口
├── config.py               # 配置管理
├── requirements.txt        # 依赖清单
├── .env.example            # 环境变量示例
├── cron_setup.sh           # 定时任务设置脚本
├── sources/                # 新闻源模块（插件式）
│   ├── __init__.py         # 自动发现机制
│   ├── base.py             # 基类 + 注册装饰器
│   ├── hackernews.py       # Hacker News (API)
│   ├── github_trending.py  # GitHub Trending (爬虫)
│   └── rss_feeds.py        # RSS源集合
├── skills/                 # 技能模块（供学习）
│   ├── news_fetcher.py     # 新闻抓取技能
│   ├── ai_analyzer.py      # AI分析技能
│   ├── report_generator.py # 报告生成技能
│   └── email_sender.py     # 邮件发送技能
├── templates/
│   └── report.html         # 报告HTML模板
└── output/                 # 报告输出目录
```

## 新闻源

| 来源 | 类型 | 费用 | 说明 |
|------|------|------|------|
| HackerNews | API | 免费 | 热门技术新闻 |
| GitHubTrending | 爬虫 | 免费 | 热门开源项目 |
| TechCrunch | RSS | 免费 | 科技资讯 |
| 36Kr | RSS | 免费 | 国内创投资讯 |
| SSPAI | RSS | 免费 | 效率工具与科技 |
| V2EX | RSS | 免费 | 技术社区热帖 |

## 添加新的新闻源

在 `sources/` 目录下创建新文件，只需 3 步：

```python
# sources/my_source.py
from .base import NewsSource, NewsItem, register_source

@register_source  # 1. 使用装饰器注册
class MySource(NewsSource):
    name = "MySource"  # 2. 设置源名称
    description = "我的新闻源"
    enabled = True
    
    async def fetch(self, limit: int = 20):  # 3. 实现fetch方法
        items = []
        # ... 抓取逻辑 ...
        return items
```

**无需修改其他代码**，系统会自动发现并使用新源。

## Skills 说明

`skills/` 目录包含 4 个独立的技能模块，每个模块都可以单独学习和使用：

| 模块 | 功能 | 学习要点 |
|------|------|----------|
| `news_fetcher.py` | 新闻抓取 | 异步编程、并发抓取 |
| `ai_analyzer.py` | AI分析 | OpenAI API、Prompt设计 |
| `report_generator.py` | 报告生成 | Jinja2模板、PDF生成 |
| `email_sender.py` | 邮件发送 | SMTP、MIME协议 |

## 定时任务

设置每周自动执行：

```bash
# 设置定时任务（每周一 9:00）
chmod +x cron_setup.sh
./cron_setup.sh

# 查看状态
./cron_setup.sh --status

# 移除定时任务
./cron_setup.sh --remove
```

## PDF 生成（可选）

PDF 生成需要系统级依赖。如果不需要 PDF，系统会自动回退到 HTML。

```bash
# macOS
brew install pango gdk-pixbuf libffi

# Ubuntu/Debian
apt-get install libpango-1.0-0 libpangocairo-1.0-0 libgdk-pixbuf2.0-0
```

## 切换 AI 模型

系统默认使用通义千问，但支持任何 OpenAI 兼容接口：

```bash
# .env 配置

# 通义千问（默认）
DASHSCOPE_API_KEY=your_key
AI_MODEL=qwen-plus

# 切换到 OpenAI
AI_BASE_URL=https://api.openai.com/v1
AI_API_KEY=your_openai_key
AI_MODEL=gpt-4

# 切换到 DeepSeek
AI_BASE_URL=https://api.deepseek.com/v1
AI_API_KEY=your_deepseek_key
AI_MODEL=deepseek-chat
```

## 获取 API Key

### 通义千问
1. 访问 [阿里云百炼平台](https://bailian.console.aliyun.com/)
2. 开通服务并创建 API Key
3. 将 API Key 填入 `.env` 的 `DASHSCOPE_API_KEY`

### 邮箱 SMTP
以 QQ 邮箱为例：
1. 登录 QQ 邮箱 -> 设置 -> 账户
2. 开启 SMTP 服务，获取授权码
3. 填入 `.env` 的 `SMTP_PASSWORD`

## License

MIT
