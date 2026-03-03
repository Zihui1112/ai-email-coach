"""
检查邮件回复并自动处理 - GitHub Actions
v4.1 - 使用任务编号系统 + 极简反馈格式
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
    format_unlock_progress_message,
    get_user_inventory_summary,
    # v4.0 任务编号系统函数
    parse_task_operations_v4,
    process_task_operations_v4,
    format_operation_feedback_v4
)

def update_user_reply_tracking(supabase_url, headers, user_email):
    """更新用户回复追踪"""
    try:
        update_url = f"{supabase_url}/rest/v1/user_reply_tracking?user_email=eq.{user_email}"
        update_data = {
            "last_reply_date": date.today().isoformat(),
            "consecutive_no_reply_days": 0,
            "total_replies": 1,
            "updated_at": datetime.now().isoformat()
        }
        
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
        
        # 数据库headers
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
        
        # ============================================
        # v4.1：使用任务编号系统处理任务操作
        # ============================================
        print("\n使用 v4.0 任务编号系统解析回复...")
        
        # 解析任务操作
        operations = parse_task_operations_v4(latest_reply, deepseek_api_key)
        
        if not operations or len(operations) == 0:
            print("⚠️ 未检测到任务操作")
            feedback_content = "📊 任务更新反馈\n\n"
            feedback_content += "未检测到任务操作。\n\n"
            feedback_content += "💬 回复格式示例\n"
            feedback_content += "Q1: 1完成; 2进度50%\n"
            feedback_content += "Q2: 1暂缓\n"
            feedback_content += "新增：写论文 Q1\n"
            feedback_content += "暂缓任务1恢复到Q1\n"
        else:
            print(f"✅ 解析到 {len(operations)} 个任务操作")
            
            # 处理任务操作
            operation_results = process_task_operations_v4(supabase_url, db_headers, email_username, operations)
            
            # 格式化反馈（v4.1：极简风格）
            feedback_content = format_operation_feedback_v4_minimalist(operation_results)
            
            # 更新用户经验值和金币
            total_exp_gain = operation_results.get('total_exp_gain', 0)
            total_coins_gain = operation_results.get('total_coins_gain', 0)
            
            if total_exp_gain > 0 or total_coins_gain > 0:
                print(f"\n更新游戏化数据: EXP +{total_exp_gain}, Coins +{total_coins_gain}")
                update_result = update_user_exp_and_coins(
                    supabase_url, 
                    db_headers, 
                    email_username, 
                    total_exp_gain, 
                    total_coins_gain,
                    f"任务更新"
                )
                
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
        
        # 如果有性格切换，添加切换消息
        if personality_switch_result:
            feedback_content += "\n\n" + format_personality_switch_message(personality_switch_result)
        
        # 如果有购买，添加购买结果
        if purchase_result:
            if purchase_result.get('success'):
                feedback_content += "\n\n" + format_purchase_result_message(purchase_result)
            else:
                error_type = purchase_result.get('error_type', 'unknown')
                error_data = purchase_result.get('error_data', {})
                feedback_content += "\n\n" + format_purchase_error_message(error_type, error_data)
        
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


def format_operation_feedback_v4_minimalist(operation_results):
    """
    v4.1：格式化任务操作反馈消息（极简风格）
    
    参数:
        operation_results: 操作结果（包含results, total_exp_gain, total_coins_gain）
    
    返回:
        格式化的反馈消息
    """
    feedback = "📊 任务更新反馈\n\n"
    
    results = operation_results.get('results', [])
    
    for item in results:
        op = item['operation']
        result = item['result']
        
        if not result.get('success'):
            # 操作失败
            error = result.get('error', '未知错误')
            feedback += f"❌ 操作失败：{error}\n\n"
            continue
        
        # 操作成功
        if op == 'complete':
            task_name = result.get('task_name', '')
            exp_gain = result.get('exp_gain', 0)
            coins_gain = result.get('coins_gain', 0)
            display_number = result.get('display_number', '')
            
            feedback += f"✅ {display_number}. {task_name} 完成\n"
            feedback += f"   💫 +{exp_gain} EXP"
            if coins_gain > 0:
                feedback += f"  💰 +{coins_gain} Coin"
            feedback += "\n\n"
            
        elif op == 'update':
            task_name = result.get('task_name', '')
            old_progress = result.get('old_progress', 0)
            new_progress = result.get('new_progress', 0)
            exp_gain = result.get('exp_gain', 0)
            display_number = result.get('display_number', '')
            
            # 生成进度条
            filled = int(new_progress / 10)
            empty = 10 - filled
            progress_bar = "■" * filled + "□" * empty
            
            feedback += f"🔄 {display_number}. {task_name} 进度更新\n"
            feedback += f"   {old_progress}% → {new_progress}% [{progress_bar}]\n"
            if exp_gain > 0:
                feedback += f"   💫 +{exp_gain} EXP\n"
            feedback += "\n"
            
        elif op == 'create':
            task_name = result.get('task_name', '')
            display_number = result.get('display_number', '')
            quadrant = result.get('quadrant', 1)
            
            feedback += f"🆕 {display_number}. {task_name}\n"
            feedback += f"   象限：Q{quadrant}\n\n"
            
        elif op == 'pause':
            task_name = result.get('task_name', '')
            old_display_number = result.get('old_display_number', '')
            
            feedback += f"⏸️ {old_display_number}. {task_name} 已暂缓\n\n"
            
        elif op == 'resume':
            task_name = result.get('task_name', '')
            new_display_number = result.get('new_display_number', '')
            target_quadrant = result.get('target_quadrant', 1)
            
            feedback += f"🔄 {task_name} 已恢复\n"
            feedback += f"   新编号：{new_display_number}\n"
            feedback += f"   象限：Q{target_quadrant}\n\n"
    
    # 添加总结
    total_exp_gain = operation_results.get('total_exp_gain', 0)
    total_coins_gain = operation_results.get('total_coins_gain', 0)
    
    if total_exp_gain > 0 or total_coins_gain > 0:
        feedback += "本次收获：\n"
        if total_exp_gain > 0:
            feedback += f"💫 +{total_exp_gain} EXP\n"
        if total_coins_gain > 0:
            feedback += f"💰 +{total_coins_gain} Coin\n"
    
    return feedback


if __name__ == "__main__":
    success = check_and_process_email_reply()
    sys.exit(0 if success else 1)
