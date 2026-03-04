"""
每月报告脚本 - GitHub Actions
v2.0 - 故事叙述风格 + ASCII图表可视化
"""
import os
import sys
import requests
from datetime import datetime, timedelta

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from gamification_utils import get_user_gamification_data, LEVEL_EXP_REQUIRED

def generate_ascii_bar_chart(data, max_width=25):
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

def generate_level_progress_bar(current_level, current_exp):
    """生成等级进度条"""
    exp_required = LEVEL_EXP_REQUIRED.get(current_level, 2000)
    percentage = int((current_exp / exp_required) * 100) if exp_required > 0 else 0
    
    filled = int(percentage / 5)  # 20个字符宽度
    empty = 20 - filled
    
    bar = "█" * filled + "░" * empty
    return f"[{bar}] {percentage}%"

def generate_monthly_story(stats, user_data, level_changes):
    """生成月度故事叙述"""
    level = user_data.get('level', 1)
    current_exp = user_data.get('current_exp', 0)
    total_exp = user_data.get('total_exp', 0)
    coins = user_data.get('coins', 0)
    consecutive_q1_days = user_data.get('consecutive_q1_days', 0)
    
    completed_count = stats['completed_count']
    active_count = stats['active_count']
    paused_count = stats['paused_count']
    avg_completion_rate = stats['avg_completion_rate']
    quadrant_stats = stats['quadrant_stats']
    
    # 开场白
    story = "📖 本月成长史诗\n\n"
    story += f"时光荏苒，{datetime.now().strftime('%Y年%m月')}已经过去。让我们一起回顾这个月的成长历程。\n\n"
    
    # 第一章：总体成就
    story += "📜 第一章：成就回顾\n\n"
    
    if completed_count >= 30:
        story += f"这个月，你如同一位传奇冒险者，征服了 {completed_count} 个任务！这样的执行力，足以让人惊叹。"
    elif completed_count >= 20:
        story += f"这个月，你完成了 {completed_count} 个任务，表现优秀！你的坚持和努力正在结出果实。"
    elif completed_count >= 10:
        story += f"这个月，你完成了 {completed_count} 个任务，稳步前进。虽然还有提升空间，但你已经在正确的道路上。"
    else:
        story += f"这个月，你完成了 {completed_count} 个任务。看起来遇到了一些挑战，但记住：每一次尝试都是成长的机会。"
    
    story += f"平均完成率达到 {avg_completion_rate:.0f}%。\n\n"
    
    # 第二章：等级成长
    story += "⭐ 第二章：等级成长\n\n"
    story += f"当前等级：LV{level}\n"
    story += f"经验值：{generate_level_progress_bar(level, current_exp)}\n"
    story += f"总经验：{total_exp} EXP\n"
    story += f"金币：{coins} Coin\n\n"
    
    if level_changes > 0:
        story += f"🎉 本月你升了 {level_changes} 级！每一次升级都是对你努力的认可。\n\n"
    elif current_exp > 0:
        exp_required = LEVEL_EXP_REQUIRED.get(level, 2000)
        exp_needed = exp_required - current_exp
        story += f"💪 距离下一级还需要 {exp_needed} EXP，继续加油！\n\n"
    
    # 第三章：任务分析
    story += "📊 第三章：任务分析\n\n"
    story += "象限分布：\n"
    story += generate_ascii_bar_chart({
        "Q1 重要紧急": quadrant_stats.get(1, 0),
        "Q2 重要非紧急": quadrant_stats.get(2, 0),
        "Q3 紧急非重要": quadrant_stats.get(3, 0),
        "Q4 非紧急非重要": quadrant_stats.get(4, 0)
    })
    story += "\n"
    
    # 深度分析
    q1_ratio = quadrant_stats.get(1, 0) / completed_count if completed_count > 0 else 0
    q2_ratio = quadrant_stats.get(2, 0) / completed_count if completed_count > 0 else 0
    
    story += "💡 深度分析：\n"
    
    if q1_ratio > 0.5:
        story += "• Q1任务占比过高（超过50%），说明你经常处于救火状态\n"
        story += "• 建议：提前规划，把更多精力投入Q2任务，建立长期优势\n\n"
    elif q2_ratio > 0.3:
        story += "• Q2任务占比良好（超过30%），你在重要但不紧急的事情上投入了足够精力\n"
        story += "• 这是一个优秀的习惯，继续保持！\n\n"
    else:
        story += "• 建议增加Q2任务的投入，这些任务能帮助你避免陷入Q1的紧急循环\n"
        story += "• 长期来看，Q2任务能带来更大的价值\n\n"
    
    # 第四章：连击与坚持
    if consecutive_q1_days > 0:
        story += "🔥 第四章：连击记录\n\n"
        story += f"Q1连击：{consecutive_q1_days}天\n"
        
        if consecutive_q1_days >= 30:
            story += "惊人的坚持！连续一个月完成Q1任务，你的自律令人敬佩。\n\n"
        elif consecutive_q1_days >= 14:
            story += "出色的连击！连续两周完成Q1任务，你正在养成优秀的习惯。\n\n"
        elif consecutive_q1_days >= 7:
            story += "不错的连击！连续一周完成Q1任务，继续保持这个节奏。\n\n"
        else:
            story += "保持连击，让优秀成为习惯！\n\n"
    
    # 第五章：当前状态
    story += "📋 第五章：当前状态\n\n"
    
    if active_count > 0:
        story += f"进行中：{active_count} 个任务\n"
    
    if paused_count > 0:
        story += f"暂缓池：{paused_count} 个任务\n"
    
    story += "\n"
    
    # 尾声：展望未来
    story += "🌟 尾声：展望未来\n\n"
    
    if avg_completion_rate >= 80:
        story += "你的表现堪称优秀！下个月，让我们一起冲击更高的目标，创造新的记录！"
    elif avg_completion_rate >= 60:
        story += "你的进步有目共睹。下个月，让我们继续保持这个势头，追求更高的完成率！"
    else:
        story += "每一次尝试都是成长的机会。下个月，让我们重新出发，用行动书写新的篇章！"
    
    story += "\n\n💪 新的一月，新的开始。让我们一起加油！"
    
    return story

def send_monthly_report():
    """发送月报"""
    print(f"[{datetime.now()}] 开始生成月报")
    
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
        
        # 获取本月数据（过去30天）
        month_ago = (datetime.now() - timedelta(days=30)).isoformat()
        
        # 查询本月完成的任务
        completed_url = f"{supabase_url}/rest/v1/tasks?user_email=eq.{user_email}&status=eq.completed&is_deleted=eq.true&updated_at=gte.{month_ago}&select=*"
        completed_response = requests.get(completed_url, headers=headers, timeout=30)
        
        # 查询所有任务
        all_url = f"{supabase_url}/rest/v1/tasks?user_email=eq.{user_email}&is_deleted=eq.false&select=*"
        all_response = requests.get(all_url, headers=headers, timeout=30)
        
        if completed_response.status_code != 200 or all_response.status_code != 200:
            print(f"❌ 数据库查询失败")
            return False
        
        completed_tasks = completed_response.json()
        all_tasks = all_response.json()
        
        # 统计数据
        total_completed = len(completed_tasks)
        total_active = len([t for t in all_tasks if t['status'] == 'active'])
        total_paused = len([t for t in all_tasks if t['status'] == 'paused'])
        
        # 按象限统计
        quadrant_stats = {1: 0, 2: 0, 3: 0, 4: 0}
        for task in completed_tasks:
            q = task.get('quadrant', 1)
            quadrant_stats[q] = quadrant_stats.get(q, 0) + 1
        
        # 计算平均完成率
        total_tasks = total_completed + total_active
        avg_completion_rate = (total_completed / total_tasks * 100) if total_tasks > 0 else 0
        
        # 获取用户游戏化数据
        user_data = get_user_gamification_data(supabase_url, headers, user_email)
        
        # 计算等级变化（简化版，实际应该查询历史数据）
        level_changes = 0  # TODO: 从历史数据计算
        
        # 构建统计数据
        stats = {
            'completed_count': total_completed,
            'active_count': total_active,
            'paused_count': total_paused,
            'avg_completion_rate': avg_completion_rate,
            'quadrant_stats': quadrant_stats
        }
        
        # 生成月度故事
        content = generate_monthly_story(stats, user_data, level_changes)
        
        # 发送到飞书
        feishu_success = False
        if webhook_url:
            message = {
                "msg_type": "text",
                "content": {
                    "text": f"📊 每月报告\n\n{content}"
                }
            }
            
            response = requests.post(webhook_url, json=message, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("StatusCode") == 0:
                    print("✅ 飞书月报发送成功")
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
                
                print("发送月报邮件...")
                
                msg = MIMEMultipart()
                msg['From'] = user_email
                msg['To'] = user_email
                msg['Subject'] = "📊 每月成长史诗"
                
                email_body = f"每月报告\n\n{content}\n\n---\n本月报告由AI邮件教练自动生成"
                msg.attach(MIMEText(email_body, 'plain', 'utf-8'))
                
                server = smtplib.SMTP_SSL("smtp.163.com", 465)
                server.login(user_email, email_password)
                server.send_message(msg)
                server.quit()
                
                print("✅ 月报邮件发送成功")
                return True
                
            except Exception as e:
                print(f"❌ 邮件发送失败: {e}")
                return feishu_success
        
        return feishu_success
                
    except Exception as e:
        print(f"❌ 生成月报失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = send_monthly_report()
    sys.exit(0 if success else 1)
