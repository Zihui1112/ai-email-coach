"""
每日跟进脚本 - 在23:00提醒用户更新任务
"""
import os
import sys
import requests
from datetime import datetime

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def send_followup_reminder():
    """发送跟进提醒"""
    print(f"[{datetime.now()}] 发送每日跟进提醒")
    
    webhook_url = os.getenv("FEISHU_WEBHOOK_URL", "").strip()
    
    if not webhook_url:
        print("❌ 飞书 Webhook URL 未配置")
        return False
    
    # 生成提醒消息
    content = "🌙 晚安！今天的任务都完成了吗？\n\n"
    content += "如果有任务更新，请：\n\n"
    content += "📝 方式1：直接在这里回复（推荐）\n"
    content += "例如：完成了用户登录功能90%，这是Q1任务\n\n"
    content += "🔗 方式2：前往 GitHub Actions\n"
    content += "https://github.com/Zihui1112/ai-email-coach/actions\n"
    content += "选择 '处理用户回复' → Run workflow\n\n"
    content += "💤 如果今天没有更新，就好好休息吧！\n"
    content += "明天继续加油！"
    
    message = {
        "msg_type": "text",
        "content": {
            "text": f"📊 每日跟进\n\n{content}"
        }
    }
    
    try:
        response = requests.post(webhook_url, json=message, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            if result.get("StatusCode") == 0:
                print("✅ 跟进提醒发送成功")
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

if __name__ == "__main__":
    success = send_followup_reminder()
    sys.exit(0 if success else 1)
