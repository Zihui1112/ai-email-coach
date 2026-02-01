"""
GitHub Actions版AI督导系统
完全免费，每天自动运行
"""

import os
import asyncio
import httpx
from datetime import datetime

async def send_daily_review():
    """发送每日复盘提醒"""
    print(f"[{datetime.now()}] 开始发送每日复盘提醒")
    
    # 环境变量
    webhook_url = os.getenv("FEISHU_WEBHOOK_URL")
    user_email = os.getenv("EMAIL_163_USERNAME")
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    if not all([webhook_url, user_email, supabase_url, supabase_key]):
        print("❌ 环境变量未配置完整")
        return False
    
    try:
        # 连接数据库
        from supabase import create_client
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
        
        # 发送到飞书
        message = {
            "msg_type": "text",
            "content": {
                "text": f"📊 每日复盘\n\n{content}"
            }
        }
        
        # 使用HTTP/1.1避免HTTP/2协议问题
        async with httpx.AsyncClient(timeout=30.0, http2=False) as client:
            response = await client.post(webhook_url, json=message)
            
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

async def main():
    """主函数"""
    print("="*60)
    print("🤖 GitHub Actions AI督导系统")
    print("="*60)
    print()
    
    success = await send_daily_review()
    
    if success:
        print("\n✅ 任务执行成功")
        exit(0)
    else:
        print("\n❌ 任务执行失败")
        exit(1)

if __name__ == "__main__":
    asyncio.run(main())
