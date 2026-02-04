"""
测试发送邮件功能
"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 从环境变量读取
email_username = os.getenv("EMAIL_163_USERNAME", "15302814198@163.com")
email_password = os.getenv("EMAIL_163_PASSWORD", "JSewF34VrE5GGNwQ")

print("=" * 60)
print("测试发送邮件")
print("=" * 60)

print(f"\n发件人: {email_username}")
print(f"收件人: {email_username}")

try:
    # 创建邮件
    msg = MIMEMultipart()
    msg['From'] = email_username
    msg['To'] = email_username
    msg['Subject'] = "📊 测试邮件 - 每日复盘提醒"
    
    content = """每日复盘

🌙 晚上好！今天的任务完成情况如何？

📋 今日任务清单：

🔄 用户登录功能
   进度：[■■■■■■■■□□] 80%
   象限: Q1

💬 请回复以下内容：
1. 今天完成了哪些任务？进度如何？
2. 明天计划做什么？
3. 有哪些任务需要暂缓？

示例：完成了用户登录功能80%，明天做数据库设计Q2任务

---
请直接回复此邮件更新任务进度
"""
    
    msg.attach(MIMEText(content, 'plain', 'utf-8'))
    
    # 连接到 SMTP 服务器
    print("\n连接到 163 SMTP 服务器...")
    server = smtplib.SMTP_SSL("smtp.163.com", 465)
    
    print("登录...")
    server.login(email_username, email_password)
    
    print("发送邮件...")
    server.send_message(msg)
    
    print("关闭连接...")
    server.quit()
    
    print("\n✅ 邮件发送成功！")
    print(f"请检查你的邮箱：{email_username}")
    
except Exception as e:
    print(f"\n❌ 发送失败: {e}")
    import traceback
    traceback.print_exc()
