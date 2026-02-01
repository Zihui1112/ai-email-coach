"""
每周报告脚本 - GitHub Actions
"""
import os
import sys
import asyncio
import httpx
from datetime import datetime, timedelta
from supabase import create_client

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

async def send_weekly_report():
    """发送周报"""
    print(f"[{datetime.now()}] 开始生成周报")
    
    webhook_url = os.getenv("FEISHU_WEBHOOK_URL")
    user_email = os.getenv("EMAIL_163_USERNAME")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    try:
        # 连接数据库
        supabase = create_client(supabase_url, supabase_key)
        
        # 获取本周数据（过去7天）
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        
        # 查询本周完成的任务
        completed_response = supabase.table('tasks').select('*').eq(
            'user_email', user_email
        ).eq('status', 'completed').gte('updated_at', week_ago).execute()
        
        # 查询进行中的任务
        active_response = supabase.table('tasks').select('*').eq(
            'user_email', user_email
        ).eq('status', 'active').execute()
        
        # 查询待办池任务
        backlog_response = supabase.table('tasks').select('*').eq(
            'user_email', user_email
        ).eq('status', 'backlog').execute()
        
        completed_tasks = completed_response.data
        active_tasks = active_response.data
        backlog_tasks = backlog_response.data
        
        # 计算统计数据
        total_tasks = len(completed_tasks) + len(active_tasks)
        completion_rate = (len(completed_tasks) / total_tasks * 100) if total_tasks > 0 else 0
        
        # 按象限统计
        quadrant_stats = {1: 0, 2: 0, 3: 0, 4: 0}
        for task in completed_tasks:
            q = task.get('quadrant', 1)
            quadrant_stats[q] = quadrant_stats.get(q, 0) + 1
        
        # 生成周报内容
        content = "📊 本周任务统计报告\n\n"
        content += f"📅 统计周期: {datetime.now().strftime('%Y年%m月%d日')} 前7天\n\n"
        
        content += "📈 总体数据:\n"
        content += f"  ✅ 完成任务: {len(completed_tasks)} 个\n"
        content += f"  🔄 进行中: {len(active_tasks)} 个\n"
        content += f"  📦 待办池: {len(backlog_tasks)} 个\n"
        content += f"  📊 完成率: {completion_rate:.1f}%\n\n"
        
        content += "🎯 象限分布（已完成）:\n"
        content += f"  Q1（重要紧急）: {quadrant_stats.get(1, 0)} 个\n"
        content += f"  Q2（重要不紧急）: {quadrant_stats.get(2, 0)} 个\n"
        content += f"  Q3（不重要紧急）: {quadrant_stats.get(3, 0)} 个\n"
        content += f"  Q4（不重要不紧急）: {quadrant_stats.get(4, 0)} 个\n\n"
        
        if completed_tasks:
            content += "🏆 本周完成的任务:\n"
            for task in completed_tasks[:10]:  # 最多显示10个
                content += f"  ✅ {task['task_name']}\n"
            if len(completed_tasks) > 10:
                content += f"  ... 还有 {len(completed_tasks) - 10} 个\n"
            content += "\n"
        
        if active_tasks:
            content += "🔄 进行中的任务:\n"
            for task in active_tasks[:5]:  # 最多显示5个
                progress = task.get('progress', 0)
                filled = int(progress / 10)
                empty = 10 - filled
                bar = "■" * filled + "□" * empty
                content += f"  [{bar}] {task['task_name']} ({progress}%)\n"
            if len(active_tasks) > 5:
                content += f"  ... 还有 {len(active_tasks) - 5} 个\n"
            content += "\n"
        
        content += "💪 继续加油！下周见！"
        
        # 发送到飞书
        message = {
            "msg_type": "text",
            "content": {
                "text": f"📊 每周报告\n\n{content}"
            }
        }
        
        # 使用HTTP/1.1避免HTTP/2协议问题
        async with httpx.AsyncClient(timeout=30.0, http2=False) as client:
            response = await client.post(webhook_url, json=message)
            
            if response.status_code == 200:
                print("✅ 周报发送成功")
                return True
            else:
                print(f"❌ 周报发送失败: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ 生成周报失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(send_weekly_report())
    sys.exit(0 if success else 1)
