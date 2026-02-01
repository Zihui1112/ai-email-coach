"""
每日复盘提醒脚本 - GitHub Actions
"""
import os
import sys
import requests
from datetime import datetime
from supabase import create_client

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def send_daily_review():
    """发送每日复盘提醒"""
    print(f"[{datetime.now()}] 开始发送每日复盘提醒")
    
    webhook_url = os.getenv("FEISHU_WEBHOOK_URL")
    user_email = os.getenv("EMAIL_163_USERNAME")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not all([webhook_url, user_email, supabase_url, supabase_key]):
        print("❌ 环境变量未配置完整，请检查.env文件")
        return False
    
    try:
        # 连接数据库
        supabase = create_client(supabase_url, supabase_key)
        
        # 获取今日任务
        response = supabase.table('tasks').select('*').eq('user_email', user_email).eq('status', 'active').execute()
        tasks = response.data
        
        # 生成消息内容
        content = "🌙 晚上好！今天的任务完成情况如何？\n\n"
        content += "📋 今日任务清单：\n"
        
        if tasks:
            for task in tasks:
                progress = task.get('progress', 0)
                task_name = task.get('task_name', '未命名任务')
                quadrant = task.get('quadrant', 'Q1')
                
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
        
        content += "\n\n💬 请回复以下内容：\n"
        content += "1. 今天完成了哪些任务？进度如何？\n"
        content += "2. 明天计划做什么？\n"
        content += "3. 有哪些任务需要暂缓？\n"
        content += "\n示例：完成了用户登录功能80%，明天做数据库设计Q2任务"
        
        # 发送到飞书 - 使用requests库
        message = {
            "msg_type": "text",
            "content": {
                "text": f"📊 每日复盘\n\n{content}"
            }
        }
        
        response = requests.post(webhook_url, json=message, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("StatusCode") == 0:
                print("✅ 每日复盘提醒发送成功")
                return True
            else:
                print(f"❌ 飞书返回错误: {result}")
                return False
        else:
            print(f"❌ HTTP请求失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 发送失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = send_daily_review()
    sys.exit(0 if success else 1)
