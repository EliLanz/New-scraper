#!/bin/bash
# NewsAPI 版本运行脚本

echo "📰 新闻日报生成器 - NewsAPI 集成版"
echo "====================================="
echo ""

# 检查配置文件
if [ ! -f "config.json" ]; then
    echo "⚠️  未找到 config.json，使用 NewsAPI 配置模板..."
    if [ -f "config_newsapi.json" ]; then
        cp config_newsapi.json config.json
        echo "✅ 已创建 config.json"
        echo ""
        echo "⚠️  请编辑 config.json 并填入你的 NewsAPI Key:"
        echo "   nano config.json"
        echo ""
        echo "获取 API Key:"
        echo "   1. 访问 https://newsapi.org/register"
        echo "   2. 注册并获取免费 API Key"
        echo "   3. 将 API Key 填入 config.json"
        exit 1
    else
        echo "❌ 未找到配置文件"
        exit 1
    fi
fi

# 测试 NewsAPI 配置
echo "🔍 测试 NewsAPI 配置..."
conda run -n ML python test_newsapi.py

if [ $? -eq 0 ]; then
    echo ""
    echo "🚀 开始抓取新闻..."
    echo ""
    conda run -n ML python news_scraper_hybrid.py
    echo ""
    echo "✅ 完成!"
else
    echo ""
    echo "❌ NewsAPI 测试失败，请检查配置"
    exit 1
fi
