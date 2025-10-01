#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
新闻抓取工具 - 集成 NewsAPI 版本
支持 newspaper3k 和 NewsAPI 两种抓取方式
"""
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Set, Optional
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


class NewsAPIIntegration:
    """NewsAPI 集成"""
    
    def __init__(self, api_key: str):
        """
        初始化 NewsAPI
        
        Args:
            api_key: NewsAPI 密钥
        """
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2"
        
        try:
            import requests
            self.requests = requests
        except ImportError:
            raise NewsScraperError("需要安装 requests 库: pip install requests")
    
    def get_top_headlines(self, 
                         category: Optional[str] = None,
                         country: str = 'us',
                         q: Optional[str] = None,
                         page_size: int = 100) -> List[Dict]:
        """
        获取头条新闻
        
        Args:
            category: 分类 (business, entertainment, general, health, science, sports, technology)
            country: 国家代码 (us, cn, gb, etc.)
            q: 搜索关键词
            page_size: 返回结果数量 (最多100)
            
        Returns:
            新闻列表
        """
        url = f"{self.base_url}/top-headlines"
        params = {
            'apiKey': self.api_key,
            'pageSize': min(page_size, 100)
        }
        
        if category:
            params['category'] = category
        if country:
            params['country'] = country
        if q:
            params['q'] = q
        
        try:
            response = self.requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'ok':
                return data.get('articles', [])
            else:
                logger.error(f"NewsAPI 错误: {data.get('message', 'Unknown error')}")
                return []
                
        except Exception as e:
            logger.error(f"NewsAPI 请求失败: {e}")
            return []
    
    def search_everything(self,
                         q: str,
                         from_date: Optional[datetime] = None,
                         to_date: Optional[datetime] = None,
                         language: str = 'en',
                         sort_by: str = 'publishedAt',
                         page_size: int = 100) -> List[Dict]:
        """
        搜索所有新闻
        
        Args:
            q: 搜索关键词
            from_date: 开始日期
            to_date: 结束日期
            language: 语言 (ar, de, en, es, fr, he, it, nl, no, pt, ru, sv, ud, zh)
            sort_by: 排序方式 (relevancy, popularity, publishedAt)
            page_size: 返回结果数量
            
        Returns:
            新闻列表
        """
        url = f"{self.base_url}/everything"
        params = {
            'apiKey': self.api_key,
            'q': q,
            'language': language,
            'sortBy': sort_by,
            'pageSize': min(page_size, 100)
        }
        
        if from_date:
            params['from'] = from_date.strftime('%Y-%m-%d')
        if to_date:
            params['to'] = to_date.strftime('%Y-%m-%d')
        
        try:
            response = self.requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get('status') == 'ok':
                return data.get('articles', [])
            else:
                logger.error(f"NewsAPI 错误: {data.get('message', 'Unknown error')}")
                return []
                
        except Exception as e:
            logger.error(f"NewsAPI 请求失败: {e}")
            return []


class NewspaperIntegration:
    """Newspaper3k 集成"""
    
    def __init__(self, language: str = 'en'):
        """
        初始化 Newspaper3k
        
        Args:
            language: 语言代码
        """
        self.language = language
        
        try:
            from newspaper import Article, Source
            self.Article = Article
            self.Source = Source
        except ImportError:
            raise NewsScraperError("需要安装 newspaper3k 库: pip install newspaper3k")
    
    def fetch_from_source(self, url: str, max_articles: int = 50) -> List[Dict]:
        """
        从新闻源抓取文章
        
        Args:
            url: 新闻源 URL
            max_articles: 最多抓取文章数
            
        Returns:
            文章列表
        """
        articles = []
        try:
            logger.info(f"正在抓取: {url}")
            
            source = self.Source(url, language=self.language)
            source.build()
            
            article_urls = source.article_urls()[:max_articles]
            logger.info(f"发现 {len(article_urls)} 篇文章")
            
            for article_url in article_urls:
                try:
                    article = self.Article(article_url, language=self.language)
                    article.download()
                    article.parse()
                    
                    articles.append({
                        'title': article.title,
                        'url': article.url,
                        'source': url,
                        'publish_date': article.publish_date.strftime("%Y-%m-%d") if article.publish_date else "未知",
                        'description': article.text[:200] + '...' if article.text else ''
                    })
                    
                    time.sleep(0.5)
                except Exception as e:
                    logger.warning(f"抓取文章失败 {article_url}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"抓取新闻源失败 {url}: {e}")
        
        return articles


class DeepSeekSummarizer:
    """DeepSeek 大语言模型集成 - 用于生成新闻摘要"""
    
    def __init__(self, api_key: str, config: Optional[Dict] = None):
        """
        初始化 DeepSeek
        
        Args:
            api_key: DeepSeek API 密钥
            config: 摘要配置
        """
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com"
        self.config = config or {}
        
        try:
            from openai import OpenAI
            self.client = OpenAI(
                api_key=api_key,
                base_url=self.base_url
            )
            logger.info("✅ DeepSeek 客户端初始化成功")
        except ImportError:
            raise NewsScraperError("需要安装 openai 库: pip install openai")
        except Exception as e:
            raise NewsScraperError(f"DeepSeek 初始化失败: {e}")
    
    def generate_daily_summary(self, news_data: Dict[str, List[Dict]]) -> str:
        """
        生成当日新闻摘要
        
        Args:
            news_data: 分类后的新闻数据
            
        Returns:
            生成的摘要文本
        """
        # 准备新闻标题数据
        news_text = self._prepare_news_text(news_data)
        
        if not news_text.strip():
            logger.warning("没有新闻数据，跳过摘要生成")
            return ""
        
        # 构建提示词
        min_length = self.config.get('min_length', 300)
        max_length = self.config.get('max_length', 500)
        
        prompt = f"""请基于以下今日新闻标题，生成一段{min_length}-{max_length}字的中文摘要。

要求：
1. 摘要应具有整体感，能够提炼出当日新闻的主要趋势、关注焦点或舆论动向
2. 不要机械复述标题，要进行概括与串联，风格自然流畅
3. 分析各类新闻的内在联系和整体趋势
4. 语言专业但易懂，适合快速阅读

今日新闻标题：

{news_text}

请生成摘要："""
        
        try:
            logger.info("🤖 正在调用 DeepSeek 生成摘要...")
            
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system",
                        "content": "你是一位资深的新闻分析师和编辑，擅长从大量新闻中提炼关键信息，发现趋势和联系，用简洁专业的语言撰写导读摘要。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000,
                stream=False
            )
            
            summary = response.choices[0].message.content.strip()
            logger.info(f"✅ 摘要生成成功，长度: {len(summary)} 字")
            
            return summary
            
        except Exception as e:
            logger.error(f"DeepSeek 摘要生成失败: {e}")
            return ""
    
    def _prepare_news_text(self, news_data: Dict[str, List[Dict]]) -> str:
        """
        准备用于生成摘要的新闻文本
        
        Args:
            news_data: 分类后的新闻数据
            
        Returns:
            格式化的新闻文本
        """
        text_parts = []
        
        for category, articles in news_data.items():
            if not articles or category == "其他":
                continue
            
            text_parts.append(f"\n【{category}类】({len(articles)}篇)")
            
            # 每个分类最多取前10条
            for idx, article in enumerate(articles[:10], 1):
                title = article.get('title', '').strip()
                if title:
                    text_parts.append(f"{idx}. {title}")
        
        return '\n'.join(text_parts)


class HybridNewsScraper:
    """混合新闻抓取器 - 支持 NewsAPI 和 Newspaper3k"""
    
    def __init__(self, config_path: str = "config.json"):
        """
        初始化混合新闻抓取器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = Path(config_path)
        self.config = self._load_config()
        
        # 基础配置
        self.keywords = self.config.get("keywords", {})
        self.language = self.config.get("language", "zh")
        
        # NewsAPI 配置
        self.use_newsapi = self.config.get("use_newsapi", False)
        self.newsapi_key = self.config.get("newsapi_key", "")
        self.newsapi = None
        
        if self.use_newsapi and self.newsapi_key:
            try:
                self.newsapi = NewsAPIIntegration(self.newsapi_key)
                logger.info("✅ NewsAPI 已启用")
            except Exception as e:
                logger.warning(f"NewsAPI 初始化失败: {e}")
                self.use_newsapi = False
        
        # Newspaper3k 配置
        self.use_newspaper = self.config.get("use_newspaper", True)
        self.news_sources = self.config.get("news_sources", {})
        self.max_articles = self.config.get("max_articles", 50)
        self.newspaper = None
        
        if self.use_newspaper:
            try:
                self.newspaper = NewspaperIntegration(self.language)
                logger.info("✅ Newspaper3k 已启用")
            except Exception as e:
                logger.warning(f"Newspaper3k 初始化失败: {e}")
                self.use_newspaper = False
        
        # DeepSeek 配置
        self.use_deepseek = self.config.get("use_deepseek_summary", False)
        self.deepseek_api_key = self.config.get("deepseek_api_key", "")
        self.deepseek = None
        
        if self.use_deepseek and self.deepseek_api_key:
            try:
                deepseek_config = self.config.get("deepseek_summary_config", {})
                self.deepseek = DeepSeekSummarizer(self.deepseek_api_key, deepseek_config)
                logger.info("✅ DeepSeek 摘要已启用")
            except Exception as e:
                logger.warning(f"DeepSeek 初始化失败: {e}")
                self.use_deepseek = False
    
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
        """检查文本是否包含指定分类的关键词"""
        if not text or category not in self.keywords:
            return False
        
        text_lower = text.lower()
        keywords = self.keywords[category]
        
        for keyword in keywords:
            if keyword.lower() in text_lower:
                return True
        return False
    
    def _categorize_article(self, article: Dict) -> str:
        """
        为文章分类
        
        Args:
            article: 文章信息
            
        Returns:
            分类名称
        """
        title = article.get('title', '')
        description = article.get('description', '')
        text = f"{title} {description}"
        
        for category in self.keywords.keys():
            if self._match_keywords(text, category):
                return category
        
        return "其他"
    
    def scrape_from_newsapi(self) -> List[Dict]:
        """从 NewsAPI 抓取新闻"""
        if not self.newsapi:
            return []
        
        all_articles = []
        newsapi_config = self.config.get("newsapi_config", {})
        
        # 获取头条新闻
        if newsapi_config.get("fetch_top_headlines", True):
            logger.info("\n📰 从 NewsAPI 获取头条新闻...")
            
            countries = newsapi_config.get("countries", ["us"])
            categories = newsapi_config.get("categories", ["technology", "business", "science"])
            
            for country in countries:
                for category in categories:
                    logger.info(f"  获取 {country} - {category}")
                    articles = self.newsapi.get_top_headlines(
                        category=category,
                        country=country,
                        page_size=self.max_articles
                    )
                    
                    for article in articles:
                        all_articles.append({
                            'title': article.get('title', ''),
                            'url': article.get('url', ''),
                            'source': article.get('source', {}).get('name', 'NewsAPI'),
                            'region': f"NewsAPI-{country}",
                            'publish_date': article.get('publishedAt', '')[:10] if article.get('publishedAt') else '未知',
                            'description': article.get('description', '')
                        })
                    
                    time.sleep(0.5)
        
        # 按关键词搜索
        if newsapi_config.get("search_by_keywords", True):
            logger.info("\n🔍 从 NewsAPI 按关键词搜索...")
            
            from_date = datetime.now() - timedelta(days=newsapi_config.get("days_back", 7))
            language = newsapi_config.get("search_language", "en")
            
            for category, keywords in self.keywords.items():
                # 取前3个关键词搜索
                search_keywords = keywords[:3]
                for keyword in search_keywords:
                    logger.info(f"  搜索: {keyword}")
                    articles = self.newsapi.search_everything(
                        q=keyword,
                        from_date=from_date,
                        language=language,
                        page_size=20
                    )
                    
                    for article in articles:
                        all_articles.append({
                            'title': article.get('title', ''),
                            'url': article.get('url', ''),
                            'source': article.get('source', {}).get('name', 'NewsAPI'),
                            'region': f"NewsAPI-搜索",
                            'publish_date': article.get('publishedAt', '')[:10] if article.get('publishedAt') else '未知',
                            'description': article.get('description', '')
                        })
                    
                    time.sleep(0.5)
        
        logger.info(f"✅ NewsAPI 共获取 {len(all_articles)} 篇文章")
        return all_articles
    
    def scrape_from_newspaper(self) -> List[Dict]:
        """从 Newspaper3k 抓取新闻"""
        if not self.newspaper:
            return []
        
        all_articles = []
        
        logger.info("\n📰 使用 Newspaper3k 抓取新闻源...")
        
        for region, sources in self.news_sources.items():
            logger.info(f"\n开始抓取【{region}】新闻源")
            
            for source_url in sources:
                articles = self.newspaper.fetch_from_source(source_url, self.max_articles)
                
                for article in articles:
                    article['region'] = region
                    all_articles.append(article)
        
        logger.info(f"✅ Newspaper3k 共获取 {len(all_articles)} 篇文章")
        return all_articles
    
    def scrape_news(self) -> Dict[str, List[Dict]]:
        """
        抓取所有新闻源的新闻
        
        Returns:
            按分类组织的新闻字典
        """
        all_articles = []
        
        # 从 NewsAPI 抓取
        if self.use_newsapi:
            all_articles.extend(self.scrape_from_newsapi())
        
        # 从 Newspaper3k 抓取
        if self.use_newspaper:
            all_articles.extend(self.scrape_from_newspaper())
        
        # 去重（基于 URL）
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            url = article.get('url', '')
            if url and url not in seen_urls:
                seen_urls.add(url)
                unique_articles.append(article)
        
        logger.info(f"\n📊 去重后共 {len(unique_articles)} 篇文章")
        
        # 分类
        categorized_news = {category: [] for category in self.keywords.keys()}
        categorized_news["其他"] = []
        
        for article in unique_articles:
            category = self._categorize_article(article)
            categorized_news[category].append(article)
        
        return categorized_news
    
    def generate_markdown_report(self, news_data: Dict[str, List[Dict]], output_dir: str = "output") -> str:
        """生成 Markdown 格式的日报"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        today = datetime.now().strftime("%Y-%m-%d")
        filename = f"news_daily_report_{today}.md"
        filepath = output_path / filename
        
        content = []
        content.append(f"# 新闻日报 - {today}\n")
        content.append(f"> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # 数据源说明
        sources_used = []
        if self.use_newsapi:
            sources_used.append("NewsAPI")
        if self.use_newspaper:
            sources_used.append("Newspaper3k")
        if self.use_deepseek:
            sources_used.append("DeepSeek AI 摘要")
        content.append(f"> 数据源: {', '.join(sources_used)}\n")
        content.append("---\n")
        
        # AI 生成的今日导览摘要
        if self.use_deepseek and self.deepseek:
            logger.info("\n🤖 生成 AI 摘要...")
            summary = self.deepseek.generate_daily_summary(news_data)
            
            if summary:
                content.append("\n## 🌟 今日导览摘要\n\n")
                content.append("> *由 DeepSeek AI 根据当日新闻自动生成*\n\n")
                content.append(f"{summary}\n\n")
                content.append("---\n")
        
        # 统计信息
        total_articles = sum(len(articles) for articles in news_data.values())
        content.append(f"\n## 📊 统计概览\n")
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
                content.append(f"- **发布日期**: {article['publish_date']}\n")
                
                if article.get('description'):
                    content.append(f"- **摘要**: {article['description'][:150]}...\n")
                
                content.append("\n")
        
        # 页脚
        content.append("\n---\n")
        content.append(f"*报告由新闻抓取工具自动生成*\n")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(''.join(content))
        
        logger.info(f"日报已生成: {filepath}")
        return str(filepath)
    
    def run(self, output_dir: str = "output") -> str:
        """运行新闻抓取并生成报告"""
        logger.info("=" * 60)
        logger.info("开始抓取新闻...")
        logger.info("=" * 60)
        
        start_time = time.time()
        
        news_data = self.scrape_news()
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
        scraper = HybridNewsScraper("config.json")
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
