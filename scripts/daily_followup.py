"""
每日跟进提醒脚本 - GitHub Actions
每天23:00运行，提醒用户尽快回复邮件
"""
import os
import sys
import requests
from datetime import datetime

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def send_daily_followup():
    """发送每日跟进提醒"""
    print(f"[{datetime.now()}] 开始发送每日跟进提醒")
    
    # 获取环境变量
    webhook_url = os.getenv("FEISHU_WEBHOOK_URL", "").strip()
    user_email = os.getenv("EMAIL_163_USERNAME", "").strip()
    email_password = os.getenv("EMAIL_163_PASSWORD", "").strip()
    supabase_url = os.getenv("SUPABASE_URL", "").strip()
    supabase_key = os.getenv("SUPABASE_KEY", "").strip()
    
    if not all([webhook_url, user_email, email_password, supabase_url, supabase_key]):
        print("❌ 环境变量未配置完整")
        return False
    
    try:
        # 查询数据库获取任务清单
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json"
        }
        
        query_url = f"{supabase_url}/rest/v1/tasks?user_email=eq.{user_email}&status=eq.active&select=*"
        db_response = requests.get(query_url, headers=headers, timeout=30)
        
        if db_response.status_code != 200:
            print(f"❌ 数据库查询失败: {db_response.status_code}")
            return False
        
        tasks = db_response.json()
        
        # 生成消息内容
        content = "⏰ 跟进提醒\n\n"
        content += "如果你已经回复了复盘邮件，请忽略此消息。\n\n"
        content += "如果还没有回复，请尽快回复今天的复盘邮件！\n\n"
        content += "📋 今日任务清单：\n"
        
        if tasks:
            for task in tasks:
                progress = task.get('progress_percentage', 0)
                task_name = task.get('task_name', '未命名任务')
                quadrant = f"Q{task.get('quadrant', 1)}"
                
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
        
        content += "\n\n💬 请回复复盘邮件更新你的任务进度！"
        
        # 发送到飞书
        message = {
            "msg_type": "text",
            "content": {
                "text": f"📊 每日跟进提醒\n\n{content}"
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
        
        # 发送邮件
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            print("发送跟进邮件...")
            
            msg = MIMEMultipart()
            msg['From'] = user_email
            msg['To'] = user_email
            msg['Subject'] = "📊 每日跟进提醒"
            
            email_body = f"{content}\n\n---\n请直接回复此邮件或回复复盘邮件更新任务进度"
            msg.attach(MIMEText(email_body, 'plain', 'utf-8'))
            
            server = smtplib.SMTP_SSL("smtp.163.com", 465)
            server.login(user_email, email_password)
            server.send_message(msg)
            server.quit()
            
            print("✅ 跟进邮件发送成功")
            return True
            
        except Exception as e:
            print(f"❌ 跟进邮件发送失败: {e}")
            return feishu_success
            
    except Exception as e:
        print(f"❌ 发送失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = send_daily_followup()
    sys.exit(0 if success else 1)
