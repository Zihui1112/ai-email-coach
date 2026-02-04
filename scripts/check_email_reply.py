"""
检查邮件回复并自动处理 - GitHub Actions
每天23:00自动运行，检查用户的邮件回复
"""
import os
import sys
import poplib
import email
from email.header import decode_header
import requests
from datetime import datetime, timedelta
import re
import json

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def decode_str(s):
    """解码邮件头"""
    if s is None:
        return ""
    value, charset = decode_header(s)[0]
    if charset:
        try:
            value = value.decode(charset)
        except:
            value = value.decode('utf-8', errors='ignore')
    elif isinstance(value, bytes):
        value = value.decode('utf-8', errors='ignore')
    return str(value)

def parse_email_content(msg):
    """解析邮件内容"""
    content = ""
    
    if msg.is_multipart():
        for part in msg.walk():
            content_type = part.get_content_type()
            if content_type == "text/plain":
                try:
                    payload = part.get_payload(decode=True)
                    charset = part.get_content_charset() or 'utf-8'
                    content = payload.decode(charset, errors='ignore')
                    break
                except:
                    continue
    else:
        try:
            payload = msg.get_payload(decode=True)
            charset = msg.get_content_charset() or 'utf-8'
            content = payload.decode(charset, errors='ignore')
        except:
            content = str(msg.get_payload())
    
    return content.strip()

def check_and_process_email_reply():
    """检查邮件回复并处理"""
    print(f"[{datetime.now()}] 开始检查邮件回复")
    
    # 获取环境变量
    email_username = os.getenv("EMAIL_163_USERNAME", "").strip()
    email_password = os.getenv("EMAIL_163_PASSWORD", "").strip()
    webhook_url = os.getenv("FEISHU_WEBHOOK_URL", "").strip()
    supabase_url = os.getenv("SUPABASE_URL", "").strip()
    supabase_key = os.getenv("SUPABASE_KEY", "").strip()
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    
    if not all([email_username, email_password, supabase_url, supabase_key, deepseek_api_key]):
        print("❌ 环境变量未配置完整")
        return False
    
    try:
        # 连接到 POP3 服务器
        print("连接到 163 邮箱...")
        pop_server = poplib.POP3_SSL("pop.163.com", 995)
        pop_server.user(email_username)
        pop_server.pass_(email_password)
        
        # 获取邮件数量
        num_messages = len(pop_server.list()[1])
        print(f"邮箱中共有 {num_messages} 封邮件")
        
        if num_messages == 0:
            print("没有新邮件")
            pop_server.quit()
            return True
        
        # 只检查最近的邮件（最多检查最新的5封）
        check_count = min(5, num_messages)
        latest_reply = None
        latest_time = None
        
        # 从最新的邮件开始检查
        for i in range(num_messages, num_messages - check_count, -1):
            try:
                # 获取邮件
                response, lines, octets = pop_server.retr(i)
                msg_content = b'\r\n'.join(lines)
                msg = email.message_from_bytes(msg_content)
                
                # 获取邮件时间
                date_str = msg.get("Date", "")
                subject = decode_str(msg.get("Subject", ""))
                
                print(f"\n检查邮件 #{i}: {subject}")
                print(f"时间: {date_str}")
                
                # 检查是否是最近的邮件（最近2小时内）
                try:
                    from email.utils import parsedate_to_datetime
                    email_date = parsedate_to_datetime(date_str)
                    now = datetime.now(email_date.tzinfo)
                    
                    # 只处理最近2小时内的邮件
                    two_hours_ago = now - timedelta(hours=2)
                    
                    if email_date < two_hours_ago:
                        print(f"  → 邮件时间早于2小时前，跳过")
                        continue
                    
                    # 解析邮件内容
                    content = parse_email_content(msg)
                    
                    if content and len(content) > 10:
                        # 找到最新的回复
                        if latest_time is None or email_date > latest_time:
                            latest_reply = content
                            latest_time = email_date
                            print(f"  → 找到回复内容（{len(content)}字符）")
                    
                except Exception as e:
                    print(f"  → 解析邮件失败: {e}")
                    continue
                    
            except Exception as e:
                print(f"读取邮件 #{i} 失败: {e}")
                continue
        
        pop_server.quit()
        
        # 如果没有找到回复
        if not latest_reply:
            print("\n没有找到最近2小时内的回复邮件")
            
            # 发送提醒到飞书
            if webhook_url:
                message = {
                    "msg_type": "text",
                    "content": {
                        "text": "📧 邮件检查结果\n\n"
                               "没有检测到你的回复邮件。\n\n"
                               "如果你已经回复了，请确认：\n"
                               "1. 回复的是 15302814198@163.com\n"
                               "2. 邮件已成功发送\n"
                               "3. 回复时间在最近2小时内\n\n"
                               "或者稍后再试！😊"
                    }
                }
                requests.post(webhook_url, json=message, timeout=30)
            
            return True
        
        print(f"\n✅ 找到最新回复（{latest_time}）")
        print(f"内容预览: {latest_reply[:100]}...")
        
        # 使用 DeepSeek AI 解析回复
        print("\n使用 AI 解析回复...")
        
        headers = {
            "Authorization": f"Bearer {deepseek_api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""请解析以下任务更新内容，提取任务信息。

用户回复：
{latest_reply}

请以JSON格式返回，包含以下字段：
- task_name: 任务名称
- progress: 进度百分比(0-100)
- quadrant: 象限(Q1/Q2/Q3/Q4)
- action: 动作(update/pause/complete)

如果有多个任务，返回JSON数组。
只返回JSON，不要其他内容。"""
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ AI 解析失败: {response.status_code}")
            return False
        
        result = response.json()
        ai_response = result['choices'][0]['message']['content'].strip()
        
        # 清理 markdown 代码块
        ai_response = re.sub(r'```json\s*', '', ai_response)
        ai_response = re.sub(r'```\s*$', '', ai_response)
        ai_response = ai_response.strip()
        
        print(f"AI 解析结果: {ai_response}")
        
        # 解析 JSON
        try:
            tasks_data = json.loads(ai_response)
            if not isinstance(tasks_data, list):
                tasks_data = [tasks_data]
        except:
            print("❌ 无法解析 AI 返回的 JSON")
            return False
        
        # 更新数据库
        print("\n更新数据库...")
        
        db_headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json"
        }
        
        feedback_content = "📊 任务更新反馈\n\n"
        
        for task_data in tasks_data:
            task_name = task_data.get('task_name', '')
            progress = task_data.get('progress', 0)
            quadrant = task_data.get('quadrant', 'Q1')
            action = task_data.get('action', 'update')
            
            # 确保所有字段都不是 None
            if not task_name:
                continue
            
            # 确保 quadrant 不是 None 并且格式正确
            if not quadrant or not isinstance(quadrant, str):
                quadrant = 'Q1'
            
            # 确保 progress 是数字
            try:
                progress = int(progress) if progress else 0
            except:
                progress = 0
            
            # 确保 action 不是 None
            if not action:
                action = 'update'
            
            # 查询任务是否存在
            query_url = f"{supabase_url}/rest/v1/tasks?user_email=eq.{email_username}&task_name=eq.{task_name}&select=*"
            query_response = requests.get(query_url, headers=db_headers, timeout=30)
            
            if query_response.status_code == 200:
                existing_tasks = query_response.json()
                
                if existing_tasks:
                    # 更新现有任务
                    task_id = existing_tasks[0]['id']
                    update_url = f"{supabase_url}/rest/v1/tasks?id=eq.{task_id}"
                    
                    update_data = {
                        "progress_percentage": progress,
                        "quadrant": int(quadrant[1]) if quadrant.startswith('Q') else 1,
                        "status": "completed" if action == "complete" else ("paused" if action == "pause" else "active"),
                        "updated_at": datetime.now().isoformat()
                    }
                    
                    update_response = requests.patch(update_url, headers=db_headers, json=update_data, timeout=30)
                    
                    if update_response.status_code in [200, 204]:
                        status_emoji = "✅" if action == "complete" else ("⏸️" if action == "pause" else "🔄")
                        filled = int(progress / 10)
                        empty = 10 - filled
                        progress_bar = "■" * filled + "□" * empty
                        
                        feedback_content += f"{status_emoji} {task_name}\n"
                        feedback_content += f"   进度：[{progress_bar}] {progress}%\n"
                        feedback_content += f"   象限: {quadrant}\n\n"
                    else:
                        print(f"更新任务失败: {update_response.status_code}")
                else:
                    # 创建新任务
                    create_url = f"{supabase_url}/rest/v1/tasks"
                    
                    create_data = {
                        "user_email": email_username,
                        "task_name": task_name,
                        "progress_percentage": progress,
                        "quadrant": int(quadrant[1]) if quadrant.startswith('Q') else 1,
                        "status": "active",
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat()
                    }
                    
                    create_response = requests.post(create_url, headers=db_headers, json=create_data, timeout=30)
                    
                    if create_response.status_code in [200, 201]:
                        filled = int(progress / 10)
                        empty = 10 - filled
                        progress_bar = "■" * filled + "□" * empty
                        
                        feedback_content += f"🆕 {task_name}\n"
                        feedback_content += f"   进度：[{progress_bar}] {progress}%\n"
                        feedback_content += f"   象限: {quadrant}\n\n"
                    else:
                        print(f"创建任务失败: {create_response.status_code}")
        
        feedback_content += "💪 继续加油！"
        
        # 发送反馈到飞书
        if webhook_url:
            message = {
                "msg_type": "text",
                "content": {
                    "text": feedback_content
                }
            }
            
            response = requests.post(webhook_url, json=message, timeout=30)
            
            if response.status_code == 200:
                print("✅ 反馈已发送到飞书")
            else:
                print(f"❌ 发送飞书消息失败: {response.status_code}")
        
        # 同时发送反馈邮件
        try:
            import smtplib
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            
            print("\n发送反馈邮件...")
            
            msg = MIMEMultipart()
            msg['From'] = email_username
            msg['To'] = email_username
            msg['Subject'] = "📊 任务更新反馈"
            
            msg.attach(MIMEText(feedback_content, 'plain', 'utf-8'))
            
            server = smtplib.SMTP_SSL("smtp.163.com", 465)
            server.login(email_username, email_password)
            server.send_message(msg)
            server.quit()
            
            print("✅ 反馈邮件发送成功")
            
        except Exception as e:
            print(f"❌ 反馈邮件发送失败: {e}")
        
        print("\n✅ 邮件回复处理完成")
        return True
        
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = check_and_process_email_reply()
    sys.exit(0 if success else 1)
