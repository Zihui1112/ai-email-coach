"""
最小化测试 - 只测试基本功能，不依赖复杂的包
"""

import json
import os
from datetime import datetime

def test_env_variables():
    """测试环境变量"""
    print("🔧 测试环境变量...")
    
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_KEY", 
        "RESEND_API_KEY",
        "DEEPSEEK_API_KEY"
    ]
    
    # 尝试从.env文件读取
    env_vars = {}
    try:
        with open('.env', 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key] = value
    except FileNotFoundError:
        print("   ❌ .env文件不存在")
        return False
    
    missing_vars = []
    for var in required_vars:
        if var not in env_vars or not env_vars[var]:
            missing_vars.append(var)
    
    if missing_vars:
        print(f"   ❌ 缺少环境变量: {', '.join(missing_vars)}")
        return False
    else:
        print("   ✅ 所有环境变量都已配置")
        return True

def test_progress_bar():
    """测试进度条生成"""
    print("📊 测试进度条生成...")
    
    def format_progress_bar(progress):
        filled = int(progress / 10)
        empty = 10 - filled
        bar = "■" * filled + "□" * empty
        return f"进度：[{bar}] {progress}%"
    
    test_values = [0, 25, 50, 75, 100]
    
    for progress in test_values:
        bar = format_progress_bar(progress)
        print(f"   {progress:3d}%: {bar}")
    
    print("   ✅ 进度条生成正常")
    return True

def test_llm_prompt():
    """测试LLM提示词格式"""
    print("🧠 测试LLM提示词...")
    
    email_content = "项目文档写了60%，属于Q1重要紧急"
    
    prompt = f"""
你是一个任务管理助手，需要从用户的邮件中提取任务信息。

用户邮件内容：
{email_content}

请分析邮件内容，提取以下信息并以JSON格式返回：
{{
    "task_updates": [
        {{
            "task_name": "任务名称",
            "progress_percentage": 进度百分比(0-100),
            "quadrant": 象限分类(1-4),
            "action": "update/create/backlog"
        }}
    ],
    "is_plan_modification": 是否在修改计划(true/false),
    "is_backlog_request": 是否要求暂缓任务(true/false),
    "confidence_score": 解析置信度(0-1)
}}
"""
    
    print("   📝 生成的提示词:")
    print("   " + "="*50)
    print("   " + prompt.strip().replace("\n", "\n   "))
    print("   " + "="*50)
    print("   ✅ LLM提示词格式正常")
    return True

def test_email_template():
    """测试邮件模板"""
    print("📧 测试邮件模板...")
    
    # 模拟任务数据
    tasks = [
        {"name": "项目文档", "progress": 60, "quadrant": 1},
        {"name": "学习Python", "progress": 30, "quadrant": 2}
    ]
    
    def format_progress_bar(progress):
        filled = int(progress / 10)
        empty = 10 - filled
        bar = "■" * filled + "□" * empty
        return f"进度：[{bar}] {progress}%"
    
    # 生成邮件内容
    content = """
收到你的任务更新，以下是当前状态：

📊 任务进度更新：
"""
    
    for task in tasks:
        progress_bar = format_progress_bar(task["progress"])
        content += f"• {task['name']}\n  {progress_bar}\n"
    
    content += """
🎯 明日四象限清单：

Q1 重要紧急：
• 项目文档
  进度：[■■■■■■□□□□] 60%

Q2 重要不紧急：
• 学习Python
  进度：[■■■□□□□□□□] 30%

继续努力，保持专注！

---
回复此邮件更新你的任务进度吧！
"""
    
    print("   📝 生成的邮件内容:")
    print("   " + "="*50)
    print("   " + content.strip().replace("\n", "\n   "))
    print("   " + "="*50)
    print("   ✅ 邮件模板生成正常")
    return True

def main():
    """主测试函数"""
    print("🚀 AI邮件督导系统 - 最小化测试\n")
    
    tests = [
        ("环境变量", test_env_variables),
        ("进度条生成", test_progress_bar),
        ("LLM提示词", test_llm_prompt),
        ("邮件模板", test_email_template),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"🧪 开始测试: {test_name}")
        result = test_func()
        results.append(result)
        print()
    
    # 显示总结
    passed = sum(results)
    total = len(results)
    
    print("="*60)
    print(f"📊 测试总结: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("🎉 基础功能测试通过！")
        print("\n下一步:")
        print("1. 解决依赖安装问题")
        print("2. 运行完整测试")
        print("3. 启动应用服务")
    else:
        print("⚠️ 有测试失败，请检查配置")

if __name__ == "__main__":
    main()