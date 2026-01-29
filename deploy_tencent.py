"""
腾讯云CloudBase部署脚本 - 免费且支持国内访问
"""

import os
import json
import subprocess

def create_cloudbase_config():
    """创建腾讯云CloudBase配置"""
    print("☁️ 创建腾讯云CloudBase配置...")
    
    # cloudbaserc.json
    cloudbase_config = {
        "envId": "your-env-id",
        "functionRoot": "./",
        "functions": [
            {
                "name": "ai-email-coach",
                "timeout": 60,
                "envVariables": {
                    "SUPABASE_URL": os.getenv("SUPABASE_URL", ""),
                    "SUPABASE_KEY": os.getenv("SUPABASE_KEY", ""),
                    "RESEND_API_KEY": os.getenv("RESEND_API_KEY", ""),
                    "DEEPSEEK_API_KEY": os.getenv("DEEPSEEK_API_KEY", ""),
                    "EMAIL_163_USERNAME": os.getenv("EMAIL_163_USERNAME", ""),
                    "EMAIL_163_PASSWORD": os.getenv("EMAIL_163_PASSWORD", "")
                },
                "installDependency": True,
                "handler": "main.handler"
            }
        ]
    }
    
    with open("cloudbaserc.json", "w", encoding="utf-8") as f:
        json.dump(cloudbase_config, f, indent=2, ensure_ascii=False)
    
    print("✅ CloudBase配置文件已创建")

def create_serverless_handler():
    """创建Serverless处理函数"""
    print("⚡ 创建Serverless处理函数...")
    
    handler_content = '''
"""
腾讯云CloudBase Serverless处理函数
"""

import json
import asyncio
from main import app

def handler(event, context):
    """CloudBase函数入口"""
    try:
        # 解析HTTP请求
        method = event.get("httpMethod", "GET")
        path = event.get("path", "/")
        headers = event.get("headers", {})
        body = event.get("body", "")
        
        # 处理请求
        if method == "POST" and path == "/inbound-email":
            # 处理webhook请求
            import asyncio
            from main import handle_inbound_email_sync
            
            result = handle_inbound_email_sync(body, headers)
            
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps(result)
            }
        
        elif path == "/health":
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"status": "healthy", "platform": "tencent-cloudbase"})
            }
        
        else:
            return {
                "statusCode": 404,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Not Found"})
            }
            
    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }
'''
    
    with open("serverless_handler.py", "w", encoding="utf-8") as f:
        f.write(handler_content.strip())
    
    print("✅ Serverless处理函数已创建")

def create_vercel_config():
    """创建Vercel配置（备选方案）"""
    print("🔺 创建Vercel配置...")
    
    vercel_config = {
        "version": 2,
        "builds": [
            {
                "src": "main.py",
                "use": "@vercel/python"
            }
        ],
        "routes": [
            {
                "src": "/(.*)",
                "dest": "main.py"
            }
        ],
        "env": {
            "SUPABASE_URL": os.getenv("SUPABASE_URL", ""),
            "SUPABASE_KEY": os.getenv("SUPABASE_KEY", ""),
            "RESEND_API_KEY": os.getenv("RESEND_API_KEY", ""),
            "DEEPSEEK_API_KEY": os.getenv("DEEPSEEK_API_KEY", "")
        }
    }
    
    with open("vercel.json", "w") as f:
        json.dump(vercel_config, f, indent=2)
    
    # 创建Vercel适配器
    vercel_adapter = '''
from fastapi import FastAPI
from mangum import Mangum
from main import app

handler = Mangum(app)
'''
    
    with open("api/index.py", "w") as f:
        os.makedirs("api", exist_ok=True)
        f.write(vercel_adapter.strip())
    
    print("✅ Vercel配置文件已创建")

def show_deployment_guide():
    """显示部署指南"""
    print("📖 国内免费部署指南\n")
    
    print("🥇 方案1：腾讯云CloudBase（最推荐）")
    print("优势：")
    print("  ✅ 完全免费（每月5GB流量）")
    print("  ✅ 国内访问速度快")
    print("  ✅ 自动HTTPS证书")
    print("  ✅ 支持自定义域名")
    print()
    print("部署步骤：")
    print("1. 注册腾讯云账号：https://cloud.tencent.com")
    print("2. 开通CloudBase服务")
    print("3. 安装CloudBase CLI：npm install -g @cloudbase/cli")
    print("4. 登录：tcb login")
    print("5. 初始化：tcb init")
    print("6. 部署：tcb functions:deploy ai-email-coach")
    print()
    
    print("🥈 方案2：Vercel（国外但速度还行）")
    print("优势：")
    print("  ✅ 完全免费")
    print("  ✅ 自动HTTPS")
    print("  ✅ GitHub集成")
    print("  ⚠️ 需要VPN访问控制台")
    print()
    print("部署步骤：")
    print("1. 访问：https://vercel.com")
    print("2. 连接GitHub仓库")
    print("3. 自动部署")
    print()
    
    print("🥉 方案3：阿里云函数计算")
    print("优势：")
    print("  ✅ 免费额度充足")
    print("  ✅ 国内网络优化")
    print("  ✅ 阿里云生态")
    print()
    
    print("🔧 推荐配置顺序：")
    print("1. 腾讯云CloudBase（主要）")
    print("2. Vercel（备用）")
    print("3. 本地开发环境（测试）")

def create_tencent_deploy_script():
    """创建腾讯云一键部署脚本"""
    print("🚀 创建腾讯云一键部署脚本...")
    
    deploy_script = '''#!/bin/bash

echo "🚀 腾讯云CloudBase一键部署脚本"
echo "=================================="

# 检查是否安装了CloudBase CLI
if ! command -v tcb &> /dev/null; then
    echo "❌ CloudBase CLI未安装"
    echo "请先安装：npm install -g @cloudbase/cli"
    exit 1
fi

echo "✅ CloudBase CLI已安装"

# 登录腾讯云
echo "🔐 请登录腾讯云..."
tcb login

# 检查登录状态
if [ $? -ne 0 ]; then
    echo "❌ 登录失败"
    exit 1
fi

echo "✅ 登录成功"

# 初始化项目（如果需要）
if [ ! -f "cloudbaserc.json" ]; then
    echo "📦 初始化CloudBase项目..."
    tcb init
fi

# 部署函数
echo "🚀 部署函数到CloudBase..."
tcb functions:deploy ai-email-coach

if [ $? -eq 0 ]; then
    echo "✅ 部署成功！"
    echo "📧 请在腾讯云控制台配置HTTP触发器"
    echo "🔗 获取触发器URL用于配置Resend webhook"
else
    echo "❌ 部署失败"
    exit 1
fi
'''
    
    with open("deploy_tencent.sh", "w") as f:
        f.write(deploy_script.strip())
    
    # 设置执行权限
    os.chmod("deploy_tencent.sh", 0o755)
    
    print("✅ 腾讯云部署脚本已创建")

def show_free_alternatives():
    """显示其他免费替代方案"""
    print("🆓 其他免费部署方案\n")
    
    alternatives = [
        {
            "name": "Koyeb",
            "pros": ["完全免费", "自动HTTPS", "支持Docker"],
            "cons": ["国外服务器", "需要VPN管理"],
            "url": "https://www.koyeb.com"
        },
        {
            "name": "Fly.io", 
            "pros": ["免费额度", "全球CDN", "Docker支持"],
            "cons": ["国外服务器", "配置复杂"],
            "url": "https://fly.io"
        },
        {
            "name": "Deta Space",
            "pros": ["完全免费", "简单部署", "Python友好"],
            "cons": ["国外服务器", "功能限制"],
            "url": "https://deta.space"
        },
        {
            "name": "PythonAnywhere",
            "pros": ["Python专用", "免费套餐", "简单易用"],
            "cons": ["功能限制", "国外访问"],
            "url": "https://www.pythonanywhere.com"
        }
    ]
    
    for alt in alternatives:
        print(f"🔸 {alt['name']}")
        print(f"   网址: {alt['url']}")
        print(f"   优势: {', '.join(alt['pros'])}")
        print(f"   劣势: {', '.join(alt['cons'])}")
        print()

def main():
    """主菜单"""
    print("🇨🇳 AI邮件督导系统 - 国内免费部署方案\n")
    
    options = [
        "创建腾讯云CloudBase配置（推荐）",
        "创建Vercel配置（备选）",
        "创建腾讯云部署脚本",
        "查看部署指南",
        "查看其他免费方案",
        "创建所有配置文件",
        "退出"
    ]
    
    while True:
        print("请选择操作:")
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")
        
        try:
            choice = int(input("\n请输入选择 (数字): "))
            
            if choice == 1:
                create_cloudbase_config()
                create_serverless_handler()
            elif choice == 2:
                create_vercel_config()
            elif choice == 3:
                create_tencent_deploy_script()
            elif choice == 4:
                show_deployment_guide()
            elif choice == 5:
                show_free_alternatives()
            elif choice == 6:
                print("🔄 创建所有配置文件...")
                create_cloudbase_config()
                create_serverless_handler()
                create_vercel_config()
                create_tencent_deploy_script()
                print("✅ 所有配置文件已创建完成！")
            elif choice == 7:
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