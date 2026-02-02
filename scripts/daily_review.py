"""
每日复盘提醒脚本 - GitHub Actions
"""
import os
import sys
import requests
from datetime import datetime

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def send_daily_review():
    """发送每日复盘提醒"""
    print(f"[{datetime.now()}] 开始发送每日复盘提醒")
    
    # 获取环境变量并清理空格和换行符
    webhook_url = os.getenv("FEISHU_WEBHOOK_URL", "").strip()
    user_email = os.getenv("EMAIL_163_USERNAME", "").strip()
    supabase_url = os.getenv("SUPABASE_URL", "").strip()
    supabase_key = os.getenv("SUPABASE_KEY", "").strip()
    
    if not all([webhook_url, user_email, supabase_url, supabase_key]):
        print("❌ 环境变量未配置完整，请检查.env文件")
        return False
    
    try:
        # 使用 REST API 直接查询数据库（避免 HTTP/2 问题）
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json"
        }
        
        # 获取今日任务
        query_url = f"{supabase_url}/rest/v1/tasks?user_email=eq.{user_email}&status=eq.active&select=*"
        db_response = requests.get(query_url, headers=headers, timeout=30)
        
        if db_response.status_code != 200:
            print(f"❌ 数据库查询失败: {db_response.status_code}")
            print(f"响应内容: {db_response.text}")
            if db_response.status_code == 401:
                print("⚠️ 认证失败！请检查 SUPABASE_KEY 是否使用了 service_role key")
                print("提示：需要使用 service_role key，而不是 anon key")
            return False
        
        tasks = db_response.json()
        
        # 生成消息内容
        content = "🌙 晚上好！今天的任务完成情况如何？\n\n"
        content += "📋 今日任务清单：\n"
        
        if tasks:
            for task in tasks:
                progress = task.get('progress', 0)
                task_name = task.get('task_name', '未命名任务')
                quadrant = task.get('quadrant', 'Q1')
                
                # 生成进度条
                filled = int(progress / 10)
                empty = 10 - filled
                progress_bar = "■" * filled + "□" * empty
                
                status_emoji = "✅" if progress == 100 else "🔄"
                
                content += f"\n{status_emoji} {task_name}\n"
                content += f"   进度：[{progress_bar}] {progress}%\n"
                content += f"   象限: {quadrant}\n"
        else:
            content += "\n暂无进行中的任务\n"
        
        content += "\n\n💬 请回复以下内容：\n"
        content += "1. 今天完成了哪些任务？进度如何？\n"
        content += "2. 明天计划做什么？\n"
        content += "3. 有哪些任务需要暂缓？\n"
        content += "\n示例：完成了用户登录功能80%，明天做数据库设计Q2任务"
        
        # 发送到飞书
        message = {
            "msg_type": "text",
            "content": {
                "text": f"📊 每日复盘\n\n{content}"
            }
        }
        
        feishu_success = False
        response = requests.post(webhook_url, json=message, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("StatusCode") == 0:
                print("✅ 飞书消息发送成功")
                feishu_success = True
            else:
                print(f"❌ 飞书返回错误: {result}")
        else:
            print(f"❌ 飞书HTTP请求失败: {response.status_code}")
        
        # 同时发送邮件
        email_password = os.getenv("EMAIL_163_PASSWORD", "").strip()
        
        if email_password:
            try:
                import smtplib
                from email.mime.text import MIMEText
                from email.mime.multipart import MIMEMultipart
                
                print("发送邮件...")
                
                msg = MIMEMultipart()
                msg['From'] = user_email
                msg['To'] = user_email
                msg['Subject'] = "📊 每日复盘提醒"
                
                email_body = f"每日复盘\n\n{content}\n\n---\n请直接回复此邮件更新任务进度"
                msg.attach(MIMEText(email_body, 'plain', 'utf-8'))
                
                server = smtplib.SMTP_SSL("smtp.163.com", 465)
                server.login(user_email, email_password)
                server.send_message(msg)
                server.quit()
                
                print("✅ 邮件发送成功")
                return True
                
            except Exception as e:
                print(f"❌ 邮件发送失败: {e}")
                return feishu_success
        
        return feishu_success
            
    except Exception as e:
        print(f"❌ 发送失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = send_daily_review()
    sys.exit(0 if success else 1)
