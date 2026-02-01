"""
AI 分析技能

Skill: 使用 AI 分析新闻，提取洞察和项目建议
输入: List[NewsItem]
输出: AnalysisResult（结构化分析结果）

学习要点:
1. OpenAI 兼容接口调用
2. Prompt Engineering
3. 结构化输出（JSON Schema）
"""

import json
from dataclasses import dataclass, field
from typing import Optional, List
from openai import OpenAI

import config
from sources import NewsItem


@dataclass
class ProjectSuggestion:
    """项目建议"""
    name: str                    # 项目名称
    description: str             # 项目描述
    target_users: str            # 目标用户
    tech_stack: List[str]        # 技术栈建议
    difficulty: str              # 难度：简单/中等/困难
    reason: str                  # 推荐理由
    priority: int                # 优先级：1-5，5最高


@dataclass
class AnalysisResult:
    """AI分析结果"""
    summary: str                              # 本周热点总结
    trends: List[str]                         # 趋势关键词
    opportunities: List[str]                  # 市场机会
    project_suggestions: List[ProjectSuggestion]  # 项目建议
    raw_response: str = ""                    # 原始响应（调试用）


class AIAnalyzer:
    """
    AI 分析器
    
    使用 AI 大模型分析新闻内容，提取：
    - 热点趋势总结
    - 市场机会
    - 值得做的项目建议
    
    支持通义千问、OpenAI等兼容接口
    
    Example:
        analyzer = AIAnalyzer()
        result = await analyzer.analyze(news_items)
        print(result.summary)
        for project in result.project_suggestions:
            print(f"- {project.name}: {project.description}")
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        """
        初始化 AI 分析器
        
        Args:
            api_key: API密钥（默认从config读取）
            base_url: API地址（默认从config读取）
            model: 模型名称（默认从config读取）
        """
        self.api_key = api_key or config.AI_API_KEY
        self.base_url = base_url or config.AI_BASE_URL
        self.model = model or config.AI_MODEL
        
        if not self.api_key:
            raise ValueError("未配置 AI API Key，请设置 DASHSCOPE_API_KEY 环境变量")
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def analyze(self, news_items: List[NewsItem]) -> AnalysisResult:
        """
        分析新闻列表
        
        Args:
            news_items: 新闻条目列表
            
        Returns:
            AnalysisResult 分析结果
        """
        if not news_items:
            return AnalysisResult(
                summary="没有可分析的新闻",
                trends=[],
                opportunities=[],
                project_suggestions=[]
            )
        
        # 构建新闻摘要文本
        news_text = self._format_news_for_prompt(news_items)
        
        # 构建 prompt
        prompt = self._build_analysis_prompt(news_text)
        
        # 调用 AI
        response = self._call_ai(prompt)
        
        # 解析结果
        return self._parse_response(response)
    
    def _format_news_for_prompt(self, items: List[NewsItem]) -> str:
        """将新闻列表格式化为文本"""
        lines = []
        for i, item in enumerate(items, 1):
            lines.append(f"{i}. [{item.source}] {item.title}")
            if item.summary:
                lines.append(f"   摘要: {item.summary[:200]}")
            lines.append("")
        return "\n".join(lines)
    
    def _build_analysis_prompt(self, news_text: str) -> str:
        """构建分析提示词"""
        return f"""你是一位资深的科技产品分析师和独立开发者顾问。请分析以下一周内的科技新闻，为独立开发者提供有价值的洞察和项目建议。

## 新闻列表
{news_text}

## 分析要求
请从独立开发者的角度，分析这些新闻并提供：

1. **本周热点总结**（200字以内）：概括主要趋势和值得关注的方向

2. **趋势关键词**：提取3-5个热门技术/产品趋势关键词

3. **市场机会**：列出2-3个可能的市场机会

4. **项目建议**：推荐3-5个适合独立开发者的项目，每个项目包含：
   - 项目名称
   - 一句话描述
   - 目标用户群体
   - 推荐技术栈
   - 难度评估（简单/中等/困难）
   - 推荐理由
   - 优先级（1-5分）

## 输出格式
请严格按以下 JSON 格式输出（不要包含其他内容）：

```json
{{
  "summary": "本周热点总结...",
  "trends": ["趋势1", "趋势2", "趋势3"],
  "opportunities": ["机会1", "机会2"],
  "project_suggestions": [
    {{
      "name": "项目名称",
      "description": "项目描述",
      "target_users": "目标用户",
      "tech_stack": ["技术1", "技术2"],
      "difficulty": "中等",
      "reason": "推荐理由",
      "priority": 4
    }}
  ]
}}
```"""
    
    def _call_ai(self, prompt: str) -> str:
        """调用 AI API"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一位专业的科技分析师，擅长发现市场机会和产品趋势。请用中文回复，输出格式为JSON。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=4000
        )
        
        return response.choices[0].message.content or ""
    
    def _parse_response(self, response: str) -> AnalysisResult:
        """解析 AI 响应"""
        try:
            # 尝试提取 JSON
            json_str = response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            
            data = json.loads(json_str.strip())
            
            # 解析项目建议
            suggestions = []
            for proj in data.get("project_suggestions", []):
                suggestions.append(ProjectSuggestion(
                    name=proj.get("name", ""),
                    description=proj.get("description", ""),
                    target_users=proj.get("target_users", ""),
                    tech_stack=proj.get("tech_stack", []),
                    difficulty=proj.get("difficulty", "中等"),
                    reason=proj.get("reason", ""),
                    priority=proj.get("priority", 3)
                ))
            
            return AnalysisResult(
                summary=data.get("summary", ""),
                trends=data.get("trends", []),
                opportunities=data.get("opportunities", []),
                project_suggestions=suggestions,
                raw_response=response
            )
            
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            # 解析失败，返回原始响应
            return AnalysisResult(
                summary=f"AI分析完成，但解析失败: {e}",
                trends=[],
                opportunities=[],
                project_suggestions=[],
                raw_response=response
            )


# 便捷函数
def analyze_news(news_items: List[NewsItem]) -> AnalysisResult:
    """
    便捷函数：分析新闻
    
    Args:
        news_items: 新闻列表
        
    Returns:
        分析结果
    """
    analyzer = AIAnalyzer()
    return analyzer.analyze(news_items)
