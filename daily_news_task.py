#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日新闻任务脚本
由 cron 定时执行，抓取新闻并发送邮件
"""
import sys
import logging
from pathlib import Path
from datetime import datetime

# 添加项目路径到 sys.path
project_dir = Path(__file__).parent
sys.path.insert(0, str(project_dir))

from news_scraper_hybrid import HybridNewsScraper, NewsScraperError
from email_sender import EmailSender, EmailSenderError

# 配置日志
log_dir = project_dir / "logs"
log_dir.mkdir(exist_ok=True)

log_file = log_dir / f"daily_task_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def run_daily_task():
    """运行每日新闻任务"""
    logger.info("="*60)
    logger.info("每日新闻任务开始执行")
    logger.info(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("="*60)
    
    try:
        # 步骤 1: 抓取新闻并生成报告
        logger.info("\n【步骤 1/2】抓取新闻并生成报告...")
        
        scraper = HybridNewsScraper("config.json")
        report_path = scraper.run("output")
        
        logger.info(f"✅ 新闻报告生成成功: {report_path}")
        
        # 步骤 2: 发送邮件
        logger.info("\n【步骤 2/2】发送邮件...")
        
        try:
            sender = EmailSender("email_config.json")
            success = sender.send_news_report(report_path)
            
            if success:
                logger.info("✅ 邮件发送成功")
            else:
                logger.error("❌ 邮件发送失败")
                return 1
                
        except EmailSenderError as e:
            logger.error(f"❌ 邮件发送器初始化失败: {e}")
            logger.warning("⚠️  跳过邮件发送步骤")
            # 即使邮件发送失败，任务也算部分成功
            return 0
        
        logger.info("\n" + "="*60)
        logger.info("✅ 每日新闻任务执行完成!")
        logger.info("="*60)
        
        return 0
        
    except NewsScraperError as e:
        logger.error(f"❌ 新闻抓取失败: {e}")
        return 1
        
    except FileNotFoundError as e:
        logger.error(f"❌ 文件不存在: {e}")
        logger.error("   请确保 config.json 和 email_config.json 文件存在")
        return 1
        
    except Exception as e:
        logger.error(f"❌ 任务执行失败: {e}", exc_info=True)
        return 1


def main():
    """主函数"""
    try:
        exit_code = run_daily_task()
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        logger.info("\n任务被用户中断")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"❌ 未预期的错误: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
