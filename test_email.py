"""
邮件处理测试脚本 - 不需要配置webhook，直接测试邮件处理功能
"""

import asyncio
import json
import os
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入主应用模块
try:
    from main import process_email, EmailData
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    print("请确保main.py文件存在且没有语法错误")
    exit(1)

async def test_email_processing():
    """测试邮件处理功能"""
    
    # 模拟邮件数据
    test_emails = [
        {
            "from_email": "test@example.com",
            "subject": "任务进度更新",
            "content": "项目文档写了60%，属于Q1重要紧急。学习Python进度30%，Q2重要不紧急。",
            "message_id": "test_001"
        },
        {
            "from_email": "test@example.com", 
            "subject": "计划调整",
            "content": "我想调整一下计划，把学习Python改到Q1，进度提升到50%",
            "message_id": "test_002"
        },
        {
            "from_email": "test@example.com",
            "subject": "任务暂缓", 
            "content": "整理桌面这个任务先暂缓吧，以后再说",
            "message_id": "test_003"
        }
    ]
    
    print("🧪 开始测试邮件处理功能...\n")
    
    for i, email_data in enumerate(test_emails, 1):
        print(f"📧 测试邮件 {i}: {email_data['subject']}")
        print(f"   内容: {email_data['content']}")
        
        # 创建EmailData对象
        email = EmailData(
            from_email=email_data["from_email"],
            subject=email_data["subject"],
            content=email_data["content"],
            received_at=datetime.utcnow(),
            message_id=email_data["message_id"]
        )
        
        try:
            # 直接调用邮件处理函数
            print("   🔄 开始处理...")
            await process_email(email)
            print("   ✅ 处理成功")
            print("   📬 应该已发送反馈邮件（检查日志）\n")
        except Exception as e:
            print(f"   ❌ 处理失败: {e}")
            print(f"   详细错误: {type(e).__name__}\n")
        
        # 等待一下避免防抖
        print("   ⏳ 等待2秒避免防抖...")
        await asyncio.sleep(2)

async def test_webhook_endpoint():
    """测试webhook端点（使用HTTP POST请求）"""
    import httpx
    
    # 模拟Resend webhook数据格式
    webhook_data = {
        "type": "email.received",
        "created_at": datetime.utcnow().isoformat(),
        "data": {
            "message_id": "test_webhook_001",
            "from": {
                "email": "test@example.com",
                "name": "测试用户"
            },
            "to": [
                {
                    "email": "coach@yourdomain.com",
                    "name": "AI督导"
                }
            ],
            "subject": "Webhook测试邮件",
            "text": "这是一个webhook测试，任务A完成了80%，属于Q1象限。",
            "html": "<p>这是一个webhook测试，任务A完成了80%，属于Q1象限。</p>"
        }
    }
    
    print("🌐 测试webhook端点...\n")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/inbound-email",
                json=webhook_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                print("✅ Webhook端点测试成功")
                print(f"   响应: {response.json()}")
            else:
                print(f"❌ Webhook端点测试失败: {response.status_code}")
                print(f"   错误: {response.text}")
                
    except Exception as e:
        print(f"❌ Webhook端点连接失败: {e}")
        print("   请确保应用正在运行 (python main.py)")

async def main():
    """主测试函数"""
    print("🚀 AI邮件督导系统测试\n")
    
    # 选择测试模式
    print("请选择测试模式:")
    print("1. 直接测试邮件处理功能（推荐）")
    print("2. 测试webhook端点（需要应用运行）")
    
    choice = input("\n请输入选择 (1 或 2): ").strip()
    
    if choice == "1":
        await test_email_processing()
    elif choice == "2":
        await test_webhook_endpoint()
    else:
        print("无效选择，默认运行邮件处理测试")
        await test_email_processing()

if __name__ == "__main__":
    asyncio.run(main())