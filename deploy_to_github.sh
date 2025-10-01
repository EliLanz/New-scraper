#!/bin/bash
# GitHub Actions 快速部署脚本

set -e

echo "========================================"
echo "  GitHub Actions 快速部署向导"
echo "========================================"
echo ""

# 检查 Git
if ! command -v git &> /dev/null; then
    echo "❌ 错误: 未安装 Git"
    echo "请先安装 Git: https://git-scm.com/downloads"
    exit 1
fi

echo "✅ Git 已安装: $(git --version)"
echo ""

# 步骤 1: 初始化 Git 仓库
echo "========================================="
echo "步骤 1: 初始化 Git 仓库"
echo "========================================="
echo ""

if [ -d ".git" ]; then
    echo "⚠️  Git 仓库已存在"
else
    git init
    echo "✅ Git 仓库初始化完成"
fi

# 创建 .gitignore
if [ ! -f ".gitignore" ]; then
    echo "⚠️  .gitignore 文件不存在，已自动创建"
fi

echo ""

# 步骤 2: 配置 Git 用户信息
echo "========================================="
echo "步骤 2: 配置 Git 用户信息"
echo "========================================="
echo ""

read -p "请输入您的 GitHub 用户名: " github_username
read -p "请输入您的 GitHub 邮箱: " github_email

git config user.name "$github_username"
git config user.email "$github_email"

echo "✅ Git 用户信息配置完成"
echo ""

# 步骤 3: 添加远程仓库
echo "========================================="
echo "步骤 3: 配置远程仓库"
echo "========================================="
echo ""

read -p "请输入您的 GitHub 仓库名称 (例如: news-scraper): " repo_name

remote_url="https://github.com/$github_username/$repo_name.git"

if git remote | grep -q "origin"; then
    echo "⚠️  远程仓库 origin 已存在"
    read -p "是否更新为新的地址? (y/n): " update_remote
    if [ "$update_remote" = "y" ]; then
        git remote set-url origin "$remote_url"
        echo "✅ 远程仓库地址已更新"
    fi
else
    git remote add origin "$remote_url"
    echo "✅ 远程仓库已添加: $remote_url"
fi

echo ""

# 步骤 4: 提交代码
echo "========================================="
echo "步骤 4: 提交代码"
echo "========================================="
echo ""

git add .
git status

echo ""
read -p "确认提交所有文件? (y/n): " confirm_commit

if [ "$confirm_commit" = "y" ]; then
    git commit -m "Initial commit: 新闻抓取自动化项目"
    echo "✅ 代码提交完成"
else
    echo "⚠️  跳过提交步骤"
fi

echo ""

# 步骤 5: 推送到 GitHub
echo "========================================="
echo "步骤 5: 推送到 GitHub"
echo "========================================="
echo ""

echo "提示: 确保您已在 GitHub 上创建了仓库"
echo "      仓库地址: https://github.com/$github_username/$repo_name"
echo ""

read -p "是否现在推送代码到 GitHub? (y/n): " confirm_push

if [ "$confirm_push" = "y" ]; then
    git branch -M main
    git push -u origin main
    echo "✅ 代码推送成功!"
else
    echo "⚠️  跳过推送步骤"
    echo "   稍后可以手动执行: git push -u origin main"
fi

echo ""

# 步骤 6: 配置 Secrets 提醒
echo "========================================="
echo "步骤 6: 配置 GitHub Secrets (重要!)"
echo "========================================="
echo ""

echo "现在需要在 GitHub 仓库中配置 Secrets："
echo ""
echo "1. 访问: https://github.com/$github_username/$repo_name/settings/secrets/actions"
echo ""
echo "2. 点击 'New repository secret' 添加以下 4 个 secrets："
echo ""
echo "   ┌─────────────────────────────────────────────────┐"
echo "   │ Secret 1: SENDER_EMAIL                          │"
echo "   │ Value: 您的发件邮箱地址                          │"
echo "   │ 例如: your_email@qq.com                         │"
echo "   └─────────────────────────────────────────────────┘"
echo ""
echo "   ┌─────────────────────────────────────────────────┐"
echo "   │ Secret 2: SENDER_PASSWORD                       │"
echo "   │ Value: 邮箱授权码（不是登录密码！）              │"
echo "   │ 例如: abcd1234efgh5678                          │"
echo "   └─────────────────────────────────────────────────┘"
echo ""
echo "   ┌─────────────────────────────────────────────────┐"
echo "   │ Secret 3: RECIPIENTS                            │"
echo "   │ Value: JSON 数组格式的收件人列表                 │"
echo "   │ 例如: [\"user@example.com\"]                      │"
echo "   │ 多个收件人: [\"user1@a.com\", \"user2@b.com\"]    │"
echo "   └─────────────────────────────────────────────────┘"
echo ""
echo "   ┌─────────────────────────────────────────────────┐"
echo "   │ Secret 4: SMTP_TYPE                             │"
echo "   │ Value: 邮箱类型                                  │"
echo "   │ 可选: qq, gmail, 163, outlook                   │"
echo "   └─────────────────────────────────────────────────┘"
echo ""

read -p "按回车键继续..."

echo ""

# 步骤 7: 测试运行
echo "========================================="
echo "步骤 7: 测试 GitHub Actions"
echo "========================================="
echo ""

echo "配置完 Secrets 后："
echo ""
echo "1. 访问: https://github.com/$github_username/$repo_name/actions"
echo ""
echo "2. 选择 'Daily News Scraper' workflow"
echo ""
echo "3. 点击 'Run workflow' 按钮进行测试"
echo ""
echo "4. 查看运行日志，确认是否成功"
echo ""

# 完成
echo "========================================="
echo "  🎉 部署向导完成！"
echo "========================================="
echo ""
echo "下一步:"
echo "  1. 在 GitHub 上配置 4 个 Secrets"
echo "  2. 手动触发 workflow 进行测试"
echo "  3. 确认邮件发送成功"
echo "  4. 等待每天自动执行（北京时间 8:00）"
echo ""
echo "详细文档:"
echo "  - GitHub Actions 指南: GITHUB_ACTIONS_GUIDE.md"
echo "  - 项目说明: README.md"
echo ""
echo "如有问题，请查看文档或检查 Actions 日志"
echo ""
