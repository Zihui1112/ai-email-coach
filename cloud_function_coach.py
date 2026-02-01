"""
云函数版AI督导系统
可部署到：腾讯云函数、阿里云函数计算、AWS Lambda
完全免费，支持定时触发和HTTP触发
"""

import json
import os
from datetime import datetime
import asyncio

# 云函数入口 - 定时触发（每晚22:00）
def daily_review_handler(event, context):
    """
    定时触发器：每天22:00执行
    腾讯云函数配置：Cron表达式 0 22 * * *
    """
    print(f"[{datetime.now()}] 定时任务触发：发送每日复盘")
    
    result = asyncio.run(send_daily_review())
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': '每日复盘已发送',
            'result': result
        })
    }

# 云函数入口 - HTTP触发（接收飞书消息）
def message_handler(event, context):
    """
    HTTP触发器：接收飞书机器人消息
    """
    print(f"[{datetime.now()}] HTTP触发：收到飞书消息")
    
    try:
        # 解析飞书消息
        body = json.loads(event.get('body', '{}'))
        message_content = body.get('content', {}).get('text', '')
        
        if not message_content:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': '消息内容为空'})
            }
        
        # 处理消息
        result = asyncio.run(process_message(message_content))
        
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': '消息处理成功',
                'result': result
            })
        }
    except Exception as e:
        print(f"错误: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

async def send_daily_review():
    """发送每日复盘提醒"""
    import httpx
    from main import db_syncer
    
    webhook_url = os.getenv("FEISHU_WEBHOOK_URL")
    user_email = os.getenv("EMAIL_163_USERNAME")
    
    # 获取今日任务
    tasks = await db_syncer.get_user_tasks(user_email)
    
    content = "🌙 晚上好！今天的任务完成情况如何？\n\n"
    content += "📋 今日任务清单：\n"
    
    if tasks:
        for task in tasks:
            progress = task.get('progress', 0)
            status = task.get('status', 'active')
            
            status_emoji = "✅" if status == "completed" else "🔄"
            progress_bar = generate_progress_bar(progress)
            
            content += f"\n{status_emoji} {task['task_name']}\n"
            content += f"   {progress_bar}\n"
    else:
        content += "\n暂无任务记录\n"
    
    content += "\n\n💬 请回复任务更新"
    
    # 发送到飞书
    message = {
        "msg_type": "text",
        "content": {
            "text": f"📊 每日复盘\n\n{content}"
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(webhook_url, json=message)
        return response.status_code == 200

async def process_message(message: str):
    """处理用户消息"""
    import httpx
    from main import llm_parser, db_syncer, email_generator
    
    webhook_url = os.getenv("FEISHU_WEBHOOK_URL")
    user_email = os.getenv("EMAIL_163_USERNAME")
    
    # 使用LLM解析
    parse_result = await llm_parser.parse_reply(message, user_email)
    
    if parse_result.task_updates:
        # 更新数据库
        await db_syncer.sync_task_updates(parse_result.task_updates, user_email)
        
        # 生成反馈
        feedback_content = await email_generator.generate_feedback_email(
            user_email, parse_result.task_updates
        )
        
        # 发送反馈到飞书
        response_message = {
            "msg_type": "text",
            "content": {
                "text": f"📊 任务更新反馈\n\n{feedback_content}"
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, json=response_message)
            return response.status_code == 200
    else:
        return False

def generate_progress_bar(progress: int) -> str:
    """生成进度条"""
    filled = int(progress / 10)
    empty = 10 - filled
    bar = "■" * filled + "□" * empty
    return f"进度：[{bar}] {progress}%"

# 本地测试入口
if __name__ == "__main__":
    print("本地测试模式")
    
    # 测试定时任务
    print("\n测试1: 发送每日复盘")
    result = daily_review_handler({}, {})
    print(f"结果: {result}")
    
    # 测试消息处理
    print("\n测试2: 处理用户消息")
    test_event = {
        'body': json.dumps({
            'content': {
                'text': '完成了用户登录功能80%，这是Q1任务'
            }
        })
    }
    result = message_handler(test_event, {})
    print(f"结果: {result}")
