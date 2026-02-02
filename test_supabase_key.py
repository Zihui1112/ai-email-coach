"""
测试 Supabase API Key 是否有效
"""
import os
import requests

def test_supabase_connection():
    """测试 Supabase 连接"""
    supabase_url = os.getenv("SUPABASE_URL", "").strip()
    supabase_key = os.getenv("SUPABASE_KEY", "").strip()
    user_email = os.getenv("EMAIL_163_USERNAME", "").strip()
    
    print("=" * 60)
    print("测试 Supabase 连接")
    print("=" * 60)
    
    print(f"\nSupabase URL: {supabase_url}")
    print(f"User Email: {user_email}")
    print(f"API Key 长度: {len(supabase_key)}")
    print(f"API Key 前20字符: {supabase_key[:20]}...")
    print(f"API Key 后20字符: ...{supabase_key[-20:]}")
    
    # 解析 JWT 来检查 key 类型
    try:
        import base64
        import json
        
        # JWT 格式: header.payload.signature
        parts = supabase_key.split('.')
        if len(parts) == 3:
            # 解码 payload (第二部分)
            payload = parts[1]
            # 添加必要的 padding
            padding = 4 - len(payload) % 4
            if padding != 4:
                payload += '=' * padding
            
            decoded = base64.urlsafe_b64decode(payload)
            payload_data = json.loads(decoded)
            
            role = payload_data.get('role', 'unknown')
            print(f"\n✅ JWT 解析成功")
            print(f"Key 类型: {role}")
            
            if role == 'anon':
                print("⚠️ 警告：这是 anon key，需要使用 service_role key！")
            elif role == 'service_role':
                print("✅ 正确：这是 service_role key")
            else:
                print(f"⚠️ 未知的 role: {role}")
        else:
            print("❌ 无法解析 JWT 格式")
    except Exception as e:
        print(f"❌ JWT 解析失败: {e}")
    
    # 测试 API 调用
    print("\n" + "=" * 60)
    print("测试 API 调用")
    print("=" * 60)
    
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json"
    }
    
    # 测试查询
    query_url = f"{supabase_url}/rest/v1/tasks?user_email=eq.{user_email}&status=eq.active&select=*"
    
    print(f"\n请求 URL: {query_url}")
    print(f"请求头: apikey={supabase_key[:20]}...")
    
    try:
        response = requests.get(query_url, headers=headers, timeout=30)
        
        print(f"\n响应状态码: {response.status_code}")
        print(f"响应内容: {response.text[:500]}")
        
        if response.status_code == 200:
            print("\n✅ 连接成功！")
            tasks = response.json()
            print(f"查询到 {len(tasks)} 个任务")
            return True
        elif response.status_code == 401:
            print("\n❌ 认证失败 (401)")
            print("请检查：")
            print("1. 是否使用了 service_role key（不是 anon key）")
            print("2. key 是否完整（没有多余空格或换行符）")
            print("3. key 是否正确（从 Supabase 控制台重新复制）")
            return False
        else:
            print(f"\n❌ 请求失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"\n❌ 请求异常: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_supabase_connection()
    
    if not success:
        print("\n" + "=" * 60)
        print("如何获取正确的 service_role key：")
        print("=" * 60)
        print("1. 访问 https://supabase.com/dashboard")
        print("2. 选择你的项目")
        print("3. 点击左侧 Settings → API")
        print("4. 找到 'service_role' key（在 'anon' key 下方）")
        print("5. 点击 'Reveal' 显示完整 key")
        print("6. 复制整个 key（以 eyJ 开头）")
        print("7. 更新 .env 文件中的 SUPABASE_KEY")
        print("8. 更新 GitHub Secret 中的 SUPABASE_KEY")
