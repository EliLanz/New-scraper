
echo "步骤 2: 配置邮件发送"
echo "========================================="
echo ""

if [ ! -f "email_config.json" ]; then
    echo "未找到邮件配置文件，创建新配置..."
    cp email_config.json.example email_config.json 2>/dev/null || true
fi

echo "请编辑 email_config.json 文件，配置以下信息："
echo "  1. sender_email: 发件人邮箱地址"
echo "  2. sender_password: 邮箱授权码（不是登录密码！）"
echo "  3. recipients: 收件人列表"
echo "  4. smtp_type: 邮箱类型 (qq/gmail/163/outlook)"
echo ""

read -p "是否现在配置邮件? (y/n): " configure_email

if [ "$configure_email" = "y" ] || [ "$configure_email" = "Y" ]; then
    # 使用默认编辑器打开配置文件
    ${EDITOR:-nano} email_config.json
    
    echo ""
    echo "配置完成，正在测试邮件发送..."
    echo ""
    
    # 测试邮件配置
    python3 email_sender.py
else
    echo "⚠️  跳过邮件配置，请稍后手动编辑 email_config.json"
fi

echo ""

# 配置定时任务
echo "========================================="
echo "步骤 3: 配置定时任务"
echo "========================================="
echo ""

if [ ! -f "cron_config.json" ]; then
    echo "未找到定时任务配置文件，创建默认配置..."
    cat > cron_config.json << EOF
{
  "enabled": true,
  "schedule": {
    "hour": 8,
    "minute": 0
  },
  "task_comment": "Daily News Scraper Task"
}
EOF
fi

echo "当前定时任务配置:"
cat cron_config.json | grep -E "(hour|minute)" | head -2
echo ""

read -p "是否修改执行时间? (y/n): " modify_schedule

if [ "$modify_schedule" = "y" ] || [ "$modify_schedule" = "Y" ]; then
    read -p "请输入小时 (0-23): " hour
    read -p "请输入分钟 (0-59): " minute
    
    cat > cron_config.json << EOF
{
  "enabled": true,
  "schedule": {
    "hour": $hour,
    "minute": $minute
  },
  "task_comment": "Daily News Scraper Task"
}
EOF
    
    echo "✅ 定时任务配置已更新"
fi

echo ""

# 添加定时任务
echo "========================================="
echo "步骤 4: 添加定时任务"
echo "========================================="
echo ""

read -p "是否现在添加定时任务到 crontab? (y/n): " add_cron

if [ "$add_cron" = "y" ] || [ "$add_cron" = "Y" ]; then
    python3 cron_manager.py add --force
    
    echo ""
    echo "查看已添加的任务:"
    python3 cron_manager.py list
else
    echo "⚠️  跳过定时任务添加，可以稍后运行: python3 cron_manager.py add"
fi

echo ""

# 测试任务
echo "========================================="
echo "步骤 5: 测试完整流程"
echo "========================================="
echo ""

read -p "是否立即运行一次测试? (y/n): " run_test

if [ "$run_test" = "y" ] || [ "$run_test" = "Y" ]; then
    echo ""
    echo "开始执行测试..."
    echo ""
    python3 daily_news_task.py
    
    echo ""
    echo "✅ 测试完成!"
else
    echo "⚠️  跳过测试，可以稍后运行: python3 daily_news_task.py"
fi

echo ""

# 完成
echo "========================================"
echo "  ✅ 设置完成！"
echo "========================================"
echo ""
echo "下一步："
echo "  1. 如果还未配置邮件，请编辑: email_config.json"
echo "  2. 如果还未添加定时任务，运行: python3 cron_manager.py add"
echo "  3. 查看定时任务列表: python3 cron_manager.py list"
echo "  4. 手动测试执行: python3 daily_news_task.py"
echo "  5. 查看日志: tail -f logs/cron_task.log"
echo ""
echo "详细文档: SCHEDULE_EMAIL_GUIDE.md"
echo ""
