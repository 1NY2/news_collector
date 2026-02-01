"""
配置管理模块
从环境变量加载配置，提供默认值
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 项目根目录
BASE_DIR = Path(__file__).parent

# ========== AI 配置 ==========
AI_API_KEY = os.getenv("DASHSCOPE_API_KEY") or os.getenv("AI_API_KEY", "")
AI_BASE_URL = os.getenv("AI_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
AI_MODEL = os.getenv("AI_MODEL", "qwen-plus")

# ========== 邮件配置 ==========
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.qq.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "465"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
EMAIL_TO = os.getenv("EMAIL_TO", "")

# ========== 其他配置 ==========
NEWS_LIMIT_PER_SOURCE = int(os.getenv("NEWS_LIMIT_PER_SOURCE", "20"))
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", str(BASE_DIR / "output")))

# 确保输出目录存在
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# ========== RSS 源配置 ==========
RSS_FEEDS = {
    "TechCrunch": "https://techcrunch.com/feed/",
    "36Kr": "https://36kr.com/feed",
    "SSPAI": "https://sspai.com/feed",
    "V2EX": "https://www.v2ex.com/index.xml",
    "HackerNews": "https://hnrss.org/frontpage",
    "InfoQ": "https://www.infoq.cn/feed",
}


def validate_config() -> list[str]:
    """验证配置完整性，返回缺失的配置项列表"""
    missing = []
    if not AI_API_KEY:
        missing.append("DASHSCOPE_API_KEY 或 AI_API_KEY")
    return missing


def validate_email_config() -> list[str]:
    """验证邮件配置完整性"""
    missing = []
    if not SMTP_USER:
        missing.append("SMTP_USER")
    if not SMTP_PASSWORD:
        missing.append("SMTP_PASSWORD")
    if not EMAIL_TO:
        missing.append("EMAIL_TO")
    return missing
