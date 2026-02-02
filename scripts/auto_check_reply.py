"""
自动检查并处理用户回复 - GitHub Actions
每天23:00自动运行，检查飞书回复并处理
"""
import os
import sys
import requests
from datetime import datetime

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def auto_check_and_process():
    """自动检查并处理回复"""
    print(f"[{datetime.now()}] 开始自动检查用户回复")
    
    # 获取环境变量
    webhook_url = os.getenv("FEISHU_WEBHOOK_URL", "").strip()
    user_email = os.getenv("EMAIL_163_USERNAME", "").strip()
    supabase_url = os.getenv("SUPABASE_URL", "").strip()
    supabase_key = os.getenv("SUPABASE_KEY", "").strip()
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    
    if not all([webhook_url, user_email, supabase_url, supabase_key, deepseek_api_key]):
        print("❌ 环境变量未配置完整")
        return False
    
    # 由于飞书机器人是单向的，我们需要用户通过其他方式提供回复
    # 这里我们提供一个提示消息
    message = {
        "msg_type": "text",
        "content": {
            "text": "🤖 自动检查提醒\n\n"
                   "如果你今天有任务更新，请：\n"
                   "1. 前往 GitHub Actions\n"
                   "2. 手动触发 '处理用户回复' workflow\n"
                   "3. 输入你的回复内容\n\n"
                   "或者明天继续！😊"
        }
    }
    
    try:
        response = requests.post(webhook_url, json=message, timeout=30)
        if response.status_code == 200:
            print("✅ 提醒消息发送成功")
            return True
        else:
            print(f"❌ 发送失败: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 发送失败: {e}")
        return False

if __name__ == "__main__":
    success = auto_check_and_process()
    sys.exit(0 if success else 1)
