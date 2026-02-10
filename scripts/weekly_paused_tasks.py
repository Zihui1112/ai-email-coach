"""
每周暂缓任务提醒脚本 - GitHub Actions
每周日21:00运行，询问暂缓任务是否要提上日程
"""
import os
import sys
import requests
from datetime import datetime

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def send_weekly_paused_tasks_reminder():
    """发送每周暂缓任务提醒"""
    print(f"[{datetime.now()}] 开始发送每周暂缓任务提醒")
    
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
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json"
        }
        
        # 获取暂缓的任务
        query_url = f"{supabase_url}/rest/v1/tasks?user_email=eq.{user_email}&status=eq.paused&select=*"
        db_response = requests.get(query_url, headers=headers, timeout=30)
        
        if db_response.status_code != 200:
            print(f"❌ 数据库查询失败: {db_response.status_code}")
            return False
        
        paused_tasks = db_response.json()
        
        # 如果没有暂缓任务，不发送提醒
        if not paused_tasks:
            print("✅ 没有暂缓任务，无需发送提醒")
            return True
        
        # 生成消息内容
        content = "📋 每周暂缓任务检查\n\n"
        content += "周末好！来看看你暂缓的任务吧~\n\n"
        content += "⏸️ 暂缓任务清单：\n"
        
        for task in paused_tasks:
            task_name = task.get('task_name', '未命名任务')
            progress = task.get('progress_percentage', 0)
            quadrant = f"Q{task.get('quadrant', 1)}"
            updated_at = task.get('updated_at', '')
            
            # 计算暂缓天数
            if updated_at:
                try:
                    updated_date = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
                    days_paused = (datetime.now(updated_date.tzinfo) - updated_date).days
                    days_text = f"（已暂缓 {days_paused} 天）"
                except:
                    days_text = ""
            else:
                days_text = ""
            
            # 生成进度条
            filled = int(progress / 10)
            empty = 10 - filled
            progress_bar = "■" * filled + "□" * empty
            
            content += f"\n⏸️ {task_name} {days_text}\n"
            content += f"   进度：[{progress_bar}] {progress}%\n"
            content += f"   象限: {quadrant}\n"
        
        content += "\n\n💬 请回复以下内容：\n"
        content += "1. 哪些暂缓任务需要重新开始？\n"
        content += "2. 哪些任务可以继续暂缓？\n"
        content += "3. 有没有任务可以直接放弃？\n"
        content += "\n示例：重新开始数据库设计，继续暂缓API开发"
        
        # 发送到飞书
        message = {
            "msg_type": "text",
            "content": {
                "text": content
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
            
            print("发送邮件...")
            
            msg = MIMEMultipart()
            msg['From'] = user_email
            msg['To'] = user_email
            msg['Subject'] = "📋 每周暂缓任务检查"
            
            email_body = f"{content}\n\n---\n请直接回复此邮件更新暂缓任务状态"
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
            
    except Exception as e:
        print(f"❌ 发送失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = send_weekly_paused_tasks_reminder()
    sys.exit(0 if success else 1)
