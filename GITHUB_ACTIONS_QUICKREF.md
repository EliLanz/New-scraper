# 🚀 GitHub Actions 快速参考

## ⚡ 3 分钟快速开始

### 1️⃣ 上传代码到 GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/你的用户名/news-scraper.git
git push -u origin main
```

### 2️⃣ 配置 4 个 Secrets
访问: `Settings` → `Secrets and variables` → `Actions` → `New repository secret`

| Secret Name | 值示例 | 说明 |
|-------------|--------|------|
| `SENDER_EMAIL` | `your@qq.com` | 发件邮箱 |
| `SENDER_PASSWORD` | `abcd1234efgh` | 邮箱授权码 |
| `RECIPIENTS` | `["user@example.com"]` | 收件人（JSON数组） |
| `SMTP_TYPE` | `qq` | 邮箱类型 |

### 3️⃣ 测试运行
`Actions` → 选择 workflow → `Run workflow`

---

## 📅 定时时间配置

| 北京时间 | Cron 表达式 | 说明 |
|---------|------------|------|
| 06:00 | `'0 22 * * *'` | 早上 6 点 |
| 07:00 | `'0 23 * * *'` | 早上 7 点 |
| 08:00 | `'0 0 * * *'` | 早上 8 点 ⭐推荐 |
| 09:00 | `'0 1 * * *'` | 早上 9 点 |
| 12:00 | `'0 4 * * *'` | 中午 12 点 |
| 18:00 | `'0 10 * * *'` | 晚上 6 点 |

**公式**: UTC时间 = 北京时间 - 8

---

## 🔧 常用操作

### 修改执行时间
编辑 `.github/workflows/daily-news.yml`:
```yaml
schedule:
  - cron: '0 1 * * *'  # 改为早上 9:00
```

### 手动触发
`Actions` → 选择 workflow → `Run workflow`

### 查看日志
`Actions` → 点击运行记录 → 展开步骤

### 下载报告
运行记录底部 → `Artifacts` → 下载

### 禁用自动运行
`Actions` → 选择 workflow → `...` → `Disable workflow`

---

## 📁 项目文件结构

```
news-scraper/
├── .github/workflows/
│   ├── daily-news.yml          ← GitHub Actions 配置
│   └── daily-news-simple.yml
├── news_scraper_hybrid.py      ← 新闻抓取
├── email_sender.py             ← 邮件发送
├── daily_news_task.py          ← 主任务
├── config.json
├── requirements.txt
└── .gitignore                  ← 不要提交敏感文件
```

---

## ❓ 故障排除

### 问题 1: Secrets 未定义
**错误**: `The SENDER_EMAIL variable is not set`
**解决**: 检查 Secrets 配置，确保所有 4 个都已添加

### 问题 2: RECIPIENTS 格式错误
**错误**: `JSONDecodeError`
**解决**: 确保格式为 `["email@example.com"]`，包含方括号和引号

### 问题 3: 邮件发送失败
**错误**: `SMTP Authentication Error`
**解决**: 
- 确认使用授权码（不是登录密码）
- 检查 QQ 邮箱是否开启 SMTP 服务

### 问题 4: 依赖安装失败
**错误**: `Could not find a version`
**解决**: 检查 `requirements.txt` 是否存在且格式正确

---

## 💡 高级技巧

### 多时段执行
```yaml
schedule:
  - cron: '0 0 * * *'   # 8:00
  - cron: '0 4 * * *'   # 12:00
  - cron: '0 10 * * *'  # 18:00
```

### 仅工作日执行
```yaml
schedule:
  - cron: '0 0 * * 1-5'  # 周一到周五
```

### 添加多个收件人
Secrets → `RECIPIENTS`:
```json
["user1@qq.com", "user2@gmail.com", "user3@outlook.com"]
```

---

## 🎯 检查清单

部署前确认:
- [ ] 代码已推送到 GitHub
- [ ] 4 个 Secrets 已配置
- [ ] RECIPIENTS 格式正确（JSON数组）
- [ ] `.github/workflows/daily-news.yml` 存在
- [ ] Actions 已启用
- [ ] 手动测试运行成功
- [ ] 邮件发送成功

---

## 🔗 有用链接

- **Cron 表达式工具**: https://crontab.guru/
- **GitHub Actions 文档**: https://docs.github.com/actions
- **项目详细指南**: `GITHUB_ACTIONS_GUIDE.md`

---

## 📞 快速命令

```bash
# 部署到 GitHub
./deploy_to_github.sh

# 本地测试
python daily_news_task.py

# 查看 Git 状态
git status

# 推送更新
git add .
git commit -m "Update"
git push
```

---

**提示**: 首次使用建议先手动触发测试，确认成功后再等待定时执行！

**费用**: 公开仓库完全免费 ✅
