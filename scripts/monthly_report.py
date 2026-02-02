"""
每月报告脚本 - GitHub Actions
"""
import os
import sys
import requests
from datetime import datetime, timedelta

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def send_monthly_report():
    """发送月报"""
    print(f"[{datetime.now()}] 开始生成月报")
    
    # 获取环境变量并清理空格和换行符
    webhook_url = os.getenv("FEISHU_WEBHOOK_URL", "").strip()
    user_email = os.getenv("EMAIL_163_USERNAME", "").strip()
    supabase_url = os.getenv("SUPABASE_URL", "").strip()
    supabase_key = os.getenv("SUPABASE_KEY", "").strip()
    
    try:
        # 使用 REST API 直接查询数据库（避免 HTTP/2 问题）
        headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json"
        }
        
        # 获取本月数据（过去30天）
        month_ago = (datetime.now() - timedelta(days=30)).isoformat()
        
        # 查询本月完成的任务
        completed_url = f"{supabase_url}/rest/v1/tasks?user_email=eq.{user_email}&status=eq.completed&updated_at=gte.{month_ago}&select=*"
        completed_response = requests.get(completed_url, headers=headers, timeout=30)
        
        # 查询所有任务
        all_url = f"{supabase_url}/rest/v1/tasks?user_email=eq.{user_email}&select=*"
        all_response = requests.get(all_url, headers=headers, timeout=30)
        
        if completed_response.status_code != 200 or all_response.status_code != 200:
            print(f"❌ 数据库查询失败")
            if completed_response.status_code == 401:
                print(f"完成任务查询: {completed_response.status_code} - {completed_response.text}")
                print("⚠️ 认证失败！请使用 service_role key")
            if all_response.status_code == 401:
                print(f"所有任务查询: {all_response.status_code} - {all_response.text}")
            return False
        
        completed_tasks = completed_response.json()
        all_tasks = all_response.json()
        
        # 统计数据
        total_completed = len(completed_tasks)
        total_active = len([t for t in all_tasks if t['status'] == 'active'])
        total_backlog = len([t for t in all_tasks if t['status'] == 'backlog'])
        
        # 按象限统计
        quadrant_stats = {1: 0, 2: 0, 3: 0, 4: 0}
        for task in completed_tasks:
            q = task.get('quadrant', 1)
            quadrant_stats[q] = quadrant_stats.get(q, 0) + 1
        
        # 计算平均进度
        if all_tasks:
            avg_progress = sum(t.get('progress', 0) for t in all_tasks) / len(all_tasks)
        else:
            avg_progress = 0
        
        # 生成月报内容
        content = "📊 本月任务统计报告\n\n"
        content += f"📅 统计周期: {datetime.now().strftime('%Y年%m月')}\n\n"
        
        content += "📈 总体数据:\n"
        content += f"  ✅ 完成任务: {total_completed} 个\n"
        content += f"  🔄 进行中: {total_active} 个\n"
        content += f"  📦 待办池: {total_backlog} 个\n"
        content += f"  📊 平均进度: {avg_progress:.1f}%\n\n"
        
        content += "🎯 完成任务象限分布:\n"
        content += f"  Q1（重要紧急）: {quadrant_stats.get(1, 0)} 个\n"
        content += f"  Q2（重要不紧急）: {quadrant_stats.get(2, 0)} 个\n"
        content += f"  Q3（不重要紧急）: {quadrant_stats.get(3, 0)} 个\n"
        content += f"  Q4（不重要不紧急）: {quadrant_stats.get(4, 0)} 个\n\n"
        
        # 分析
        content += "💡 本月分析:\n"
        if quadrant_stats.get(1, 0) > total_completed * 0.5:
            content += "  ⚠️ Q1任务占比较高，建议提前规划，减少紧急任务\n"
        if quadrant_stats.get(2, 0) > total_completed * 0.3:
            content += "  ✅ Q2任务执行良好，保持重要但不紧急的任务规划\n"
        if total_completed >= 20:
            content += "  🎉 本月完成任务数量优秀！\n"
        elif total_completed >= 10:
            content += "  👍 本月完成任务数量不错！\n"
        else:
            content += "  💪 下个月继续努力！\n"
        
        content += "\n🚀 下个月继续加油！"
        
        # 发送到飞书
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
                print("✅ 月报发送成功")
                return True
            else:
                print(f"❌ 飞书返回错误: {result}")
                return False
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            return False
                
    except Exception as e:
        print(f"❌ 生成月报失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = send_monthly_report()
    sys.exit(0 if success else 1)
