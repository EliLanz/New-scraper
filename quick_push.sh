#!/bin/bash
# Git 推送快速脚本
# 用法: ./quick_push.sh "你的提交信息"

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Git 快速推送工具${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 1. 检查 Git 状态
echo -e "${YELLOW}步骤 1/3: 检查文件变更...${NC}"
git status --short
echo ""

# 2. 添加所有修改的文件
echo -e "${YELLOW}步骤 2/3: 添加文件到暂存区...${NC}"
git add .
echo -e "${GREEN}✓ 已添加所有文件${NC}"
echo ""

# 3. 提交
echo -e "${YELLOW}步骤 3/3: 提交并推送...${NC}"
if [ -z "$1" ]; then
    # 如果没有提供提交信息，使用默认信息
    COMMIT_MSG="更新代码 - $(date '+%Y-%m-%d %H:%M:%S')"
    echo -e "${YELLOW}未提供提交信息，使用默认信息${NC}"
else
    COMMIT_MSG="$1"
fi

echo "提交信息: $COMMIT_MSG"
git commit -m "$COMMIT_MSG"

# 4. 推送到 GitHub
echo ""
echo -e "${YELLOW}推送到 GitHub...${NC}"
git push origin main

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}✓ 成功推送到 GitHub!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "查看更新: https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:/]\(.*\)\.git/\1/')"
else
    echo ""
    echo -e "${YELLOW}推送失败，请检查错误信息${NC}"
    exit 1
fi
