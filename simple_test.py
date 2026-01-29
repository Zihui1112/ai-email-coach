"""
简化测试脚本 - 直接测试各个组件功能
"""

import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

async def test_llm_parsing():
    """测试LLM解析功能"""
    print("🧠 测试LLM解析功能...")
    
    try:
        from main import LLMParser
        
        parser = LLMParser()
        
        test_content = "项目文档写了60%，属于Q1重要紧急。学习Python进度30%，Q2重要不紧急。"
        
        result = await parser.parse_reply(test_content, "test@example.com")
        
        print(f"   📝 输入: {test_content}")
        print(f"   🎯 解析结果:")
        print(f"      - 任务数量: {len(result.task_updates)}")
        print(f"      - 置信度: {result.confidence_score}")
        print(f"      - 是否修改计划: {result.is_plan_modification}")
        
        for i, task in enumerate(result.task_updates, 1):
            print(f"      - 任务{i}: {task.task_name} ({task.progress_percentage}%, Q{task.quadrant})")
        
        print("   ✅ LLM解析测试成功\n")
        return True
        
    except Exception as e:
        print(f"   ❌ LLM解析测试失败: {e}\n")
        return False

async def test_database_operations():
    """测试数据库操作"""
    print("🗄️ 测试数据库操作...")
    
    try:
        from main import DatabaseSyncer, TaskUpdate
        
        syncer = DatabaseSyncer()
        
        # 创建测试任务
        test_task = TaskUpdate(
            task_name="测试任务",
            progress_percentage=50,
            quadrant=1,
            action="create"
        )
        
        await syncer.sync_task_updates([test_task], "test@example.com")
        
        print("   ✅ 数据库操作测试成功\n")
        return True
        
    except Exception as e:
        print(f"   ❌ 数据库操作测试失败: {e}\n")
        return False

async def test_email_generation():
    """测试邮件生成功能"""
    print("📧 测试邮件生成功能...")
    
    try:
        from main import EmailGenerator, TaskUpdate
        
        generator = EmailGenerator()
        
        # 创建测试任务更新
        test_updates = [
            TaskUpdate(
                task_name="测试任务A",
                progress_percentage=60,
                quadrant=1,
                action="update"
            ),
            TaskUpdate(
                task_name="测试任务B", 
                progress_percentage=30,
                quadrant=2,
                action="update"
            )
        ]
        
        email_content = await generator.generate_feedback_email("test@example.com", test_updates)
        
        print("   📝 生成的邮件内容:")
        print("   " + "="*50)
        # 只显示前500个字符
        preview = email_content[:500] + "..." if len(email_content) > 500 else email_content
        print("   " + preview.replace("\n", "\n   "))
        print("   " + "="*50)
        
        print("   ✅ 邮件生成测试成功\n")
        return True
        
    except Exception as e:
        print(f"   ❌ 邮件生成测试失败: {e}\n")
        return False

async def test_progress_bar():
    """测试进度条格式"""
    print("📊 测试进度条格式...")
    
    try:
        from main import EmailGenerator
        
        generator = EmailGenerator()
        
        test_values = [0, 25, 50, 75, 100]
        
        for progress in test_values:
            bar = await generator.format_progress_bar(progress)
            print(f"   {progress:3d}%: {bar}")
        
        print("   ✅ 进度条格式测试成功\n")
        return True
        
    except Exception as e:
        print(f"   ❌ 进度条格式测试失败: {e}\n")
        return False

async def main():
    """主测试函数"""
    print("🚀 AI邮件督导系统 - 组件测试\n")
    
    tests = [
        ("进度条格式", test_progress_bar),
        ("数据库操作", test_database_operations), 
        ("邮件生成", test_email_generation),
        ("LLM解析", test_llm_parsing),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"🧪 开始测试: {test_name}")
        result = await test_func()
        results.append(result)
    
    # 显示总结
    passed = sum(results)
    total = len(results)
    
    print("="*60)
    print(f"📊 测试总结: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 所有测试都通过了！系统核心功能正常")
        print("\n下一步:")
        print("1. 运行 'python main.py' 启动服务")
        print("2. 配置Resend webhook（可选）")
        print("3. 开始使用邮件督导功能")
    else:
        print("⚠️ 有测试失败，请检查配置和依赖")
        print("\n建议:")
        print("1. 检查 .env 文件中的API密钥")
        print("2. 确保已在Supabase中创建数据库表")
        print("3. 检查网络连接")

if __name__ == "__main__":
    asyncio.run(main())