#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定时任务管理模块
使用 python-crontab 自动管理 cron 任务
"""
import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional
import json

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CronManagerError(Exception):
    """定时任务管理异常"""
    pass


class CronTaskManager:
    """Cron 定时任务管理器"""
    
    def __init__(self, config_path: str = "cron_config.json"):
        """
        初始化定时任务管理器
        
        Args:
            config_path: 定时任务配置文件路径
        """
        try:
            from crontab import CronTab
            self.CronTab = CronTab
        except ImportError:
            raise CronManagerError(
                "需要安装 python-crontab 库: pip install python-crontab"
            )
        
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
        # 获取当前用户的 crontab
        try:
            self.cron = self.CronTab(user=True)
            logger.info("✅ Crontab 初始化成功")
        except Exception as e:
            raise CronManagerError(f"无法访问 crontab: {e}")
    
    def _load_config(self) -> dict:
        """加载定时任务配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            # 如果配置文件不存在，返回默认配置
            logger.warning(f"配置文件不存在，使用默认配置: {self.config_path}")
            return self._get_default_config()
        except json.JSONDecodeError as e:
            raise CronManagerError(f"配置文件格式错误: {e}")
    
    def _get_default_config(self) -> dict:
        """获取默认配置"""
        return {
            "enabled": True,
            "schedule": {
                "hour": 7,
                "minute": 0
            },
            "script_path": str(Path(__file__).parent / "daily_news_task.py"),
            "log_file": str(Path(__file__).parent / "logs" / "cron_task.log"),
            "python_executable": sys.executable,
            "task_comment": "Daily News Scraper Task"
        }
    
    def _get_script_path(self) -> str:
        """获取脚本的绝对路径"""
        script_path = self.config.get("script_path", "")
        
        if not script_path:
            # 默认使用 daily_news_task.py
            script_path = str(Path(__file__).parent / "daily_news_task.py")
        
        # 转换为绝对路径
        script_path = str(Path(script_path).resolve())
        
        if not Path(script_path).exists():
            raise CronManagerError(f"脚本文件不存在: {script_path}")
        
        return script_path
    
    def _get_python_executable(self) -> str:
        """获取 Python 解释器路径"""
        python_path = self.config.get("python_executable", sys.executable)
        
        # 转换为绝对路径
        python_path = str(Path(python_path).resolve())
        
        if not Path(python_path).exists():
            raise CronManagerError(f"Python 解释器不存在: {python_path}")
        
        return python_path
    
    def _get_log_file(self) -> str:
        """获取日志文件路径"""
        log_file = self.config.get("log_file", "")
        
        if not log_file:
            log_file = str(Path(__file__).parent / "logs" / "cron_task.log")
        
        # 确保日志目录存在
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        return str(log_path.resolve())
    
    def _build_command(self) -> str:
        """构建要执行的完整命令"""
        python_exe = self._get_python_executable()
        script_path = self._get_script_path()
        log_file = self._get_log_file()
        
        # 构建命令：Python解释器 脚本路径 >> 日志文件 2>&1
        command = f"{python_exe} {script_path} >> {log_file} 2>&1"
        
        return command
    
    def task_exists(self, comment: str) -> bool:
        """
        检查任务是否已存在
        
        Args:
            comment: 任务注释
            
        Returns:
            任务是否存在
        """
        for job in self.cron:
            if job.comment == comment:
                return True
        return False
    
    def add_task(self, force: bool = False) -> bool:
        """
        添加定时任务
        
        Args:
            force: 是否强制添加（如果任务已存在，先删除再添加）
            
        Returns:
            添加是否成功
        """
        try:
            comment = self.config.get("task_comment", "Daily News Scraper Task")
            
            # 检查任务是否已存在
            if self.task_exists(comment):
                if not force:
                    logger.info(f"⚠️  定时任务已存在: {comment}")
                    logger.info("   使用 --force 参数可以强制重新添加")
                    return False
                else:
                    logger.info(f"🔄 删除现有任务: {comment}")
                    self.remove_task(comment)
            
            # 构建命令
            command = self._build_command()
            
            # 创建新任务
            job = self.cron.new(command=command, comment=comment)
            
            # 设置执行时间
            schedule = self.config.get("schedule", {})
            hour = schedule.get("hour", 7)
            minute = schedule.get("minute", 0)
            
            job.setall(f"{minute} {hour} * * *")
            
            # 写入 crontab
            self.cron.write()
            
            logger.info(f"\n{'='*60}")
            logger.info(f"✅ 定时任务添加成功!")
            logger.info(f"{'='*60}")
            logger.info(f"   任务名称: {comment}")
            logger.info(f"   执行时间: 每天 {hour:02d}:{minute:02d}")
            logger.info(f"   执行命令: {command}")
            logger.info(f"   日志文件: {self._get_log_file()}")
            logger.info(f"{'='*60}\n")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ 添加定时任务失败: {e}")
            return False
    
    def remove_task(self, comment: Optional[str] = None) -> bool:
        """
        删除定时任务
        
        Args:
            comment: 任务注释（可选，默认使用配置文件中的）
            
        Returns:
            删除是否成功
        """
        try:
            if comment is None:
                comment = self.config.get("task_comment", "Daily News Scraper Task")
            
            removed = False
            for job in self.cron:
                if job.comment == comment:
                    self.cron.remove(job)
                    removed = True
            
            if removed:
                self.cron.write()
                logger.info(f"✅ 定时任务已删除: {comment}")
                return True
            else:
                logger.warning(f"⚠️  未找到任务: {comment}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 删除定时任务失败: {e}")
            return False
    
    def list_tasks(self, show_all: bool = False) -> None:
        """
        列出所有定时任务
        
        Args:
            show_all: 是否显示所有任务（否则只显示本项目的任务）
        """
        try:
            comment = self.config.get("task_comment", "Daily News Scraper Task")
            
            print(f"\n{'='*60}")
            print("当前 Crontab 任务列表")
            print(f"{'='*60}\n")
            
            found = False
            for idx, job in enumerate(self.cron, 1):
                if show_all or job.comment == comment:
                    found = True
                    print(f"任务 #{idx}")
                    print(f"  注释: {job.comment}")
                    print(f"  时间: {job.slices}")
                    print(f"  命令: {job.command}")
                    print(f"  启用: {'是' if job.is_enabled() else '否'}")
                    print()
            
            if not found:
                if show_all:
                    print("没有找到任何定时任务")
                else:
                    print(f"没有找到项目任务: {comment}")
                    print("使用 --all 参数可以查看所有任务")
            
            print(f"{'='*60}\n")
            
        except Exception as e:
            logger.error(f"❌ 列出任务失败: {e}")
    
    def enable_task(self, comment: Optional[str] = None) -> bool:
        """
        启用定时任务
        
        Args:
            comment: 任务注释
            
        Returns:
            启用是否成功
        """
        try:
            if comment is None:
                comment = self.config.get("task_comment", "Daily News Scraper Task")
            
            found = False
            for job in self.cron:
                if job.comment == comment:
                    job.enable()
                    found = True
            
            if found:
                self.cron.write()
                logger.info(f"✅ 任务已启用: {comment}")
                return True
            else:
                logger.warning(f"⚠️  未找到任务: {comment}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 启用任务失败: {e}")
            return False
    
    def disable_task(self, comment: Optional[str] = None) -> bool:
        """
        禁用定时任务
        
        Args:
            comment: 任务注释
            
        Returns:
            禁用是否成功
        """
        try:
            if comment is None:
                comment = self.config.get("task_comment", "Daily News Scraper Task")
            
            found = False
            for job in self.cron:
                if job.comment == comment:
                    job.enable(False)
                    found = True
            
            if found:
                self.cron.write()
                logger.info(f"✅ 任务已禁用: {comment}")
                return True
            else:
                logger.warning(f"⚠️  未找到任务: {comment}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 禁用任务失败: {e}")
            return False


def main():
    """主函数 - 命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="新闻抓取定时任务管理工具")
    parser.add_argument(
        'action',
        choices=['add', 'remove', 'list', 'enable', 'disable'],
        help='操作类型'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='强制操作（用于 add 命令）'
    )
    parser.add_argument(
        '--all',
        action='store_true',
        help='显示所有任务（用于 list 命令）'
    )
    parser.add_argument(
        '--config',
        default='cron_config.json',
        help='配置文件路径'
    )
    
    args = parser.parse_args()
    
    try:
        manager = CronTaskManager(args.config)
        
        if args.action == 'add':
            success = manager.add_task(force=args.force)
            sys.exit(0 if success else 1)
            
        elif args.action == 'remove':
            success = manager.remove_task()
            sys.exit(0 if success else 1)
            
        elif args.action == 'list':
            manager.list_tasks(show_all=args.all)
            sys.exit(0)
            
        elif args.action == 'enable':
            success = manager.enable_task()
            sys.exit(0 if success else 1)
            
        elif args.action == 'disable':
            success = manager.disable_task()
            sys.exit(0 if success else 1)
    
    except CronManagerError as e:
        logger.error(f"❌ 错误: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("\n操作被用户取消")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ 未预期的错误: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
