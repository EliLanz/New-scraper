# 📤 如何推送代码到 GitHub

## 🚀 方法 1: 使用快速推送脚本（推荐）

我已经为你创建了一键推送脚本！

### 使用方法：

```bash
# 方法 A: 使用自定义提交信息
./quick_push.sh "修改了新闻抓取配置"

# 方法 B: 使用默认提交信息（包含时间戳）
./quick_push.sh
```

**优点**：
- ✅ 一条命令完成所有操作
- ✅ 自动检查文件状态
- ✅ 彩色输出，清晰易读
- ✅ 自动生成时间戳
- ✅ 显示 GitHub 链接

---

## 📝 方法 2: 标准 Git 命令（3步）

### 步骤 1: 查看修改了哪些文件

```bash
git status
```

**输出示例**：
```
Changes not staged for commit:
  modified:   config.json
  modified:   email_sender.py
```

### 步骤 2: 添加文件到暂存区

```bash
# 添加所有修改的文件
git add .

# 或者只添加特定文件
git add config.json
git add email_sender.py
```

### 步骤 3A: 提交更改

```bash
git commit -m "修改了新闻抓取配置"
```

**提交信息建议**：
- ✅ 好的示例：
  - `"修复: 邮件发送失败问题"`
  - `"新增: 支持多个新闻源"`
  - `"更新: 调整抓取时间为早上7点"`
  - `"优化: 改进错误处理逻辑"`

- ❌ 不好的示例：
  - `"update"` (太简略)
  - `"修改"` (没说明修改了什么)
  - `"aaa"` (无意义)

### 步骤 3B: 推送到 GitHub

```bash
git push origin main
```

**完整示例**：
```bash
cd /tmp/news_scraper
git status                          # 查看状态
git add .                           # 添加所有文件
git commit -m "更新新闻源配置"       # 提交
git push origin main                # 推送
```

---

## 🔄 常见场景

### 场景 1: 修改了单个配置文件

```bash
# 查看修改
git diff config.json

# 推送
./quick_push.sh "更新新闻抓取配置"
```

### 场景 2: 修改了多个 Python 文件

```bash
# 查看所有修改
git status

# 推送
./quick_push.sh "优化新闻抓取和邮件发送逻辑"
```

### 场景 3: 添加了新文件

```bash
# 查看新文件
git status

# 推送（会自动包含新文件）
./quick_push.sh "新增测试脚本"
```

### 场景 4: 删除了文件

```bash
# 删除文件
rm old_script.py

# Git 会自动检测删除，直接推送
./quick_push.sh "删除旧的测试脚本"
```

---

## 🛠️ 高级技巧

### 查看详细修改内容

```bash
# 查看所有文件的详细修改
git diff

# 查看特定文件的修改
git diff config.json

# 查看已暂存的修改
git diff --staged
```

### 撤销修改（推送前）

```bash
# 撤销所有未提交的修改
git checkout .

# 撤销特定文件的修改
git checkout config.json

# 从暂存区移除文件（但保留修改）
git reset HEAD config.json
```

### 修改最后一次提交信息

```bash
# 如果还没 push
git commit --amend -m "新的提交信息"

# 如果已经 push，需要强制推送（谨慎使用）
git push origin main --force
```

### 查看提交历史

```bash
# 查看最近 5 次提交
git log --oneline -5

# 查看详细提交历史
git log --pretty=format:"%h - %an, %ar : %s"
```

---

## ⚠️ 常见问题

### 问题 1: 推送被拒绝

**错误信息**：
```
! [rejected] main -> main (fetch first)
```

**解决方法**：
```bash
# 先拉取远程更新
git pull origin main

# 如果有冲突，手动解决后再推送
git push origin main
```

### 问题 2: 有文件冲突

**错误信息**：
```
CONFLICT (content): Merge conflict in config.json
```

**解决方法**：
```bash
# 1. 打开冲突文件，手动编辑解决冲突
code config.json

# 2. 冲突标记格式：
# <<<<<<< HEAD
# 你的修改
# =======
# 远程的修改
# >>>>>>> origin/main

# 3. 删除标记，保留正确的内容

# 4. 标记冲突已解决
git add config.json

# 5. 完成合并
git commit -m "解决配置文件冲突"

# 6. 推送
git push origin main
```

### 问题 3: 提交了敏感信息

**如果包含密码、密钥等敏感信息**：

```bash
# ⚠️ 紧急！从历史中移除敏感文件
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch email_config.json" \
  --prune-empty --tag-name-filter cat -- --all

# 强制推送（会重写历史）
git push origin main --force

# ✅ 然后将文件添加到 .gitignore
echo "email_config.json" >> .gitignore
git add .gitignore
git commit -m "添加敏感文件到 gitignore"
git push
```

---

## 📋 快速命令速查表

| 操作 | 命令 |
|------|------|
| 查看状态 | `git status` |
| 查看修改 | `git diff` |
| 添加所有文件 | `git add .` |
| 添加特定文件 | `git add 文件名` |
| 提交 | `git commit -m "信息"` |
| 推送 | `git push origin main` |
| 拉取更新 | `git pull origin main` |
| 查看历史 | `git log --oneline` |
| 撤销修改 | `git checkout .` |
| 一键推送 | `./quick_push.sh "信息"` |

---

## 🎯 最佳实践

### ✅ 推荐做法

1. **频繁提交**：每完成一个小功能就提交
2. **清晰的提交信息**：说明做了什么修改
3. **推送前测试**：确保代码能正常运行
4. **使用 .gitignore**：不要提交敏感信息
5. **定期推送**：避免本地积累太多未推送的修改

### 📝 提交信息规范（可选）

```bash
# 格式：<类型>: <描述>

# 常用类型：
git commit -m "修复: 解决邮件发送失败问题"
git commit -m "新增: 添加多新闻源支持"
git commit -m "更新: 调整抓取时间配置"
git commit -m "优化: 改进错误处理"
git commit -m "文档: 更新 README 说明"
git commit -m "重构: 简化邮件发送逻辑"
```

---

## 🔗 相关链接

- **你的仓库**: https://github.com/EliLanz/New-scraper
- **Git 官方文档**: https://git-scm.com/doc
- **GitHub 使用指南**: https://docs.github.com/cn

---

## 💡 温馨提示

- 🔒 **永远不要提交敏感信息**（密码、密钥、token）
- 📝 **使用 .gitignore** 保护配置文件
- ✅ **推送前检查** `git status` 确认要提交的文件
- 🔄 **养成习惯**：修改 → 测试 → 提交 → 推送

---

**当前工作目录**: `/tmp/news_scraper`  
**远程仓库**: `EliLanz/New-scraper`  
**分支**: `main`
