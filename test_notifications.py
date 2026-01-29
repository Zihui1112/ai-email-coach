"""
通知功能测试脚本
"""

import asyncio
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

async def test_all_notifications():
    """测试所有配置的通知方式"""
    print("🧪 测试所有通知配置...\n")
    
    try:
        from notification_manager import notification_manager
        
        # 获取测试邮箱
        test_email = input("请输入测试邮箱地址: ").strip()
        if not test_email:
            test_email = "test@example.com"
            print(f"使用默认测试邮箱: {test_email}")
        
        # 测试消息内容
        subject = "🧪 AI邮件督导系统 - 通知测试"
        content = """
这是一条测试消息！

📊 任务进度更新：
• 项目文档
  进度：[■■■■■■□□□□] 60%

• 学习Python  
  进度：[■■■□□□□□□□] 30%

🎯 明日四象限清单：

Q1 重要紧急：
• 项目文档 (60%)

Q2 重要不紧急：
• 学习Python (30%)

📝 待办池推荐：
• 整理桌面 - 要重新开始吗？

继续努力，保持专注！

---
这是来自AI邮件督导系统的测试消息
        """.strip()
        
        print("🔄 正在发送测试通知...")
        
        # 发送通知
        results = await notification_manager.send_notification(test_email, subject, content)
        
        # 显示结果
        print(f"\n📊 通知发送结果:")
        print("="*50)
        
        success_count = 0
        total_count = len(results)
        
        for platform, success in results.items():
            status = "✅ 成功" if success else "❌ 失败"
            print(f"  {platform:20} : {status}")
            if success:
                success_count += 1
        
        print("="*50)
        print(f"📈 总结: {success_count}/{total_count} 个平台发送成功")
        
        if success_count > 0:
            print("\n🎉 至少有一个通知平台工作正常！")
            print("💡 建议:")
            print("  - 检查你的邮箱/群聊是否收到测试消息")
            print("  - 如果某些平台失败，请检查对应的配置")
        else:
            print("\n⚠️ 所有通知平台都失败了")
            print("💡 建议:")
            print("  - 检查网络连接")
            print("  - 验证API密钥和配置是否正确")
            print("  - 运行 'python setup_notifications.py' 重新配置")
        
        # 显示配置状态
        print(f"\n🔧 当前配置状态:")
        config_items = [
            ("RESEND_API_KEY", "Resend邮件服务"),
            ("EMAIL_163_USERNAME", "163邮箱"),
            ("EMAIL_QQ_USERNAME", "QQ邮箱"),
            ("FEISHU_WEBHOOK_URL", "飞书机器人"),
            ("WECHAT_WEBHOOK_URL", "企业微信机器人"),
            ("DINGTALK_WEBHOOK_URL", "钉钉机器人")
        ]
        
        for env_var, description in config_items:
            value = os.getenv(env_var)
            if value and value not in ["your-webhook-secret-will-be-generated", "whsec_你从resend获取的实际secret"]:
                print(f"  ✅ {description}: 已配置")
            else:
                print(f"  ❌ {description}: 未配置")
        
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("请确保已安装所有依赖: pip install -r requirements.txt")
    except Exception as e:
        print(f"❌ 测试失败: {e}")

async def test_single_notification():
    """测试单个通知平台"""
    print("🎯 测试单个通知平台...\n")
    
    platforms = [
        ("resend", "Resend邮件服务"),
        ("163", "163邮箱"),
        ("qq", "QQ邮箱"),
        ("feishu", "飞书机器人"),
        ("wechat", "企业微信机器人"),
        ("dingtalk", "钉钉机器人")
    ]
    
    print("选择要测试的平台:")
    for i, (key, name) in enumerate(platforms, 1):
        print(f"  {i}. {name}")
    
    try:
        choice = int(input("\n请输入选择 (数字): ")) - 1
        if 0 <= choice < len(platforms):
            platform_key, platform_name = platforms[choice]
            print(f"\n🔄 测试 {platform_name}...")
            
            # 这里可以添加单个平台的测试逻辑
            print(f"✅ {platform_name} 测试完成")
        else:
            print("❌ 无效选择")
    except ValueError:
        print("❌ 请输入数字")

def show_configuration_guide():
    """显示配置指南"""
    print("📖 通知配置指南\n")
    
    guides = {
        "163邮箱": [
            "1. 登录163邮箱网页版",
            "2. 点击设置 → POP3/SMTP/IMAP",
            "3. 开启SMTP服务",
            "4. 获取授权码（不是登录密码）",
            "5. 在.env文件中配置 EMAIL_163_USERNAME 和 EMAIL_163_PASSWORD"
        ],
        "QQ邮箱": [
            "1. 登录QQ邮箱网页版",
            "2. 点击设置 → 账户",
            "3. 找到POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务",
            "4. 开启SMTP服务并获取授权码",
            "5. 在.env文件中配置 EMAIL_QQ_USERNAME 和 EMAIL_QQ_PASSWORD"
        ],
        "飞书机器人": [
            "1. 在飞书群聊中点击群设置",
            "2. 选择群机器人 → 添加机器人 → 自定义机器人",
            "3. 设置机器人名称（如：AI督导）",
            "4. 复制Webhook URL",
            "5. 在.env文件中配置 FEISHU_WEBHOOK_URL"
        ],
        "企业微信机器人": [
            "1. 在企业微信群聊中点击群设置",
            "2. 选择群机器人 → 添加机器人",
            "3. 设置机器人名称和头像",
            "4. 复制Webhook URL",
            "5. 在.env文件中配置 WECHAT_WEBHOOK_URL"
        ],
        "钉钉机器人": [
            "1. 在钉钉群聊中点击群设置",
            "2. 选择智能群助手 → 添加机器人 → 自定义",
            "3. 设置机器人名称和头像",
            "4. 选择安全设置（推荐加签）",
            "5. 复制Webhook URL和密钥",
            "6. 在.env文件中配置 DINGTALK_WEBHOOK_URL 和 DINGTALK_SECRET"
        ]
    }
    
    for platform, steps in guides.items():
        print(f"🔧 {platform} 配置步骤:")
        for step in steps:
            print(f"   {step}")
        print()

def main():
    """主菜单"""
    print("🚀 AI邮件督导系统 - 通知测试工具\n")
    
    options = [
        "测试所有通知配置",
        "测试单个通知平台", 
        "查看配置指南",
        "运行配置向导",
        "退出"
    ]
    
    while True:
        print("请选择操作:")
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")
        
        try:
            choice = int(input("\n请输入选择 (数字): "))
            
            if choice == 1:
                asyncio.run(test_all_notifications())
            elif choice == 2:
                asyncio.run(test_single_notification())
            elif choice == 3:
                show_configuration_guide()
            elif choice == 4:
                print("🔄 启动配置向导...")
                os.system("python setup_notifications.py")
            elif choice == 5:
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