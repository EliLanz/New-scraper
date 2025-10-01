#!/bin/bash
# 新闻抓取器运行脚本 - 在 ML 虚拟环境中运行

echo "📰 新闻日报生成器"
echo "=================="
echo "使用 Conda ML 虚拟环境"
echo ""

# 检查 conda 是否可用
if ! command -v conda &> /dev/null; then
    echo "❌ 错误: 未找到 conda"
    echo "请确保已安装 Anaconda 或 Miniconda"
    exit 1
fi

# 检查 ML 环境是否存在
if ! conda env list | grep -q "^ML "; then
    echo "❌ 错误: 未找到 ML 虚拟环境"
    echo "请使用以下命令创建环境:"
    echo "  conda create -n ML python=3.12"
    exit 1
fi

# 检查依赖是否安装
echo "🔍 检查依赖..."
conda run -n ML python -c "import newspaper" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  检测到依赖未安装，正在安装..."
    conda run -n ML pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ 依赖安装失败"
        exit 1
    fi
    echo "✅ 依赖安装完成"
fi

# 下载 NLTK 数据（如果需要）
echo "🔍 检查 NLTK 数据..."
conda run -n ML python -c "import nltk; nltk.download('punkt', quiet=True)" 2>/dev/null

# 运行程序
echo ""
echo "🚀 开始抓取新闻..."
echo ""
conda run -n ML python news_scraper.py

echo ""
echo "✅ 完成!"
