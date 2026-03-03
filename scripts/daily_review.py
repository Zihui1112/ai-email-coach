"""
每日复盘提醒脚本 - GitHub Actions
v3.0 - 添加游戏化系统（等级、经验值、金币）
"""
import os
import sys
import requests
from datetime import datetime, date, timedelta
import json

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入游戏化工具
from gamification_utils import (
    get_user_gamification_data,
    format_quadrant_guide,
    format_user_status,
    check_and_apply_no_reply_punishment,
    format_punishment_message,
    get_user_inventory_summary,
    # v4.0 任务编号系统函数
    get_paused_tasks_to_remind
)

def get_user_reply_status(supabase_url, headers, user_email):
    """获取用户回复状态"""
    try:
        query_url = f"{supabase_url}/rest/v1/user_reply_tracking?user_email=eq.{user_email}&select=*"
        response = requests.get(query_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                return data[0]
        
        # 如果没有记录，创建一个
        create_url = f"{supabase_url}/rest/v1/user_reply_tracking"
        create_data = {
            "user_email": user_email,
            "last_reply_date": None,
            "consecutive_no_reply_days": 0,
            "total_replies": 0
        }
        response = requests.post(create_url, headers=headers, json=create_data, timeout=30)
        
        if response.status_code in [200, 201]:
            return create_data
        
        return None
    except Exception as e:
        print(f"获取用户回复状态失败: {e}")
        return None

def update_no_reply_days(supabase_url, headers, user_email, reply_status):
    """更新连续未回复天数"""
    try:
        last_reply_date = reply_status.get('last_reply_date')
        consecutive_days = reply_status.get('consecutive_no_reply_days', 0)
        
        # 如果有最后回复日期，计算天数差
        if last_reply_date:
            last_date = datetime.strptime(last_reply_date, '%Y-%m-%d').date()
            days_diff = (date.today() - last_date).days
            
            # 如果超过1天没回复，增加计数
            if days_diff > 1:
                consecutive_days = days_diff - 1
        else:
            # 如果从未回复，增加计数
            consecutive_days += 1
        
        # 更新数据库
        update_url = f"{supabase_url}/rest/v1/user_reply_tracking?user_email=eq.{user_email}"
        update_data = {
            "consecutive_no_reply_days": consecutive_days,
            "updated_at": datetime.now().isoformat()
        }
        
        response = requests.patch(update_url, headers=headers, json=update_data, timeout=30)
        
        if response.status_code in [200, 204]:
            print(f"✅ 更新连续未回复天数: {consecutive_days}")
            return consecutive_days
        
        return consecutive_days
    except Exception as e:
        print(f"更新未回复天数失败: {e}")
        return 0

def generate_personalized_greeting(consecutive_no_reply_days, is_weekend):
    """生成个性化问候语"""
    today = datetime.now()
    weekday = today.strftime('%A')
    weekday_cn = {
        'Monday': '周一', 'Tuesday': '周二', 'Wednesday': '周三',
        'Thursday': '周四', 'Friday': '周五', 'Saturday': '周六', 'Sunday': '周日'
    }
    
    if consecutive_no_reply_days == 0:
        # 正常情况
        greetings = [
            f"🌙 {weekday_cn.get(weekday, '')}晚上好！又到了复盘时间~",
            f"✨ {weekday_cn.get(weekday, '')}晚上好！今天过得怎么样？",
            f"🎯 {weekday_cn.get(weekday, '')}晚上好！来看看今天的进展吧！"
        ]
        import random
        return random.choice(greetings)
    elif consecutive_no_reply_days == 1:
        # 昨天没回复
        return f"👋 {weekday_cn.get(weekday, '')}晚上好！昨天好像没看到你的回复，今天一起来复盘吧~"
    elif consecutive_no_reply_days == 2:
        # 连续2天没回复
        return f"🤔 {weekday_cn.get(weekday, '')}晚上好！已经两天没见到你了，是不是最近比较忙？抽空复盘一下吧！"
    elif consecutive_no_reply_days >= 3:
        # 连续3天以上没回复
        return f"⚠️ {weekday_cn.get(weekday, '')}晚上好！已经{consecutive_no_reply_days}天没有回复了！别让任务积压太久哦，今天一定要回复！"
    
    return "🌙 晚上好！"

def send_daily_review():
    """发送每日复盘提醒"""
    print(f"[{datetime.now()}] 开始发送每日复盘提醒")
    
    # 获取环境变量
    webhook_url = os.getenv("FEISHU_WEBHOOK_URL", "").strip()
    user_email = os.getenv("EMAIL_163_USERNAME", "").strip()
    supabase_url = os.getenv("SUPABASE_URL", "").strip()
    supabase_key = os.getenv("SUPABASE_KEY", "").strip()
    
    if not all([webhook_url, user_email, supabase_url, supabase_key]):
        print("❌ 环境变量未配置完整")
        return False
    
    try:
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json"
        }
        
        # 获取用户回复状态
        reply_status = get_user_reply_status(supabase_url, headers, user_email)
        consecutive_no_reply_days = 0
        
        if reply_status:
            consecutive_no_reply_days = update_no_reply_days(supabase_url, headers, user_email, reply_status)
        
        # 检查并执行未回复惩罚
        punishment_result = check_and_apply_no_reply_punishment(supabase_url, headers, user_email)
        
        # 判断是否是周末
        is_weekend = datetime.now().weekday() >= 5
        
        # 获取用户游戏化数据
        user_game_data = get_user_gamification_data(supabase_url, headers, user_email)
        
        # 获取活跃任务（v4.0：添加is_deleted过滤和排序）
        query_url = f"{supabase_url}/rest/v1/tasks?user_email=eq.{user_email}&status=eq.active&is_deleted=eq.false&order=quadrant.asc,task_order.asc&select=*"
        db_response = requests.get(query_url, headers=headers, timeout=30)
        
        if db_response.status_code != 200:
            print(f"❌ 数据库查询失败: {db_response.status_code}")
            return False
        
        tasks = db_response.json()
        
        # 获取需要提醒的暂缓任务（v4.0）
        paused_tasks = get_paused_tasks_to_remind(supabase_url, headers, user_email)
        
        # 生成个性化问候语
        greeting = generate_personalized_greeting(consecutive_no_reply_days, is_weekend)
        
        # 生成消息内容（v4.1：极简风格）
        content = f"{greeting}\n\n"
        
        content += "📋 今日任务清单\n\n"
        
        # v4.1：按象限分组显示任务（极简风格）
        if tasks:
            # 按象限分组
            tasks_by_quadrant = {1: [], 2: [], 3: [], 4: []}
            for task in tasks:
                q = task.get('quadrant', 1)
                tasks_by_quadrant[q].append(task)
            
            # 象限名称和经验值倍率
            quadrant_info = {
                1: ("Q1 🔴 重要且紧急", "EXP x2.0"),
                2: ("Q2 🟡 重要非紧急", "EXP x1.5"),
                3: ("Q3 🔵 紧急非重要", "EXP x1.0"),
                4: ("Q4 ⚪ 非紧急非重要", "EXP x0.5")
            }
            
            # 显示每个象限（极简风格，无分隔线）
            for q in [1, 2, 3, 4]:
                q_name, exp_rate = quadrant_info[q]
                content += f"{q_name} ({exp_rate})\n"
                
                if tasks_by_quadrant[q]:
                    for task in tasks_by_quadrant[q]:
                        task_order = task.get('task_order', 0)
                        task_name = task.get('task_name', '未命名任务')
                        progress = task.get('progress_percentage', 0)
                        
                        # 生成进度条
                        filled = int(progress / 10)
                        empty = 10 - filled
                        progress_bar = "■" * filled + "□" * empty
                        
                        content += f"{task_order}. {task_name} [{progress_bar}] {progress}%\n"
                else:
                    content += "（暂无任务）\n"
                
                content += "\n"  # 象限之间用空行分隔
        else:
            content += "暂无进行中的任务\n\n"
        
        # v4.1：显示暂缓待办池（极简风格）
        if paused_tasks:
            content += "⏸️ 暂缓待办池\n"
            
            for task in paused_tasks:
                task_order = task.get('task_order', 0)
                task_name = task.get('task_name', '未命名任务')
                content += f"{task_order}. {task_name}\n"
            
            content += "\n"
            
            # 更新last_reminded_date为今天
            today = date.today().isoformat()
            for task in paused_tasks:
                task_id = task['id']
                update_url = f"{supabase_url}/rest/v1/tasks?id=eq.{task_id}"
                requests.patch(update_url, headers=headers, json={"last_reminded_date": today}, timeout=30)
            
            print(f"✅ 更新了 {len(paused_tasks)} 个暂缓任务的提醒日期")
        
        # 根据连续未回复天数调整提示语
        if consecutive_no_reply_days >= 3:
            content += "\n⚠️ 重要提醒：\n"
            content += f"已经{consecutive_no_reply_days}天没有更新任务了！\n"
            content += "长时间不复盘可能会让任务失控，今天一定要回复哦！\n"
        elif consecutive_no_reply_days >= 1:
            content += "\n💡 温馨提示：\n"
            content += "定期复盘能帮助你更好地掌控任务进度~\n"
        
        # v4.1：更新回复格式示例（简洁清晰）
        content += "💬 回复格式示例\n"
        content += "Q1: 1完成; 2进度50%\n"
        content += "Q2: 1暂缓\n"
        content += "新增：写论文 Q1\n"
        content += "暂缓任务1恢复到Q1\n"
        content += "\n⚠️ 提示：完成的任务会自动消失，不再重复出现"
        
        # 添加用户状态显示
        if user_game_data:
            content += "\n\n" + format_user_status(user_game_data)
            
            # 如果有惩罚，显示惩罚信息
            if punishment_result:
                content += "\n\n" + format_punishment_message(punishment_result)
            
            # 添加性格切换提示（简化）
            level = user_game_data.get('level', 1)
            if level >= 4:
                content += "\n\n💡 可用功能：切换AI性格"
                if level >= 8:
                    content += "（专业型/严格型）"
                if level >= 13:
                    content += "（专业型/严格型/毒舌型）"
            
            # 添加商店提示（简化）
            if level >= 13:
                content += "\n🛒 商店已解锁（格式：购买：道具名）"
            
            # 显示背包
            inventory_summary = get_user_inventory_summary(supabase_url, headers, user_email)
            if inventory_summary:
                content += inventory_summary
        
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
        
        # 发送邮件
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
