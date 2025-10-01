#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
邮件发送模块
支持发送 HTML 格式的新闻日报邮件
支持 QQ 邮箱和 Gmail
"""
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
from datetime import datetime
from pathlib import Path
from typing import Optional
import json

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EmailSenderError(Exception):
    """邮件发送异常"""
    pass


class EmailSender:
    """邮件发送器"""
    
    # 预设的 SMTP 服务器配置
    SMTP_CONFIGS = {
        'qq': {
            'server': 'smtp.qq.com',
            'port': 465,
            'use_ssl': True
        },
        'gmail': {
            'server': 'smtp.gmail.com',
            'port': 587,
            'use_ssl': False  # Gmail 使用 STARTTLS
        },
        '163': {
            'server': 'smtp.163.com',
            'port': 465,
            'use_ssl': True
        },
        'outlook': {
            'server': 'smtp-mail.outlook.com',
            'port': 587,
            'use_ssl': False
        }
    }
    
    def __init__(self, config_path: str = "email_config.json"):
        """
        初始化邮件发送器
        
        Args:
            config_path: 邮件配置文件路径
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
        # 加载邮件配置
        self.sender_email = self.config.get("sender_email", "")
        self.sender_password = self.config.get("sender_password", "")
        self.recipients = self.config.get("recipients", [])
        
        # SMTP 配置
        smtp_type = self.config.get("smtp_type", "qq").lower()
        custom_smtp = self.config.get("custom_smtp", {})
        
        if custom_smtp:
            # 使用自定义 SMTP 配置
            self.smtp_server = custom_smtp.get("server", "")
            self.smtp_port = custom_smtp.get("port", 465)
            self.use_ssl = custom_smtp.get("use_ssl", True)
        elif smtp_type in self.SMTP_CONFIGS:
            # 使用预设配置
            preset = self.SMTP_CONFIGS[smtp_type]
            self.smtp_server = preset['server']
            self.smtp_port = preset['port']
            self.use_ssl = preset['use_ssl']
        else:
            raise EmailSenderError(f"不支持的邮箱类型: {smtp_type}")
        
        logger.info(f"✅ 邮件发送器初始化完成 - 使用 {smtp_type.upper()} 邮箱")
        logger.info(f"   发件人: {self.sender_email}")
        logger.info(f"   SMTP 服务器: {self.smtp_server}:{self.smtp_port}")
    
    def _load_config(self) -> dict:
        """加载邮件配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                
                # 验证必需字段
                required_fields = ["sender_email", "sender_password", "recipients"]
                for field in required_fields:
                    if field not in config or not config[field]:
                        raise EmailSenderError(f"配置文件缺少必需字段: {field}")
                
                return config
                
        except FileNotFoundError:
            raise EmailSenderError(f"配置文件不存在: {self.config_path}")
        except json.JSONDecodeError as e:
            raise EmailSenderError(f"配置文件格式错误: {e}")
    
    def markdown_to_html(self, markdown_file: str) -> str:
        """
        将 Markdown 新闻日报转换为 HTML 格式
        
        Args:
            markdown_file: Markdown 文件路径
            
        Returns:
            HTML 内容
        """
        try:
            with open(markdown_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 简单的 Markdown 到 HTML 转换
            # 如果需要更完善的转换，可以使用 markdown 库
            html = self._simple_markdown_to_html(content)
            
            # 添加 CSS 样式
            styled_html = self._add_html_styles(html)
            
            return styled_html
            
        except Exception as e:
            raise EmailSenderError(f"Markdown 转换失败: {e}")
    
    def _simple_markdown_to_html(self, markdown_content: str) -> str:
        """简单的 Markdown 到 HTML 转换"""
        import re
        
        html = markdown_content
        
        # 标题转换
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        
        # 分隔线
        html = re.sub(r'^---+$', '<hr>', html, flags=re.MULTILINE)
        
        # 引用块
        html = re.sub(r'^> (.+)$', r'<blockquote>\1</blockquote>', html, flags=re.MULTILINE)
        
        # 粗体
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        
        # 斜体
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
        
        # 链接
        html = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2" target="_blank">\1</a>', html)
        
        # 列表项
        html = re.sub(r'^- (.+)$', r'<li>\1</li>', html, flags=re.MULTILINE)
        
        # 包裹连续的列表项
        html = re.sub(r'(<li>.*?</li>(?:\n<li>.*?</li>)*)', r'<ul>\1</ul>', html, flags=re.DOTALL)
        
        # 段落（连续的非标签行）
        lines = html.split('\n')
        result = []
        in_paragraph = False
        
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith('<'):
                if not in_paragraph:
                    result.append('<p>')
                    in_paragraph = True
                result.append(line)
            else:
                if in_paragraph:
                    result.append('</p>')
                    in_paragraph = False
                result.append(line)
        
        if in_paragraph:
            result.append('</p>')
        
        return '\n'.join(result)
    
    def _add_html_styles(self, html_content: str) -> str:
        """为 HTML 内容添加样式"""
        css = """
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                line-height: 1.6;
                color: #333;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            h1 {
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
                font-size: 28px;
                margin-top: 0;
            }
            h2 {
                color: #34495e;
                border-left: 4px solid #3498db;
                padding-left: 15px;
                font-size: 22px;
                margin-top: 30px;
            }
            h3 {
                color: #555;
                font-size: 18px;
                margin-top: 20px;
                margin-bottom: 10px;
            }
            blockquote {
                background: #e8f4f8;
                border-left: 4px solid #3498db;
                padding: 12px 20px;
                margin: 15px 0;
                font-style: italic;
                color: #555;
            }
            hr {
                border: none;
                border-top: 2px solid #ddd;
                margin: 30px 0;
            }
            ul {
                padding-left: 20px;
            }
            li {
                margin: 8px 0;
                line-height: 1.8;
            }
            a {
                color: #3498db;
                text-decoration: none;
            }
            a:hover {
                text-decoration: underline;
            }
            strong {
                color: #2c3e50;
                font-weight: 600;
            }
            p {
                margin: 12px 0;
                text-align: justify;
            }
            .container {
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }
            
            /* 移动端适配 */
            @media (max-width: 600px) {
                body {
                    padding: 10px;
                }
                .container {
                    padding: 15px;
                }
                h1 {
                    font-size: 24px;
                }
                h2 {
                    font-size: 20px;
                }
                h3 {
                    font-size: 16px;
                }
            }
        </style>
        """
        
        return f"""
        <!DOCTYPE html>
        <html lang="zh-CN">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>每日新闻导览</title>
            {css}
        </head>
        <body>
            <div class="container">
                {html_content}
            </div>
        </body>
        </html>
        """
    
    def send_email(self, 
                   subject: str, 
                   html_content: str,
                   recipients: Optional[list] = None) -> bool:
        """
        发送 HTML 格式的邮件
        
        Args:
            subject: 邮件主题
            html_content: HTML 格式的邮件正文
            recipients: 收件人列表（可选，默认使用配置文件中的）
            
        Returns:
            发送是否成功
        """
        if recipients is None:
            recipients = self.recipients
        
        if not recipients:
            raise EmailSenderError("没有指定收件人")
        
        try:
            # 创建邮件对象
            msg = MIMEMultipart('alternative')
            msg['From'] = self.sender_email  # QQ 邮箱要求使用简单格式
            msg['To'] = ', '.join(recipients)
            msg['Subject'] = Header(subject, 'utf-8')
            
            # 添加 HTML 正文
            html_part = MIMEText(html_content, 'html', 'utf-8')
            msg.attach(html_part)
            
            # 连接 SMTP 服务器并发送
            logger.info(f"📧 正在连接 SMTP 服务器: {self.smtp_server}:{self.smtp_port}")
            
            if self.use_ssl:
                # 使用 SSL
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=30)
            else:
                # 使用 STARTTLS
                server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30)
                server.starttls()
            
            logger.info("🔐 正在登录邮箱...")
            server.login(self.sender_email, self.sender_password)
            
            logger.info(f"📤 正在发送邮件到: {', '.join(recipients)}")
            server.sendmail(self.sender_email, recipients, msg.as_string())
            server.quit()
            
            logger.info("✅ 邮件发送成功!")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"❌ SMTP 认证失败: {e}")
            logger.error("   请检查邮箱地址和授权码是否正确")
            logger.error("   提示: QQ邮箱/163邮箱需要使用授权码而非登录密码")
            return False
            
        except smtplib.SMTPException as e:
            logger.error(f"❌ SMTP 错误: {e}")
            return False
            
        except Exception as e:
            logger.error(f"❌ 邮件发送失败: {e}")
            logger.error(f"   错误类型: {type(e).__name__}")
            return False
    
    def send_news_report(self, report_file: str) -> bool:
        """
        发送新闻日报邮件
        
        Args:
            report_file: Markdown 格式的日报文件路径
            
        Returns:
            发送是否成功
        """
        try:
            # 生成邮件主题
            today = datetime.now().strftime("%Y-%m-%d")
            subject = f"每日新闻导览 - {today}"
            
            logger.info(f"\n{'='*60}")
            logger.info(f"准备发送新闻日报邮件")
            logger.info(f"日报文件: {report_file}")
            logger.info(f"{'='*60}\n")
            
            # 转换为 HTML
            logger.info("📝 正在将 Markdown 转换为 HTML...")
            html_content = self.markdown_to_html(report_file)
            
            # 发送邮件
            success = self.send_email(subject, html_content)
            
            if success:
                logger.info(f"\n{'='*60}")
                logger.info(f"✅ 新闻日报邮件发送成功!")
                logger.info(f"   主题: {subject}")
                logger.info(f"   收件人: {', '.join(self.recipients)}")
                logger.info(f"{'='*60}\n")
            
            return success
            
        except Exception as e:
            logger.error(f"❌ 发送新闻日报失败: {e}")
            return False


def test_email_config():
    """测试邮件配置"""
    try:
        sender = EmailSender("email_config.json")
        
        print("\n✅ 邮件配置加载成功!")
        print(f"   发件人: {sender.sender_email}")
        print(f"   SMTP: {sender.smtp_server}:{sender.smtp_port}")
        print(f"   收件人: {', '.join(sender.recipients)}")
        
        # 发送测试邮件
        test_html = """
        <h1>测试邮件</h1>
        <p>这是一封测试邮件，用于验证邮件发送功能是否正常。</p>
        <p>如果您收到这封邮件，说明配置成功！</p>
        """
        
        response = input("\n是否发送测试邮件? (y/n): ")
        if response.lower() == 'y':
            success = sender.send_email("邮件发送测试", test_html)
            if success:
                print("\n✅ 测试邮件发送成功!")
            else:
                print("\n❌ 测试邮件发送失败，请查看错误信息")
        
    except EmailSenderError as e:
        print(f"\n❌ 配置错误: {e}")
    except Exception as e:
        print(f"\n❌ 未知错误: {e}")


if __name__ == "__main__":
    test_email_config()
