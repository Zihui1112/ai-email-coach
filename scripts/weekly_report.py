"""
每周报告脚本 - GitHub Actions
v2.0 - 故事叙述风格 + ASCII图表可视化
"""
import os
import sys
import requests
from datetime import datetime, timedelta

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gamification_utils import get_user_gamification_data

def generate_ascii_bar_chart(data, max_width=20):
    """生成ASCII柱状图"""
    if not data:
        return ""
    
    max_value = max(data.values()) if data.values() else 1
    chart = ""
    
    for label, value in data.items():
        bar_length = int((value / max_value) * max_width) if max_value > 0 else 0
        bar = "█" * bar_length
        chart += f"{label}: {bar} {value}\n"
    
    return chart

def generate_ascii_trend_chart(values, width=30, height=8):
    """生成ASCII趋势图"""
    if not values or len(values) < 2:
        return ""
    
    max_val = max(values) if max(values) > 0 else 1
    min_val = min(values)
    
    # 归一化到0-height范围
    normalized = []
    for v in values:
        if max_val == min_val:
            normalized.append(height // 2)
        else:
            normalized.append(int(((v - min_val) / (max_val - min_val)) * (height - 1)))
    
    # 生成图表
    chart = ""
    for row in range(height - 1, -1, -1):
        line = ""
        for val in normalized:
            if val >= row:
                line += "●"
            else:
                line += " "
        chart += line + "\n"
    
    # 添加底部轴线
    chart += "─" * len(values) + "\n"
    
    return chart

def generate_story_narrative(stats, user_data):
    """生成故事叙述风格的周报"""
    level = user_data.get('level', 1)
    coins = user_data.get('coins', 0)
    consecutive_q1_days = user_data.get('consecutive_q1_days', 0)
    
    completed_count = stats['completed_count']
    active_count = stats['active_count']
    paused_count = stats['paused_count']
    completion_rate = stats['completion_rate']
    quadrant_stats = stats['quadrant_stats']
    
    # 开场白
    story = "📖 本周成长故事\n\n"
    
    # 第一段：总体表现
    if completion_rate >= 80:
        story += f"这一周，你像一位勤奋的冒险者，在任务的世界里披荆斩棘。完成了 {completed_count} 个任务，完成率高达 {completion_rate:.0f}%！这样的表现，足以让人刮目相看。\n\n"
    elif completion_rate >= 60:
        story += f"这一周，你稳步前行，完成了 {completed_count} 个任务，完成率 {completion_rate:.0f}%。虽然还有提升空间，但你的努力已经开始显现成果。\n\n"
    elif completion_rate >= 40:
        story += f"这一周，你完成了 {completed_count} 个任务，完成率 {completion_rate:.0f}%。看起来遇到了一些挑战，但别气馁，每一步都是成长。\n\n"
    else:
        story += f"这一周，你完成了 {completed_count} 个任务，完成率 {completion_rate:.0f}%。似乎遇到了不少困难，但记住：最黑暗的时刻往往就在黎明之前。\n\n"
    
    # 第二段：象限分析
    story += "📊 任务象限分布\n\n"
    story += generate_ascii_bar_chart({
        "Q1 重要紧急": quadrant_stats.get(1, 0),
        "Q2 重要非紧急": quadrant_stats.get(2, 0),
        "Q3 紧急非重要": quadrant_stats.get(3, 0),
        "Q4 非紧急非重要": quadrant_stats.get(4, 0)
    })
    story += "\n"
    
    # 象限分析评论
    q1_ratio = quadrant_stats.get(1, 0) / completed_count if completed_count > 0 else 0
    q2_ratio = quadrant_stats.get(2, 0) / completed_count if completed_count > 0 else 0
    
    if q1_ratio > 0.5:
        story += "⚠️ 你的Q1任务占比超过50%，说明很多重要的事情都变成了紧急任务。建议提前规划，把更多精力放在Q2任务上，避免总是救火。\n\n"
    elif q2_ratio > 0.3:
        story += "✅ 你在Q2任务上投入了不少精力，这是一个很好的习惯！重要但不紧急的事情往往能带来长期价值。\n\n"
    else:
        story += "💡 建议多关注Q2任务（重要但不紧急），这些任务能帮助你建立长期优势，避免陷入Q1的紧急循环。\n\n"
    
    # 第三段：成长数据
    story += f"🎮 成长数据\n"
    story += f"等级：LV{level}\n"
    story += f"金币：{coins} Coin\n"
    
    if consecutive_q1_days > 0:
        story += f"Q1连击：{consecutive_q1_days}天 🔥\n"
    
    story += "\n"
    
    # 第四段：进行中的任务
    if active_count > 0:
        story += f"🔄 你还有 {active_count} 个任务在进行中，继续保持专注，一步一步完成它们。\n\n"
    
    if paused_count > 0:
        story += f"⏸️ 暂缓池里有 {paused_count} 个任务在等待，别忘了定期回顾，看看是否可以重新启动。\n\n"
    
    # 结尾：激励语
    if completion_rate >= 80:
        story += "💪 继续保持这样的节奏，你正在成为更好的自己！下周见！"
    elif completion_rate >= 60:
        story += "🌟 稳扎稳打，持续进步。下周让我们一起冲击更高的完成率！"
    else:
        story += "🚀 每一次尝试都是进步，下周让我们重新出发，创造更好的成绩！"
    
    return story

def send_weekly_report():
    """发送周报"""
    print(f"[{datetime.now()}] 开始生成周报")
    
    # 获取环境变量
    webhook_url = os.getenv("FEISHU_WEBHOOK_URL", "").strip()
    user_email = os.getenv("EMAIL_163_USERNAME", "").strip()
    email_password = os.getenv("EMAIL_163_PASSWORD", "").strip()
    supabase_url = os.getenv("SUPABASE_URL", "").strip()
    supabase_key = os.getenv("SUPABASE_KEY", "").strip()
    
    try:
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json"
        }
        
        # 获取本周数据（过去7天）
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        
        # 查询本周完成的任务
        completed_url = f"{supabase_url}/rest/v1/tasks?user_email=eq.{user_email}&status=eq.completed&is_deleted=eq.true&updated_at=gte.{week_ago}&select=*"
        completed_response = requests.get(completed_url, headers=headers, timeout=30)
        
        # 查询进行中的任务
        active_url = f"{supabase_url}/rest/v1/tasks?user_email=eq.{user_email}&status=eq.active&is_deleted=eq.false&select=*"
        active_response = requests.get(active_url, headers=headers, timeout=30)
        
        # 查询暂缓任务
        paused_url = f"{supabase_url}/rest/v1/tasks?user_email=eq.{user_email}&status=eq.paused&is_deleted=eq.false&select=*"
        paused_response = requests.get(paused_url, headers=headers, timeout=30)
        
        if completed_response.status_code != 200 or active_response.status_code != 200 or paused_response.status_code != 200:
            print(f"❌ 数据库查询失败")
            return False
        
        completed_tasks = completed_response.json()
        active_tasks = active_response.json()
        paused_tasks = paused_response.json()
        
        # 计算统计数据
        total_tasks = len(completed_tasks) + len(active_tasks)
        completion_rate = (len(completed_tasks) / total_tasks * 100) if total_tasks > 0 else 0
        
        # 按象限统计
        quadrant_stats = {1: 0, 2: 0, 3: 0, 4: 0}
        for task in completed_tasks:
            q = task.get('quadrant', 1)
            quadrant_stats[q] = quadrant_stats.get(q, 0) + 1
        
        # 获取用户游戏化数据
        user_data = get_user_gamification_data(supabase_url, headers, user_email)
        
        # 构建统计数据
        stats = {
            'completed_count': len(completed_tasks),
            'active_count': len(active_tasks),
            'paused_count': len(paused_tasks),
            'completion_rate': completion_rate,
            'quadrant_stats': quadrant_stats
        }
        
        # 生成故事叙述
        content = generate_story_narrative(stats, user_data)
        
        # 发送到飞书
        feishu_success = False
        if webhook_url:
            message = {
                "msg_type": "text",
                "content": {
                    "text": f"📊 每周报告\n\n{content}"
                }
            }
            
            response = requests.post(webhook_url, json=message, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("StatusCode") == 0:
                    print("✅ 飞书周报发送成功")
                    feishu_success = True
                else:
                    print(f"❌ 飞书返回错误: {result}")
            else:
                print(f"❌ 飞书HTTP请求失败: {response.status_code}")
        
        # 发送邮件
        if email_password:
            try:
                import smtplib
                from email.mime.text import MIMEText
                from email.mime.multipart import MIMEMultipart
                
                print("发送周报邮件...")
                
                msg = MIMEMultipart()
                msg['From'] = user_email
                msg['To'] = user_email
                msg['Subject'] = "📊 每周成长报告"
                
                email_body = f"每周报告\n\n{content}\n\n---\n本周报告由AI邮件教练自动生成"
                msg.attach(MIMEText(email_body, 'plain', 'utf-8'))
                
                server = smtplib.SMTP_SSL("smtp.163.com", 465)
                server.login(user_email, email_password)
                server.send_message(msg)
                server.quit()
                
                print("✅ 周报邮件发送成功")
                return True
                
            except Exception as e:
                print(f"❌ 邮件发送失败: {e}")
                return feishu_success
        
        return feishu_success
                
    except Exception as e:
        print(f"❌ 生成周报失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = send_weekly_report()
    sys.exit(0 if success else 1)
