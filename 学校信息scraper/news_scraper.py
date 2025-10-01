#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新闻抓取工具
使用 newspaper3k 抓取新闻并按关键词分类
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set
import newspaper
from newspaper import Article, Source
import time
import re

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NewsScraperError(Exception):
    """新闻抓取异常"""
    pass


class NewsScraper:
    """新闻抓取器"""
    
    def __init__(self, config_path: str = "config.json"):
        """
        初始化新闻抓取器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        self.news_sources = self.config.get("news_sources", {})
        self.keywords = self.config.get("keywords", {})
        self.max_articles = self.config.get("max_articles", 50)
        self.language = self.config.get("language", "zh")
        
    def _load_config(self) -> dict:
        """加载配置文件"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"配置文件不存在: {self.config_path}")
            raise NewsScraperError(f"配置文件不存在: {self.config_path}")
        except json.JSONDecodeError as e:
            logger.error(f"配置文件格式错误: {e}")
            raise NewsScraperError(f"配置文件格式错误: {e}")
    
    def _match_keywords(self, text: str, category: str) -> bool:
        """
        检查文本是否包含指定分类的关键词
        
        Args:
            text: 待检查的文本
            category: 关键词分类
            
        Returns:
            是否匹配
        """
        if not text or category not in self.keywords:
            return False
        
        text_lower = text.lower()
        keywords = self.keywords[category]
        
        for keyword in keywords:
            if keyword.lower() in text_lower:
                return True
        return False
    
    def _fetch_articles_from_source(self, url: str) -> List[Article]:
        """
        从单个新闻源抓取文章
        
        Args:
            url: 新闻源URL
            
        Returns:
            文章列表
        """
        articles = []
        try:
            logger.info(f"正在抓取: {url}")
            
            # 创建新闻源
            source = Source(url, language=self.language)
            source.build()
            
            # 限制文章数量
            article_urls = source.article_urls()[:self.max_articles]
            logger.info(f"发现 {len(article_urls)} 篇文章")
            
            # 抓取每篇文章
            for article_url in article_urls:
                try:
                    article = Article(article_url, language=self.language)
                    article.download()
                    article.parse()
                    articles.append(article)
                    time.sleep(0.5)  # 避免请求过快
                except Exception as e:
                    logger.warning(f"抓取文章失败 {article_url}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"抓取新闻源失败 {url}: {e}")
        
        return articles
    
    def scrape_news(self) -> Dict[str, List[Dict]]:
        """
        抓取所有新闻源的新闻
        
        Returns:
            按分类组织的新闻字典
        """
        categorized_news = {category: [] for category in self.keywords.keys()}
        categorized_news["其他"] = []
        
        # 遍历所有新闻源
        for region, sources in self.news_sources.items():
            logger.info(f"\n开始抓取【{region}】新闻源")
            
            for source_url in sources:
                articles = self._fetch_articles_from_source(source_url)
                
                # 分类文章
                for article in articles:
                    if not article.title:
                        continue
                    
                    article_info = {
                        "title": article.title,
                        "url": article.url,
                        "source": source_url,
                        "region": region,
                        "publish_date": article.publish_date.strftime("%Y-%m-%d") if article.publish_date else "未知"
                    }
                    
                    # 检查文章标题是否匹配关键词
                    matched = False
                    for category in self.keywords.keys():
                        if self._match_keywords(article.title, category):
                            categorized_news[category].append(article_info)
                            matched = True
                            break
                    
                    # 如果没有匹配任何分类，放入"其他"
                    if not matched:
                        categorized_news["其他"].append(article_info)
        
        return categorized_news
    
    def generate_markdown_report(self, news_data: Dict[str, List[Dict]], output_dir: str = "output") -> str:
        """
        生成 Markdown 格式的日报
        
        Args:
            news_data: 分类后的新闻数据
            output_dir: 输出目录
            
        Returns:
            生成的文件路径
        """
        # 创建输出目录
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # 生成文件名
        today = datetime.now().strftime("%Y-%m-%d")
        filename = f"news_daily_report_{today}.md"
        filepath = output_path / filename
        
        # 生成 Markdown 内容
        content = []
        content.append(f"# 新闻日报 - {today}\n")
        content.append(f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        content.append("---\n")
        
        # 统计信息
        total_articles = sum(len(articles) for articles in news_data.values())
        content.append(f"## 📊 统计概览\n")
        content.append(f"- **总计文章数**: {total_articles}\n")
        for category, articles in news_data.items():
            if articles:
                content.append(f"- **{category}**: {len(articles)} 篇\n")
        content.append("\n---\n")
        
        # 按分类输出新闻
        for category, articles in news_data.items():
            if not articles:
                continue
                
            content.append(f"\n## 📰 {category}\n")
            content.append(f"*共 {len(articles)} 篇新闻*\n\n")
            
            for idx, article in enumerate(articles, 1):
                content.append(f"### {idx}. {article['title']}\n")
                content.append(f"- **链接**: [{article['url']}]({article['url']})\n")
                content.append(f"- **来源**: {article['source']}\n")
                content.append(f"- **区域**: {article['region']}\n")
                content.append(f"- **发布日期**: {article['publish_date']}\n\n")
        
        # 页脚
        content.append("\n---\n")
        content.append(f"*报告由新闻抓取工具自动生成*\n")
        
        # 写入文件
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(''.join(content))
        
        logger.info(f"日报已生成: {filepath}")
        return str(filepath)
    
    def run(self, output_dir: str = "output") -> str:
        """
        运行新闻抓取并生成报告
        
        Args:
            output_dir: 输出目录
            
        Returns:
            生成的报告文件路径
        """
        logger.info("=" * 60)
        logger.info("开始抓取新闻...")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        # 抓取新闻
        news_data = self.scrape_news()
        
        # 生成报告
        report_path = self.generate_markdown_report(news_data, output_dir)
        
        elapsed_time = time.time() - start_time
        logger.info("=" * 60)
        logger.info(f"抓取完成! 耗时: {elapsed_time:.2f} 秒")
        logger.info(f"报告路径: {report_path}")
        logger.info("=" * 60)
        
        return report_path


def main():
    """主函数"""
    try:
        scraper = NewsScraper("config.json")
        report_path = scraper.run("output")
        print(f"\n✅ 新闻日报生成成功!")
        print(f"📄 报告位置: {report_path}")
    except NewsScraperError as e:
        logger.error(f"程序执行失败: {e}")
        return 1
    except KeyboardInterrupt:
        logger.info("\n程序被用户中断")
        return 1
    except Exception as e:
        logger.error(f"未预期的错误: {e}", exc_info=True)
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
