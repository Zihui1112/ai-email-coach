"""
检查邮件回复并自动处理 - GitHub Actions
每天23:30自动运行，检查用户的邮件回复
v3.0 - 添加游戏化系统（等级、经验值、金币）
"""
import os
import sys
import poplib
import email
from email.header import decode_header
import requests
from datetime import datetime, timedelta, date
import re
import json

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入游戏化工具
from gamification_utils import (
    calculate_exp_gain,
    calculate_coins_gain,
    update_user_exp_and_coins,
    check_and_update_q1_streak,
    format_level_up_message,
    get_user_gamification_data,
    update_consecutive_reply_days,
    check_persistence_milestone,
    format_persistence_reward_message,
    parse_personality_switch_command,
    switch_ai_personality,
    format_personality_switch_message,
    generate_personality_feedback,
    parse_purchase_command,
    get_shop_item_by_name,
    check_purchase_eligibility,
    check_usage_limit,
    purchase_item,
    format_purchase_result_message,
    format_purchase_error_message,
    format_unlock_progress_message
)
    get_user_inventory_summary
)

def update_user_reply_tracking(supabase_url, headers, user_email):
    """更新用户回复追踪"""
    try:
        update_url = f"{supabase_url}/rest/v1/user_reply_tracking?user_email=eq.{user_email}"
        update_data = {
            "last_reply_date": date.today().isoformat(),
            "consecutive_no_reply_days": 0,
            "total_replies": 1,  # 这里应该是增量，但为了简化先设为1
            "updated_at": datetime.now().isoformat()
        }
        
        # 先尝试更新
        response = requests.patch(update_url, headers=headers, json=update_data, timeout=30)
        
        if response.status_code in [200, 204]:
            print("✅ 更新用户回复追踪成功")
            return True
        
        # 如果更新失败，尝试创建
        create_url = f"{supabase_url}/rest/v1/user_reply_tracking"
        create_data = {
            "user_email": user_email,
            "last_reply_date": date.today().isoformat(),
            "consecutive_no_reply_days": 0,
            "total_replies": 1
        }
        
        response = requests.post(create_url, headers=headers, json=create_data, timeout=30)
        
        if response.status_code in [200, 201]:
            print("✅ 创建用户回复追踪成功")
            return True
        
        return False
    except Exception as e:
        print(f"更新用户回复追踪失败: {e}")
        return False

def get_task_progress_changes(supabase_url, headers, user_email, tasks_data):
    """获取任务进度变化"""
    try:
        changes = []
        
        for task_data in tasks_data:
            task_name = task_data.get('task_name', '')
            new_progress = task_data.get('progress', 0)
            
            # 查询昨天的进度
            yesterday = (date.today() - timedelta(days=1)).isoformat()
            query_url = f"{supabase_url}/rest/v1/task_progress_snapshot?user_email=eq.{user_email}&task_name=eq.{task_name}&snapshot_date=eq.{yesterday}&select=*"
            
            response = requests.get(query_url, headers=headers, timeout=30)
            
            if response.status_code == 200:
                snapshots = response.json()
                if snapshots:
                    old_progress = snapshots[0].get('progress_percentage', 0)
                    progress_change = new_progress - old_progress
                    
                    changes.append({
                        'task_name': task_name,
                        'old_progress': old_progress,
                        'new_progress': new_progress,
                        'change': progress_change
                    })
        
        return changes
    except Exception as e:
        print(f"获取任务进度变化失败: {e}")
        return []

def save_task_progress_snapshot(supabase_url, headers, user_email, tasks_data):
    """保存任务进度快照"""
    try:
        today = date.today().isoformat()
        
        for task_data in tasks_data:
            task_name = task_data.get('task_name', '')
            progress = task_data.get('progress', 0)
            action = task_data.get('action', 'update')
            
            status = "completed" if action == "complete" else ("paused" if action == "pause" else "active")
            
            # 先尝试更新
            update_url = f"{supabase_url}/rest/v1/task_progress_snapshot?user_email=eq.{user_email}&task_name=eq.{task_name}&snapshot_date=eq.{today}"
            update_data = {
                "progress_percentage": progress,
                "status": status
            }
            
            response = requests.patch(update_url, headers=headers, json=update_data, timeout=30)
            
            if response.status_code not in [200, 204]:
                # 如果更新失败，尝试创建
                create_url = f"{supabase_url}/rest/v1/task_progress_snapshot"
                create_data = {
                    "user_email": user_email,
                    "task_name": task_name,
                    "progress_percentage": progress,
                    "status": status,
                    "snapshot_date": today
                }
                
                requests.post(create_url, headers=headers, json=create_data, timeout=30)
        
        print("✅ 保存任务进度快照成功")
        return True
    except Exception as e:
        print(f"保存任务进度快照失败: {e}")
        return False

def generate_ai_feedback(tasks_data, supabase_url, headers, user_email, deepseek_api_key):
    """使用AI生成个性化反馈"""
    try:
        # 获取任务进度变化
        progress_changes = get_task_progress_changes(supabase_url, headers, user_email, tasks_data)
        
        # 构建AI提示词
        task_summary = []
        for task in tasks_data:
            task_summary.append({
                'name': task.get('task_name', ''),
                'progress': task.get('progress', 0),
                'action': task.get('action', 'update')
            })
        
        prompt = f"""你是一个温暖、鼓励的任务管理助手。请根据用户的任务更新情况，生成一段个性化的反馈。

任务更新情况：
{json.dumps(task_summary, ensure_ascii=False, indent=2)}

进度变化：
{json.dumps(progress_changes, ensure_ascii=False, indent=2) if progress_changes else "无历史数据"}

要求：
1. 语气温暖、鼓励，像朋友一样
2. 根据进度变化给出具体的反馈（进步大→表扬，进度慢→鼓励，暂缓→理解）
3. 根据任务数量给出建议（任务多→提醒合理安排，任务少→鼓励增加）
4. 不要使用"继续加油"这种机械的话
5. 控制在3-5句话以内
6. 不要使用emoji，使用文字表达情感

只返回反馈内容，不要其他说明。"""
        
        headers_ai = {
            "Authorization": f"Bearer {deepseek_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.8
        }
        
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers_ai,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            feedback = result['choices'][0]['message']['content'].strip()
            print(f"✅ AI反馈生成成功: {feedback[:50]}...")
            return feedback
        else:
            print(f"❌ AI反馈生成失败: {response.status_code}")
            return "很高兴看到你的更新！保持这个节奏，相信你能完成所有任务。"
    
    except Exception as e:
        print(f"生成AI反馈失败: {e}")
        return "感谢你的更新！继续保持，你做得很好。"

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
        
        # 只检查最近的邮件（最多检查最新的10封）
        check_count = min(10, num_messages)
        latest_reply = None
        latest_time = None
        
        # 目标邮件标题（用于筛选）
        target_subjects = [
            "回复：📊 每日复盘提醒",
            "Re: 📊 每日复盘提醒",
            "回复：📊 每日跟进提醒",
            "Re: 📊 每日跟进提醒"
        ]
        
        # 从最新的邮件开始检查
        for i in range(num_messages, num_messages - check_count, -1):
            try:
                # 获取邮件
                response, lines, octets = pop_server.retr(i)
                msg_content = b'\r\n'.join(lines)
                msg = email.message_from_bytes(msg_content)
                
                # 获取邮件时间和标题
                date_str = msg.get("Date", "")
                subject = decode_str(msg.get("Subject", ""))
                
                print(f"\n检查邮件 #{i}: {subject}")
                print(f"时间: {date_str}")
                
                # 检查标题是否符合要求
                subject_match = False
                for target_subject in target_subjects:
                    if target_subject in subject:
                        subject_match = True
                        print(f"  → 标题匹配: {target_subject}")
                        break
                
                if not subject_match:
                    print(f"  → 标题不匹配，跳过")
                    continue
                
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
                            print(f"  → 找到符合条件的回复内容（{len(content)}字符）")
                    
                except Exception as e:
                    print(f"  → 解析邮件失败: {e}")
                    continue
                    
            except Exception as e:
                print(f"读取邮件 #{i} 失败: {e}")
                continue
        
        pop_server.quit()
        
        # 如果没有找到符合条件的回复
        if not latest_reply:
            print("\n没有找到符合标题要求的回复邮件")
            
            # 发送提醒到飞书和邮箱
            reminder_text = ("📧 邮件检查结果\n\n"
                           "没有检测到符合要求的回复邮件。\n\n"
                           "请确认：\n"
                           "1. 回复了「📊 每日复盘提醒」或「📊 每日跟进提醒」邮件\n"
                           "2. 邮件标题包含「回复：」或「Re:」\n"
                           "3. 回复时间在最近2小时内\n\n"
                           "💡 如需修改计划，请访问：\n"
                           "https://github.com/Zihui1112/ai-email-coach/actions\n"
                           "手动运行「处理用户回复」workflow")
            
            # 发送到飞书
            if webhook_url:
                message = {
                    "msg_type": "text",
                    "content": {
                        "text": reminder_text
                    }
                }
                requests.post(webhook_url, json=message, timeout=30)
            
            # 发送邮件提醒
            try:
                import smtplib
                from email.mime.text import MIMEText
                from email.mime.multipart import MIMEMultipart
                
                print("\n发送提醒邮件...")
                
                msg = MIMEMultipart()
                msg['From'] = email_username
                msg['To'] = email_username
                msg['Subject'] = "⚠️ 未检测到回复"
                
                msg.attach(MIMEText(reminder_text, 'plain', 'utf-8'))
                
                server = smtplib.SMTP_SSL("smtp.163.com", 465)
                server.login(email_username, email_password)
                server.send_message(msg)
                server.quit()
                
                print("✅ 提醒邮件发送成功")
                
            except Exception as e:
                print(f"❌ 提醒邮件发送失败: {e}")
            
            return True
        
        print(f"\n✅ 找到最新回复（{latest_time}）")
        print(f"内容预览: {latest_reply[:100]}...")
        
        # 提前定义 db_headers，因为后面的命令检测需要用到
        db_headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json"
        }
        
        # 检查是否有性格切换命令
        personality_switch_cmd = parse_personality_switch_command(latest_reply)
        personality_switch_result = None
        
        if personality_switch_cmd:
            print(f"\n检测到性格切换命令: {personality_switch_cmd}")
            personality_switch_result = switch_ai_personality(supabase_url, db_headers, email_username, personality_switch_cmd)
        
        # 检查是否有购买命令
        purchase_cmd = parse_purchase_command(latest_reply)
        purchase_result = None
        
        if purchase_cmd:
            print(f"\n检测到购买命令: {purchase_cmd}")
            
            # 获取道具信息
            item_data = get_shop_item_by_name(supabase_url, db_headers, purchase_cmd)
            
            if not item_data:
                purchase_result = {'success': False, 'error_type': 'item_not_found'}
            else:
                # 获取用户数据
                user_data = get_user_gamification_data(supabase_url, db_headers, email_username)
                
                # 检查购买资格
                eligibility = check_purchase_eligibility(user_data, item_data)
                
                if not eligibility['eligible']:
                    purchase_result = {
                        'success': False,
                        'error_type': eligibility['reason'],
                        'error_data': eligibility
                    }
                else:
                    # 检查使用限制
                    limit_check = check_usage_limit(supabase_url, db_headers, email_username, item_data['item_code'], item_data)
                    
                    if not limit_check['within_limit']:
                        purchase_result = {
                            'success': False,
                            'error_type': 'usage_limit_exceeded',
                            'error_data': limit_check
                        }
                    else:
                        # 执行购买
                        purchase_result = purchase_item(supabase_url, db_headers, email_username, item_data['item_code'], item_data)
        
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

重要规则：
1. action字段的判断：
   - 如果用户明确说"完成"、"已完成"、"做完了"、"finish"、"done"、"100%"，则action="complete"
   - 如果用户说"暂缓"、"暂停"、"pause"，则action="pause"
   - 其他情况action="update"

2. progress字段的判断：
   - 如果action="complete"，progress必须是100
   - 如果用户说了具体百分比（如50%、80%），使用该百分比
   - 如果没有说百分比但说了"完成"，progress=100
   - 如果没有任何进度信息，progress=0

3. 如果用户多次提到同一个任务已完成，一定要设置action="complete"和progress=100

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
        
        feedback_content = "📊 任务更新反馈\n\n"
        
        # 用于累计经验值和金币
        total_exp_gain = 0
        total_coins_gain = 0
        completed_tasks = 0
        total_tasks = len(tasks_data)
        has_q1_task = False
        q1_all_completed = True
        
        for task_data in tasks_data:
            task_name = task_data.get('task_name', '')
            progress = task_data.get('progress', 0)
            quadrant = task_data.get('quadrant', 'Q1')
            action = task_data.get('action', 'update')
            
            # 确保所有字段都不是 None
            if not task_name:
                continue
            
            # 确保 quadrant 不是 None 并且格式正确
            if not quadrant or not isinstance(quadrant, str) or not quadrant.strip():
                quadrant = 'Q1'
            else:
                quadrant = quadrant.strip().upper()
                # 如果不是 Q1-Q4 格式，默认为 Q1
                if not (quadrant.startswith('Q') and len(quadrant) == 2 and quadrant[1] in '1234'):
                    quadrant = 'Q1'
            
            # 确保 progress 是数字
            try:
                progress = int(progress) if progress else 0
                # 限制在 0-100 范围内
                progress = max(0, min(100, progress))
            except:
                progress = 0
            
            # 确保 action 不是 None
            if not action or not isinstance(action, str):
                action = 'update'
            else:
                action = action.strip().lower()
                # 只允许特定的 action 值
                if action not in ['update', 'pause', 'complete']:
                    action = 'update'
            
            # 查询任务是否存在
            query_url = f"{supabase_url}/rest/v1/tasks?user_email=eq.{email_username}&task_name=eq.{task_name}&select=*"
            query_response = requests.get(query_url, headers=db_headers, timeout=30)
            
            quadrant_num = int(quadrant[1]) if quadrant.startswith('Q') else 1
            
            # 检查是否是Q1任务
            if quadrant_num == 1:
                has_q1_task = True
                if action != "complete" and progress < 100:
                    q1_all_completed = False
            
            if query_response.status_code == 200:
                existing_tasks = query_response.json()
                
                if existing_tasks:
                    # 更新现有任务
                    task_id = existing_tasks[0]['id']
                    old_progress = existing_tasks[0].get('progress_percentage', 0)
                    progress_change = progress - old_progress
                    
                    update_url = f"{supabase_url}/rest/v1/tasks?id=eq.{task_id}"
                    
                    update_data = {
                        "progress_percentage": progress,
                        "quadrant": quadrant_num,
                        "status": "completed" if action == "complete" else ("paused" if action == "pause" else "active"),
                        "updated_at": datetime.now().isoformat()
                    }
                    
                    update_response = requests.patch(update_url, headers=db_headers, json=update_data, timeout=30)
                    
                    if update_response.status_code in [200, 204]:
                        # 计算经验值获得
                        if progress_change > 0:
                            exp_gain = calculate_exp_gain(progress_change, quadrant_num)
                            total_exp_gain += exp_gain
                        
                        # 统计完成任务数
                        if action == "complete" or progress >= 100:
                            completed_tasks += 1
                        
                        status_emoji = "✅" if action == "complete" else ("⏸️" if action == "pause" else "🔄")
                        filled = int(progress / 10)
                        empty = 10 - filled
                        progress_bar = "■" * filled + "□" * empty
                        
                        feedback_content += f"{status_emoji} {task_name}\n"
                        feedback_content += f"   进度：[{progress_bar}] {progress}%\n"
                        feedback_content += f"   象限: {quadrant}\n"
                        
                        # 显示经验值获得
                        if progress_change > 0:
                            feedback_content += f"   💫 +{exp_gain} EXP\n"
                        
                        feedback_content += "\n"
                    else:
                        print(f"更新任务失败: {update_response.status_code}")
                else:
                    # 创建新任务
                    create_url = f"{supabase_url}/rest/v1/tasks"
                    
                    create_data = {
                        "user_email": email_username,
                        "task_name": task_name,
                        "progress_percentage": progress,
                        "quadrant": quadrant_num,
                        "status": "active",
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat()
                    }
                    
                    create_response = requests.post(create_url, headers=db_headers, json=create_data, timeout=30)
                    
                    if create_response.status_code in [200, 201]:
                        # 新任务也计算经验值
                        if progress > 0:
                            exp_gain = calculate_exp_gain(progress, quadrant_num)
                            total_exp_gain += exp_gain
                        
                        # 统计完成任务数
                        if progress >= 100:
                            completed_tasks += 1
                        
                        filled = int(progress / 10)
                        empty = 10 - filled
                        progress_bar = "■" * filled + "□" * empty
                        
                        feedback_content += f"🆕 {task_name}\n"
                        feedback_content += f"   进度：[{progress_bar}] {progress}%\n"
                        feedback_content += f"   象限: {quadrant}\n"
                        
                        # 显示经验值获得
                        if progress > 0:
                            feedback_content += f"   💫 +{exp_gain} EXP\n"
                        
                        feedback_content += "\n"
                    else:
                        print(f"创建任务失败: {create_response.status_code}")
        
        # 保存任务进度快照
        save_task_progress_snapshot(supabase_url, db_headers, email_username, tasks_data)
        
        # 计算完成率和金币获得
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        total_coins_gain = calculate_coins_gain(completion_rate)
        
        # 更新用户经验值和金币
        print(f"\n更新游戏化数据: EXP +{total_exp_gain}, Coins +{total_coins_gain}")
        update_result = update_user_exp_and_coins(
            supabase_url, 
            db_headers, 
            email_username, 
            total_exp_gain, 
            total_coins_gain,
            f"任务更新 ({completed_tasks}/{total_tasks}完成)"
        )
        
        # 检查并更新Q1连击
        q1_streak = check_and_update_q1_streak(supabase_url, db_headers, email_username, has_q1_task, q1_all_completed)
        
        # 添加经验值和金币总结
        feedback_content += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        feedback_content += "📈 本次收获：\n"
        feedback_content += f"   💫 经验值：+{total_exp_gain} EXP\n"
        feedback_content += f"   💰 金币：+{total_coins_gain} Coin\n"
        feedback_content += f"   📊 完成率：{completion_rate:.0f}% ({completed_tasks}/{total_tasks})\n"
        
        if q1_streak > 0:
            feedback_content += f"   🔥 Q1连击：{q1_streak}天\n"
        
        # 检查是否升级
        if update_result and update_result.get('level_up'):
            old_level = update_result.get('old_level')
            new_level = update_result.get('new_level')
            level_up_msg = format_level_up_message(old_level, new_level)
            feedback_content += f"\n{level_up_msg}\n"
        else:
            # 如果没有升级，显示解锁进度激励
            if update_result:
                user_game_data_updated = get_user_gamification_data(supabase_url, db_headers, email_username)
                if user_game_data_updated:
                    unlock_progress_msg = format_unlock_progress_message(user_game_data_updated, total_exp_gain)
                    feedback_content += unlock_progress_msg
        
        feedback_content += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        
        # 使用 AI 生成个性化反馈
        print("\n生成个性化反馈...")
        
        # 获取用户当前性格
        user_game_data = get_user_gamification_data(supabase_url, db_headers, email_username)
        current_personality = user_game_data.get('ai_personality', 'friendly') if user_game_data else 'friendly'
        
        # 获取进度变化
        progress_changes = get_task_progress_changes(supabase_url, db_headers, email_username, tasks_data)
        
        # 根据性格生成反馈
        personalized_feedback = generate_personality_feedback(
            tasks_data, 
            progress_changes, 
            current_personality, 
            deepseek_api_key
        )
        
        feedback_content += f"\n{personalized_feedback}\n\n"
        
        # 如果有性格切换，添加切换消息
        if personality_switch_result:
            feedback_content += format_personality_switch_message(personality_switch_result) + "\n\n"
        
        # 如果有购买，添加购买结果
        if purchase_result:
            if purchase_result.get('success'):
                feedback_content += format_purchase_result_message(purchase_result) + "\n\n"
            else:
                error_type = purchase_result.get('error_type', 'unknown')
                error_data = purchase_result.get('error_data', {})
                feedback_content += format_purchase_error_message(error_type, error_data) + "\n\n"
        
        feedback_content += "💡 如需修改计划，请访问：\n"
        feedback_content += "https://github.com/Zihui1112/ai-email-coach/actions\n"
        feedback_content += "手动运行「处理用户回复」workflow"
        
        # 更新用户回复追踪
        update_user_reply_tracking(supabase_url, db_headers, email_username)
        
        # 更新连续回复天数
        consecutive_reply_days = update_consecutive_reply_days(supabase_url, db_headers, email_username)
        
        # 检查坚持里程碑奖励
        persistence_reward = check_persistence_milestone(supabase_url, db_headers, email_username, consecutive_reply_days)
        
        # 如果有坚持奖励，添加到反馈中
        if persistence_reward:
            feedback_content += "\n\n" + format_persistence_reward_message(persistence_reward)
        
        # 显示连续回复天数
        feedback_content += f"\n\n💡 连续回复：{consecutive_reply_days}天 🔥"
        
        # 显示背包摘要
        inventory_summary = get_user_inventory_summary(supabase_url, db_headers, email_username)
        if inventory_summary:
            feedback_content += inventory_summary
        
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
