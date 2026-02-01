"""
邮件发送技能

Skill: 通过 SMTP 发送带附件的邮件
输入: PDF 文件路径 + 邮件配置
输出: 发送状态

学习要点:
1. Python smtplib 使用
2. MIME 邮件构建
3. SSL/TLS 安全连接
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from pathlib import Path
from typing import Optional

import config


class EmailSender:
    """
    邮件发送器
    
    通过 SMTP 发送邮件，支持：
    - 纯文本/HTML 正文
    - PDF 附件
    - SSL/TLS 加密
    
    Example:
        sender = EmailSender()
        success = sender.send(
            subject="科技周报",
            body="请查看附件中的本周科技周报。",
            attachment_path=Path("output/report.pdf")
        )
    """
    
    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        user: Optional[str] = None,
        password: Optional[str] = None,
        to_email: Optional[str] = None
    ):
        """
        初始化邮件发送器
        
        Args:
            host: SMTP 服务器地址
            port: SMTP 端口
            user: 发件人邮箱
            password: SMTP 密码/授权码
            to_email: 收件人邮箱
        """
        self.host = host or config.SMTP_HOST
        self.port = port or config.SMTP_PORT
        self.user = user or config.SMTP_USER
        self.password = password or config.SMTP_PASSWORD
        self.to_email = to_email or config.EMAIL_TO
    
    def validate_config(self) -> list[str]:
        """验证配置完整性，返回缺失项"""
        missing = []
        if not self.host:
            missing.append("SMTP_HOST")
        if not self.user:
            missing.append("SMTP_USER")
        if not self.password:
            missing.append("SMTP_PASSWORD")
        if not self.to_email:
            missing.append("EMAIL_TO")
        return missing
    
    def send(
        self,
        subject: str,
        body: str,
        attachment_path: Optional[Path] = None,
        to_email: Optional[str] = None,
        html_body: Optional[str] = None
    ) -> bool:
        """
        发送邮件
        
        Args:
            subject: 邮件主题
            body: 邮件正文（纯文本）
            attachment_path: 附件路径（可选）
            to_email: 收件人（可选，默认使用配置的收件人）
            html_body: HTML 格式正文（可选）
            
        Returns:
            是否发送成功
        """
        # 验证配置
        missing = self.validate_config()
        if missing:
            print(f"邮件配置不完整，缺少: {', '.join(missing)}")
            return False
        
        recipient = to_email or self.to_email
        
        try:
            # 创建邮件
            msg = MIMEMultipart()
            msg["From"] = self.user
            msg["To"] = recipient
            msg["Subject"] = subject
            
            # 添加正文
            if html_body:
                msg.attach(MIMEText(html_body, "html", "utf-8"))
            else:
                msg.attach(MIMEText(body, "plain", "utf-8"))
            
            # 添加附件
            if attachment_path and attachment_path.exists():
                with open(attachment_path, "rb") as f:
                    attachment = MIMEApplication(f.read())
                    attachment.add_header(
                        "Content-Disposition",
                        "attachment",
                        filename=attachment_path.name
                    )
                    msg.attach(attachment)
            
            # 发送邮件
            if self.port == 465:
                # SSL
                with smtplib.SMTP_SSL(self.host, self.port) as server:
                    server.login(self.user, self.password)
                    server.sendmail(self.user, recipient, msg.as_string())
            else:
                # STARTTLS
                with smtplib.SMTP(self.host, self.port) as server:
                    server.starttls()
                    server.login(self.user, self.password)
                    server.sendmail(self.user, recipient, msg.as_string())
            
            print(f"邮件发送成功: {recipient}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            print("邮件发送失败: SMTP 认证错误，请检查用户名和密码")
            return False
        except smtplib.SMTPConnectError:
            print(f"邮件发送失败: 无法连接到 SMTP 服务器 {self.host}:{self.port}")
            return False
        except Exception as e:
            print(f"邮件发送失败: {e}")
            return False
    
    def send_report(
        self,
        report_path: Path,
        summary: str = ""
    ) -> bool:
        """
        发送报告邮件
        
        Args:
            report_path: 报告文件路径
            summary: 报告摘要（用于邮件正文）
            
        Returns:
            是否发送成功
        """
        from datetime import datetime
        
        date_str = datetime.now().strftime("%Y年%m月%d日")
        subject = f"📊 科技周报 - {date_str}"
        
        body = f"""您好！

这是您订阅的科技周报，请查看附件。

{f'本周摘要：{summary}' if summary else ''}

---
本邮件由 News Collector 自动发送
"""
        
        html_body = f"""
<html>
<body style="font-family: 'PingFang SC', 'Microsoft YaHei', Arial, sans-serif; padding: 20px;">
    <h2 style="color: #1e40af;">📊 科技周报 - {date_str}</h2>
    <p>您好！</p>
    <p>这是您订阅的科技周报，请查看附件中的 PDF 文档。</p>
    {f'<div style="background: #f0f9ff; padding: 15px; border-radius: 8px; margin: 20px 0;"><strong>本周摘要：</strong><br>{summary}</div>' if summary else ''}
    <hr style="border: none; border-top: 1px solid #e2e8f0; margin: 20px 0;">
    <p style="color: #94a3b8; font-size: 12px;">本邮件由 News Collector 自动发送</p>
</body>
</html>
"""
        
        return self.send(
            subject=subject,
            body=body,
            html_body=html_body,
            attachment_path=report_path
        )


# 便捷函数
def send_email(
    subject: str,
    body: str,
    attachment_path: Optional[Path] = None
) -> bool:
    """
    便捷函数：发送邮件
    
    Args:
        subject: 主题
        body: 正文
        attachment_path: 附件路径
        
    Returns:
        是否成功
    """
    sender = EmailSender()
    return sender.send(subject, body, attachment_path)


def send_report(report_path: Path, summary: str = "") -> bool:
    """
    便捷函数：发送报告
    
    Args:
        report_path: 报告路径
        summary: 摘要
        
    Returns:
        是否成功
    """
    sender = EmailSender()
    return sender.send_report(report_path, summary)
