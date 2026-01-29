"""
通知配置向导 - 帮助用户配置各种通知方式
"""

import os
import json

def print_header(title):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def print_step(step, description):
    print(f"\n📋 步骤 {step}: {description}")

def get_user_choice(prompt, options):
    """获取用户选择"""
    print(f"\n{prompt}")
    for i, option in enumerate(options, 1):
        print(f"  {i}. {option}")
    
    while True:
        try:
            choice = int(input("\n请输入选择 (数字): "))
            if 1 <= choice <= len(options):
                return choice - 1
            else:
                print("❌ 无效选择，请重新输入")
        except ValueError:
            print("❌ 请输入数字")

def setup_email_notifications():
    """配置邮件通知"""
    print_header("📧 邮件通知配置")
    
    email_providers = [
        "163邮箱",
        "QQ邮箱", 
        "Gmail",
        "跳过邮件配置"
    ]
    
    choice = get_user_choice("选择要配置的邮箱类型:", email_providers)
    
    if choice == 3:  # 跳过
        return {}
    
    email_configs = {}
    
    if choice == 0:  # 163邮箱
        print_step(1, "获取163邮箱配置")
        print("📝 需要的信息:")
        print("  - 163邮箱地址")
        print("  - 163邮箱密码或授权码")
        print("  - 如何获取授权码: 登录163邮箱 → 设置 → POP3/SMTP/IMAP → 开启服务并获取授权码")
        
        username = input("\n请输入163邮箱地址: ").strip()
        password = input("请输入163邮箱密码或授权码: ").strip()
        
        if username and password:
            email_configs["EMAIL_163_USERNAME"] = username
            email_configs["EMAIL_163_PASSWORD"] = password
            print("✅ 163邮箱配置完成")
    
    elif choice == 1:  # QQ邮箱
        print_step(1, "获取QQ邮箱配置")
        print("📝 需要的信息:")
        print("  - QQ邮箱地址")
        print("  - QQ邮箱授权码（不是QQ密码）")
        print("  - 如何获取授权码: 登录QQ邮箱 → 设置 → 账户 → POP3/IMAP/SMTP/Exchange/CardDAV/CalDAV服务 → 开启服务并获取授权码")
        
        username = input("\n请输入QQ邮箱地址: ").strip()
        password = input("请输入QQ邮箱授权码: ").strip()
        
        if username and password:
            email_configs["EMAIL_QQ_USERNAME"] = username
            email_configs["EMAIL_QQ_PASSWORD"] = password
            print("✅ QQ邮箱配置完成")
    
    elif choice == 2:  # Gmail
        print_step(1, "获取Gmail配置")
        print("📝 需要的信息:")
        print("  - Gmail地址")
        print("  - Gmail应用专用密码")
        print("  - 如何获取应用密码: Google账户 → 安全性 → 两步验证 → 应用专用密码")
        
        username = input("\n请输入Gmail地址: ").strip()
        password = input("请输入Gmail应用专用密码: ").strip()
        
        if username and password:
            email_configs["EMAIL_GMAIL_USERNAME"] = username
            email_configs["EMAIL_GMAIL_PASSWORD"] = password
            print("✅ Gmail配置完成")
    
    return email_configs

def setup_feishu_bot():
    """配置飞书机器人"""
    print_header("🚀 飞书机器人配置")
    
    choice = get_user_choice("是否配置飞书机器人?", ["是", "否"])
    
    if choice == 1:
        return {}
    
    print_step(1, "创建飞书群机器人")
    print("📝 操作步骤:")
    print("  1. 在飞书群聊中，点击群设置")
    print("  2. 选择 '群机器人' → '添加机器人' → '自定义机器人'")
    print("  3. 设置机器人名称和描述")
    print("  4. 复制生成的Webhook URL")
    print("  5. (可选) 设置签名密钥增强安全性")
    
    webhook_url = input("\n请输入飞书机器人Webhook URL: ").strip()
    
    if not webhook_url:
        print("❌ 跳过飞书机器人配置")
        return {}
    
    secret = input("请输入签名密钥 (可选，直接回车跳过): ").strip()
    
    config = {"FEISHU_WEBHOOK_URL": webhook_url}
    if secret:
        config["FEISHU_SECRET"] = secret
    
    print("✅ 飞书机器人配置完成")
    return config

def setup_wechat_bot():
    """配置企业微信机器人"""
    print_header("💬 企业微信机器人配置")
    
    choice = get_user_choice("是否配置企业微信机器人?", ["是", "否"])
    
    if choice == 1:
        return {}
    
    print_step(1, "创建企业微信群机器人")
    print("📝 操作步骤:")
    print("  1. 在企业微信群聊中，点击群设置")
    print("  2. 选择 '群机器人' → '添加机器人'")
    print("  3. 设置机器人名称和描述")
    print("  4. 复制生成的Webhook URL")
    
    webhook_url = input("\n请输入企业微信机器人Webhook URL: ").strip()
    
    if not webhook_url:
        print("❌ 跳过企业微信机器人配置")
        return {}
    
    config = {"WECHAT_WEBHOOK_URL": webhook_url}
    print("✅ 企业微信机器人配置完成")
    return config

def setup_dingtalk_bot():
    """配置钉钉机器人"""
    print_header("📱 钉钉机器人配置")
    
    choice = get_user_choice("是否配置钉钉机器人?", ["是", "否"])
    
    if choice == 1:
        return {}
    
    print_step(1, "创建钉钉群机器人")
    print("📝 操作步骤:")
    print("  1. 在钉钉群聊中，点击群设置")
    print("  2. 选择 '智能群助手' → '添加机器人' → '自定义'")
    print("  3. 设置机器人名称和描述")
    print("  4. 选择安全设置（推荐使用加签）")
    print("  5. 复制生成的Webhook URL和密钥")
    
    webhook_url = input("\n请输入钉钉机器人Webhook URL: ").strip()
    
    if not webhook_url:
        print("❌ 跳过钉钉机器人配置")
        return {}
    
    secret = input("请输入签名密钥 (推荐设置): ").strip()
    
    config = {"DINGTALK_WEBHOOK_URL": webhook_url}
    if secret:
        config["DINGTALK_SECRET"] = secret
    
    print("✅ 钉钉机器人配置完成")
    return config

def update_env_file(new_configs):
    """更新.env文件"""
    print_step("最后", "更新配置文件")
    
    # 读取现有.env文件
    env_content = ""
    if os.path.exists(".env"):
        with open(".env", "r", encoding="utf-8") as f:
            env_content = f.read()
    
    # 添加新配置
    if new_configs:
        env_content += "\n\n# 多平台通知配置\n"
        for key, value in new_configs.items():
            env_content += f"{key}={value}\n"
    
    # 写入.env文件
    with open(".env", "w", encoding="utf-8") as f:
        f.write(env_content)
    
    print("✅ 配置已保存到 .env 文件")

def test_notifications():
    """测试通知配置"""
    print_header("🧪 测试通知配置")
    
    choice = get_user_choice("是否立即测试通知配置?", ["是", "否"])
    
    if choice == 1:
        print("跳过测试，配置完成！")
        return
    
    print("🔄 正在测试通知配置...")
    
    try:
        import asyncio
        from notification_manager import notification_manager
        
        async def run_test():
            test_email = input("请输入测试邮箱地址: ").strip()
            if not test_email:
                print("❌ 未提供测试邮箱，跳过测试")
                return
            
            results = await notification_manager.send_notification(
                test_email,
                "🧪 AI邮件督导系统测试",
                "这是一条测试消息，如果你收到了这条消息，说明通知配置成功！\n\n📊 测试内容:\n• 任务A: 进度 [■■■■■□□□□□] 50%\n• 任务B: 进度 [■■■□□□□□□□] 30%\n\n🎯 系统运行正常！"
            )
            
            print(f"\n📊 测试结果:")
            for platform, success in results.items():
                status = "✅ 成功" if success else "❌ 失败"
                print(f"  {platform}: {status}")
        
        asyncio.run(run_test())
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        print("请检查配置是否正确")

def main():
    """主配置流程"""
    print_header("🚀 AI邮件督导系统 - 多平台通知配置向导")
    
    print("欢迎使用通知配置向导！")
    print("这个向导将帮助你配置多种通知方式，包括:")
    print("  📧 邮件通知 (163、QQ、Gmail等)")
    print("  🚀 飞书机器人")
    print("  💬 企业微信机器人") 
    print("  📱 钉钉机器人")
    
    all_configs = {}
    
    # 配置各种通知方式
    all_configs.update(setup_email_notifications())
    all_configs.update(setup_feishu_bot())
    all_configs.update(setup_wechat_bot())
    all_configs.update(setup_dingtalk_bot())
    
    # 更新配置文件
    if all_configs:
        update_env_file(all_configs)
        
        print_header("🎉 配置完成")
        print("已配置的通知方式:")
        for key in all_configs.keys():
            if "USERNAME" in key or "WEBHOOK" in key:
                print(f"  ✅ {key}")
        
        # 测试配置
        test_notifications()
        
        print("\n🚀 下一步:")
        print("1. 运行 'python start.py' 启动系统")
        print("2. 系统会自动使用配置的通知方式发送消息")
        print("3. 你可以通过多个平台接收AI督导的反馈")
        
    else:
        print("\n⚠️ 未配置任何通知方式")
        print("系统将使用默认的Resend邮件服务")

if __name__ == "__main__":
    main()