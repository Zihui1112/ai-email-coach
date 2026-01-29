"""
配置测试脚本 - 验证所有API连接是否正常
"""

import os
import asyncio
import httpx
from supabase import create_client
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

async def test_supabase():
    """测试Supabase连接"""
    try:
        supabase = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
        
        # 测试查询
        result = supabase.table("user_configs").select("*").limit(1).execute()
        print("✅ Supabase连接成功")
        return True
    except Exception as e:
        print(f"❌ Supabase连接失败: {e}")
        return False

async def test_deepseek():
    """测试DeepSeek API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": "Hello"}],
                    "max_tokens": 10
                }
            )
            
            if response.status_code == 200:
                print("✅ DeepSeek API连接成功")
                return True
            else:
                print(f"❌ DeepSeek API失败: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ DeepSeek API连接失败: {e}")
        return False

async def test_resend():
    """测试Resend API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.resend.com/domains",
                headers={
                    "Authorization": f"Bearer {os.getenv('RESEND_API_KEY')}"
                }
            )
            
            if response.status_code == 200:
                print("✅ Resend API连接成功")
                domains = response.json()
                if domains.get('data'):
                    print(f"   已配置域名: {[d['name'] for d in domains['data']]}")
                else:
                    print("   ⚠️  还没有配置域名，需要在Resend控制台添加")
                return True
            else:
                print(f"❌ Resend API失败: {response.status_code}")
                return False
    except Exception as e:
        print(f"❌ Resend API连接失败: {e}")
        return False

async def main():
    print("🔍 开始测试API配置...\n")
    
    results = []
    results.append(await test_supabase())
    results.append(await test_deepseek())
    results.append(await test_resend())
    
    print(f"\n📊 测试结果: {sum(results)}/3 个API配置成功")
    
    if all(results):
        print("🎉 所有配置都正常，可以启动应用了！")
        print("\n启动命令: python main.py")
    else:
        print("⚠️  请检查失败的API配置")

if __name__ == "__main__":
    asyncio.run(main())