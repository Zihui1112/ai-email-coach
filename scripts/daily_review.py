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
    get_user_inventory_summary
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
        
        # 获取活跃任务
        query_url = f"{supabase_url}/rest/v1/tasks?user_email=eq.{user_email}&status=eq.active&select=*"
        db_response = requests.get(query_url, headers=headers, timeout=30)
        
        if db_response.status_code != 200:
            print(f"❌ 数据库查询失败: {db_response.status_code}")
            return False
        
        tasks = db_response.json()
        
        # 生成个性化问候语
        greeting = generate_personalized_greeting(consecutive_no_reply_days, is_weekend)
        
        # 生成消息内容
        content = f"{greeting}\n\n"
        
        # 添加四象限说明
        content += format_quadrant_guide() + "\n\n"
        
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
        
        # 根据连续未回复天数调整提示语
        if consecutive_no_reply_days >= 3:
            content += "\n\n⚠️ 重要提醒：\n"
            content += f"已经{consecutive_no_reply_days}天没有更新任务了！\n"
            content += "长时间不复盘可能会让任务失控，今天一定要回复哦！\n"
        elif consecutive_no_reply_days >= 1:
            content += "\n\n💡 温馨提示：\n"
            content += "定期复盘能帮助你更好地掌控任务进度~\n"
        
        content += "\n\n💬 请回复以下内容：\n"
        content += "1. 今天完成了哪些任务？进度如何？\n"
        content += "2. 明天计划做什么？\n"
        content += "3. 有哪些任务需要暂缓？\n"
        content += "\n📝 回复格式示例：\n"
        content += "• 更新进度：用户登录功能80% Q1\n"
        content += "• 标记完成：答辩模拟已完成 Q1（或：答辩模拟100% Q1）\n"
        content += "• 暂缓任务：前端优化暂缓\n"
        content += "\n⚠️ 重要：如果任务已完成，请明确说\"已完成\"或\"100%\"，否则会继续显示！"
        
        # 添加用户状态显示
        if user_game_data:
            content += "\n\n" + format_user_status(user_game_data)
            
            # 如果有惩罚，显示惩罚信息
            if punishment_result:
                content += "\n\n" + format_punishment_message(punishment_result)
            
            # 添加性格切换提示
            level = user_game_data.get('level', 1)
            if level >= 4:
                content += "\n\n💡 提示：你可以在回复中切换AI性格"
                content += "\n格式：切换性格：专业型"
                if level >= 8:
                    content += " / 严格型"
                if level >= 13:
                    content += " / 毒舌型"
            
            # 添加商店提示
            if level >= 13:
                content += "\n\n🛒 商店已解锁！"
                content += "\n格式：购买：道具名"
                content += "\n示例：购买：拖延对冲券"
            
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
