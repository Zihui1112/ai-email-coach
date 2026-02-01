"""
基于飞书的AI督导系统 - 完全云端运行
使用飞书机器人接收消息，定时发送复盘提醒
无需本地运行，无需webhook部署
"""

import os
import asyncio
from datetime import datetime, time
from dotenv import load_dotenv
import httpx
from typing import Dict, List

load_dotenv()

class FeishuCoach:
    def __init__(self):
        self.webhook_url = os.getenv("FEISHU_WEBHOOK_URL")
        self.user_email = os.getenv("EMAIL_163_USERNAME")
        
        print("🤖 飞书AI督导系统初始化完成")
        print(f"   用户邮箱: {self.user_email}")
    
    async def send_message(self, content: str, title: str = "AI督导提醒"):
        """发送飞书消息"""
        try:
            message = {
                "msg_type": "text",
                "content": {
                    "text": f"📊 {title}\n\n{content}"
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(self.webhook_url, json=message)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("StatusCode") == 0:
                        print(f"✅ 飞书消息发送成功")
                        return True
                    else:
                        print(f"❌ 飞书消息发送失败: {result}")
                        return False
                else:
                    print(f"❌ 飞书请求失败: {response.status_code}")
                    return False
        except Exception as e:
            print(f"❌ 发送消息异常: {e}")
            return False
    
    async def send_daily_review(self):
        """发送每日复盘提醒"""
        from main import db_syncer
        
        # 获取今日任务
        tasks = await db_syncer.get_user_tasks(self.user_email)
        
        content = "🌙 晚上好！今天的任务完成情况如何？\n\n"
        content += "📋 今日任务清单：\n"
        
        if tasks:
            for task in tasks:
                progress = task.get('progress', 0)
                status = task.get('status', 'active')
                quadrant = task.get('quadrant', 'Q1')
                
                status_emoji = "✅" if status == "completed" else "🔄"
                progress_bar = self.generate_progress_bar(progress)
                
                content += f"\n{status_emoji} {task['task_name']}\n"
                content += f"   {progress_bar}\n"
                content += f"   象限: {quadrant}\n"
        else:
            content += "\n暂无任务记录\n"
        
        content += "\n\n💬 请回复以下内容：\n"
        content += "1. 今天完成了哪些任务？进度如何？\n"
        content += "2. 明天计划做什么？\n"
        content += "3. 有哪些任务需要暂缓？\n"
        content += "\n示例：完成了用户登录功能80%，明天做数据库设计Q2任务"
        
        await self.send_message(content, "每日复盘")
    
    async def send_weekly_report(self):
        """发送周报"""
        from main import db_syncer
        
        # 获取本周统计
        stats = await db_syncer.get_weekly_stats(self.user_email)
        
        content = "📊 本周任务统计报告\n\n"
        content += f"✅ 完成任务: {stats.get('completed', 0)} 个\n"
        content += f"🔄 进行中: {stats.get('active', 0)} 个\n"
        content += f"📦 待办池: {stats.get('backlog', 0)} 个\n"
        content += f"📈 完成率: {stats.get('completion_rate', 0):.1f}%\n"
        
        await self.send_message(content, "周报")
    
    def generate_progress_bar(self, progress: int) -> str:
        """生成进度条"""
        filled = int(progress / 10)
        empty = 10 - filled
        bar = "■" * filled + "□" * empty
        return f"进度：[{bar}] {progress}%"
    
    async def process_user_message(self, message: str):
        """处理用户消息"""
        from main import llm_parser, db_syncer, email_generator
        
        print(f"\n📬 收到用户消息: {message[:100]}...")
        
        # 使用LLM解析
        parse_result = await llm_parser.parse_reply(message, self.user_email)
        
        if parse_result.task_updates:
            print(f"   🧠 AI解析结果: {len(parse_result.task_updates)} 个任务")
            
            # 更新数据库
            await db_syncer.sync_task_updates(parse_result.task_updates, self.user_email)
            
            # 生成反馈
            feedback_content = await email_generator.generate_feedback_email(
                self.user_email, parse_result.task_updates
            )
            
            # 发送反馈
            await self.send_message(feedback_content, "任务更新反馈")
        else:
            await self.send_message(
                "⚠️ 未能识别任务信息，请提供更清晰的描述\n\n"
                "示例：完成了用户登录功能80%，这是Q1任务",
                "提示"
            )
    
    async def schedule_daily_review(self):
        """定时发送每日复盘（22:00）"""
        print("⏰ 启动定时任务：每日22:00发送复盘提醒")
        
        while True:
            now = datetime.now()
            target_time = time(22, 0)  # 22:00
            
            # 计算距离下次22:00的秒数
            if now.time() < target_time:
                # 今天的22:00
                target = datetime.combine(now.date(), target_time)
            else:
                # 明天的22:00
                from datetime import timedelta
                target = datetime.combine(now.date() + timedelta(days=1), target_time)
            
            wait_seconds = (target - now).total_seconds()
            
            print(f"⏳ 下次复盘提醒时间: {target.strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"   等待 {wait_seconds/3600:.1f} 小时")
            
            # 等待到22:00
            await asyncio.sleep(wait_seconds)
            
            # 发送复盘提醒
            print(f"\n🔔 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 发送每日复盘提醒")
            await self.send_daily_review()
            
            # 等待1分钟，避免重复发送
            await asyncio.sleep(60)

async def main():
    """主函数"""
    print("="*60)
    print("🤖 飞书AI督导系统")
    print("="*60)
    print()
    
    coach = FeishuCoach()
    
    # 测试发送消息
    print("\n📤 发送测试消息...")
    await coach.send_message(
        "🎉 AI督导系统已启动！\n\n"
        "我会在每晚22:00提醒你复盘今日任务。\n"
        "你可以随时在飞书群里发送任务更新，我会自动处理。\n\n"
        "示例：完成了用户登录功能80%，明天做数据库设计Q2任务",
        "系统启动"
    )
    
    # 启动定时任务
    await coach.schedule_daily_review()

if __name__ == "__main__":
    asyncio.run(main())
