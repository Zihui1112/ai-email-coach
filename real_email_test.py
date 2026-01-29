"""
真实邮件测试 - 使用你的真实邮箱地址测试邮件发送
"""

import asyncio
import os
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

async def test_real_email():
    """使用真实邮箱测试邮件发送"""
    print("📧 真实邮件发送测试\n")
    
    # 获取你的真实邮箱
    your_email = input("请输入你的邮箱地址（用于接收测试邮件）: ").strip()
    
    if not your_email or "@" not in your_email:
        print("❌ 请输入有效的邮箱地址")
        return
    
    print(f"📮 将发送测试邮件到: {your_email}")
    
    try:
        # 导入通知管理器
        from notification_manager import notification_manager
        
        # 测试邮件内容
        subject = "🧪 AI邮件督导系统 - 真实测试"
        content = f"""
你好！

这是来自AI邮件督导系统的真实测试邮件。

📊 模拟任务进度更新：

• 完成项目文档
  进度：[■■■■■■□□□□] 60%

• 学习新技术
  进度：[■■■□□□□□□□] 30%

🎯 明日四象限清单：

Q1 重要紧急：
• 完成项目文档 (60%)

Q2 重要不紧急：
• 学习新技术 (30%)

📝 待办池推荐：
• 整理工作环境 - 要重新开始吗？

继续努力，保持专注！

---
测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
发送到: {your_email}

如果你收到这封邮件，说明AI邮件督导系统的邮件功能正常工作！
        """.strip()
        
        print("🔄 正在发送邮件...")
        
        # 发送邮件
        results = await notification_manager.send_notification(your_email, subject, content)
        
        # 显示结果
        print(f"\n📊 发送结果:")
        print("="*50)
        
        success_count = 0
        for platform, success in results.items():
            status = "✅ 成功" if success else "❌ 失败"
            print(f"  {platform}: {status}")
            if success:
                success_count += 1
        
        print("="*50)
        
        if success_count > 0:
            print(f"🎉 邮件发送成功！({success_count} 个平台)")
            print(f"\n📬 请检查你的邮箱: {your_email}")
            print("💡 提示:")
            print("  - 检查收件箱")
            print("  - 检查垃圾邮件/垃圾箱")
            print("  - 可能需要等待几分钟")
            print(f"  - 也可以在Resend控制台查看: https://resend.com/emails")
        else:
            print("❌ 邮件发送失败")
            print("\n🔧 可能的原因:")
            print("  - Resend API密钥无效")
            print("  - 网络连接问题")
            print("  - 邮箱地址格式错误")
            
            # 显示详细错误信息
            print(f"\n🔍 详细信息:")
            print(f"  - 目标邮箱: {your_email}")
            print(f"  - Resend API Key: {'已配置' if os.getenv('RESEND_API_KEY') else '未配置'}")
            
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("请确保已安装依赖: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ 发送失败: {e}")
        print(f"错误类型: {type(e).__name__}")

async def test_resend_directly():
    """直接测试Resend API"""
    print("🔧 直接测试Resend API\n")
    
    your_email = input("请输入你的邮箱地址: ").strip()
    
    if not your_email or "@" not in your_email:
        print("❌ 请输入有效的邮箱地址")
        return
    
    try:
        import httpx
        
        resend_api_key = os.getenv("RESEND_API_KEY")
        if not resend_api_key:
            print("❌ 未找到RESEND_API_KEY环境变量")
            return
        
        print("🔄 直接调用Resend API...")
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {resend_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "from": "AI督导 <onboarding@resend.dev>",  # 使用Resend默认发件人
                    "to": [your_email],
                    "subject": "🧪 AI邮件督导系统 - 直接API测试",
                    "text": f"""
这是直接通过Resend API发送的测试邮件。

收件人: {your_email}
发送时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

如果你收到这封邮件，说明Resend API配置正确！

---
AI邮件督导系统
                    """.strip()
                }
            )
            
            print(f"📡 API响应状态: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ 邮件发送成功！")
                print(f"📧 邮件ID: {result.get('id', 'N/A')}")
                print(f"📬 请检查邮箱: {your_email}")
                print("💡 也可以在Resend控制台查看发送状态")
            else:
                print("❌ 邮件发送失败")
                print(f"错误响应: {response.text}")
                
                if response.status_code == 401:
                    print("🔑 可能是API密钥无效")
                elif response.status_code == 422:
                    print("📝 可能是请求参数错误")
                    
    except Exception as e:
        print(f"❌ API调用失败: {e}")

def main():
    """主菜单"""
    print("🚀 AI邮件督导系统 - 真实邮件测试\n")
    
    options = [
        "使用通知管理器测试（推荐）",
        "直接测试Resend API",
        "查看当前配置",
        "退出"
    ]
    
    while True:
        print("请选择测试方式:")
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")
        
        try:
            choice = int(input("\n请输入选择 (数字): "))
            
            if choice == 1:
                asyncio.run(test_real_email())
            elif choice == 2:
                asyncio.run(test_resend_directly())
            elif choice == 3:
                print("\n🔧 当前配置:")
                config_items = [
                    ("RESEND_API_KEY", "Resend API密钥"),
                    ("EMAIL_163_USERNAME", "163邮箱"),
                    ("EMAIL_QQ_USERNAME", "QQ邮箱"),
                    ("FEISHU_WEBHOOK_URL", "飞书机器人"),
                    ("WECHAT_WEBHOOK_URL", "企业微信机器人"),
                ]
                
                for env_var, description in config_items:
                    value = os.getenv(env_var)
                    if value and value not in ["your-webhook-secret-will-be-generated"]:
                        # 只显示前几位和后几位，保护隐私
                        if len(value) > 10:
                            masked_value = value[:6] + "..." + value[-4:]
                        else:
                            masked_value = value[:3] + "..."
                        print(f"  ✅ {description}: {masked_value}")
                    else:
                        print(f"  ❌ {description}: 未配置")
            elif choice == 4:
                print("👋 再见！")
                break
            else:
                print("❌ 无效选择，请重新输入")
                
        except ValueError:
            print("❌ 请输入数字")
        except KeyboardInterrupt:
            print("\n👋 再见！")
            break
        
        input("\n按回车键继续...")
        print("\n" + "="*60 + "\n")

if __name__ == "__main__":
    main()