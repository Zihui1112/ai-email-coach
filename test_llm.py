"""
测试DeepSeek LLM解析功能
"""
import os
import asyncio
import httpx
import json
from dotenv import load_dotenv

load_dotenv()

async def test_deepseek():
    """测试DeepSeek API"""
    print("="*60)
    print("🧪 测试DeepSeek LLM解析")
    print("="*60)
    print()
    
    api_key = os.getenv("DEEPSEEK_API_KEY")
    
    if not api_key:
        print("❌ 未配置DEEPSEEK_API_KEY")
        return False
    
    print(f"✅ API Key已配置: {api_key[:10]}...")
    print()
    
    # 测试内容
    test_content = "完成了用户登录功能80%，这是Q1任务"
    
    prompt = f"""
你是一个任务管理助手，需要从用户的邮件中提取任务信息。

用户邮件内容：
{test_content}

请分析邮件内容，提取以下信息并以JSON格式返回：
{{
    "task_updates": [
        {{
            "task_name": "任务名称",
            "progress_percentage": 进度百分比(0-100),
            "quadrant": 象限分类(1-4),
            "action": "update"
        }}
    ],
    "is_plan_modification": false,
    "is_backlog_request": false,
    "confidence_score": 0.9
}}

象限说明：
Q1(1): 重要且紧急
Q2(2): 重要但不紧急  
Q3(3): 不重要但紧急
Q4(4): 不重要且不紧急

只返回JSON，不要其他内容。
"""
    
    print(f"📝 测试内容: {test_content}")
    print()
    print("🔄 调用DeepSeek API...")
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.1
                }
            )
            
            print(f"📡 HTTP状态码: {response.status_code}")
            print()
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                print("✅ API调用成功")
                print()
                print("📄 LLM返回内容:")
                print("-" * 60)
                print(content)
                print("-" * 60)
                print()
                
                # 尝试解析JSON
                try:
                    # 清理可能的markdown代码块标记
                    if content.startswith("```"):
                        content = content.split("```")[1]
                        if content.startswith("json"):
                            content = content[4:]
                    
                    parsed_data = json.loads(content.strip())
                    
                    print("✅ JSON解析成功")
                    print()
                    print("📊 解析结果:")
                    print(json.dumps(parsed_data, indent=2, ensure_ascii=False))
                    print()
                    
                    if parsed_data.get("task_updates"):
                        print(f"✅ 识别到 {len(parsed_data['task_updates'])} 个任务")
                        for task in parsed_data["task_updates"]:
                            print(f"   - 任务: {task.get('task_name')}")
                            print(f"     进度: {task.get('progress_percentage')}%")
                            print(f"     象限: Q{task.get('quadrant')}")
                        return True
                    else:
                        print("⚠️ 未识别到任务")
                        return False
                        
                except json.JSONDecodeError as e:
                    print(f"❌ JSON解析失败: {e}")
                    print(f"   原始内容: {content[:200]}...")
                    return False
            else:
                print(f"❌ API调用失败")
                print(f"   状态码: {response.status_code}")
                print(f"   响应: {response.text}")
                return False
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_multiple_examples():
    """测试多个示例"""
    examples = [
        "完成了用户登录功能80%，这是Q1任务",
        "今天做了数据库设计50%，Q2任务，明天继续",
        "用户登录100%完成了，数据库设计刚开始10%",
        "暂缓一下支付功能，先做其他的",
    ]
    
    print("\n" + "="*60)
    print("🧪 测试多个示例")
    print("="*60)
    
    for i, example in enumerate(examples, 1):
        print(f"\n测试 {i}/{len(examples)}: {example}")
        print("-" * 60)
        
        # 这里可以调用解析函数
        # 为了简化，只打印示例
        
    print("\n提示：运行 test_deepseek() 查看详细解析过程")

if __name__ == "__main__":
    print("选择测试模式：")
    print("1. 测试单个示例（详细）")
    print("2. 测试多个示例")
    print()
    
    choice = input("请选择 (1/2): ").strip()
    
    if choice == "1":
        asyncio.run(test_deepseek())
    elif choice == "2":
        asyncio.run(test_multiple_examples())
    else:
        print("运行默认测试...")
        asyncio.run(test_deepseek())
