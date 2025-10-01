# 更新日志 (Changelog)

所有重要的项目变更都将记录在此文件中。

---

## [1.0.1] - 2025-10-01

### 🔧 修复 (Fixed)
- **GitHub Actions 弃用警告**: 升级 `actions/upload-artifact` 从 v3 到 v4
  - 背景: GitHub 宣布 v3 版本已弃用，使用 v3 会导致工作流失败
  - 影响文件: `.github/workflows/daily-news.yml`, `.github/workflows/daily-news-simple.yml`

### ⬆️ 升级 (Updated)
- `actions/checkout`: v3 → v4
- `actions/setup-python`: v4 → v5
- `actions/upload-artifact`: v3 → v4

### 📝 说明
此次更新确保 GitHub Actions 工作流能够长期稳定运行，不会因为使用已弃用的 action 版本而失败。

**升级建议**: 
如果您已经部署了旧版本，请拉取最新代码：
```bash
git pull origin main
```

---

## [1.0.0] - 2025-10-01

### 🎉 新功能 (Added)
- ✅ GitHub Actions 自动化工作流
  - 定时任务（每天早上 8:00）
  - 手动触发支持
  - 完整版和简化版两个 workflow
  
- ✅ 邮件发送功能
  - 支持 QQ、Gmail、163、Outlook 邮箱
  - HTML 格式邮件
  - 多收件人支持
  
- ✅ 新闻抓取功能
  - NewsAPI 集成
  - 混合抓取模式
  - Markdown 报告生成
  
- ✅ 本地定时任务
  - Python Crontab 管理
  - 自动化任务调度

### 📚 文档 (Documentation)
- `GITHUB_ACTIONS_GUIDE.md` - 完整部署指南（600+ 行）
- `GITHUB_ACTIONS_QUICKREF.md` - 快速参考卡片
- `README.md` - 项目说明
- `QUICKSTART.md` - 快速开始指南
- `NEWSAPI_GUIDE.md` - NewsAPI 使用指南
- `VERSION_COMPARISON.md` - 版本对比

### 🔧 工具 (Tools)
- `deploy_to_github.sh` - 一键部署脚本
- `run.sh` - 本地运行脚本
- `run_newsapi.sh` - NewsAPI 测试脚本

### 🔒 安全 (Security)
- `.gitignore` - 保护敏感配置文件
- GitHub Secrets 集成
- 邮箱授权码加密存储

---

## 版本规范

本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/) 规范：

- **主版本号 (Major)**: 不兼容的 API 修改
- **次版本号 (Minor)**: 向下兼容的功能性新增
- **修订号 (Patch)**: 向下兼容的问题修正

---

## 获取更新

### 方法 1: Git 拉取（推荐）
```bash
cd /tmp/news_scraper
git pull origin main
```

### 方法 2: 查看 GitHub Releases
访问: https://github.com/你的用户名/news-scraper/releases

---

**维护者**: GitHub Copilot  
**项目**: 新闻抓取与邮件发送自动化系统
