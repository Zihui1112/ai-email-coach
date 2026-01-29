"""
中国大陆免费部署方案 - 最适合国内网络环境
"""

import os
import json

def show_best_options():
    """显示最佳部署选项"""
    print("🇨🇳 中国大陆最佳免费部署方案\n")
    
    print("🥇 第一推荐：腾讯云CloudBase")
    print("="*50)
    print("✅ 优势：")
    print("  • 完全免费（每月5GB流量，40万次调用）")
    print("  • 国内访问速度极快")
    print("  • 自动HTTPS证书")
    print("  • 支持自定义域名")
    print("  • 腾讯云CDN加速")
    print("  • 无需备案（使用默认域名）")
    print()
    print("📋 部署步骤：")
    print("1. 注册腾讯云：https://cloud.tencent.com")
    print("2. 开通CloudBase：https://console.cloud.tencent.com/tcb")
    print("3. 创建环境（选择按量付费，有免费额度）")
    print("4. 安装CLI：npm install -g @cloudbase/cli")
    print("5. 运行：python deploy_china.py")
    print()
    
    print("🥈 第二推荐：阿里云函数计算")
    print("="*50)
    print("✅ 优势：")
    print("  • 每月100万次免费调用")
    print("  • 阿里云网络优化")
    print("  • 支持HTTP触发器")
    print("  • 自动扩缩容")
    print()
    print("📋 部署步骤：")
    print("1. 注册阿里云：https://www.aliyun.com")
    print("2. 开通函数计算：https://fc.console.aliyun.com")
    print("3. 创建函数，选择Python运行时")
    print("4. 上传代码包")
    print("5. 配置HTTP触发器")
    print()
    
    print("🥉 第三推荐：华为云FunctionGraph")
    print("="*50)
    print("✅ 优势：")
    print("  • 每月100万次免费调用")
    print("  • 华为云基础设施")
    print("  • 支持API网关")
    print()

def create_tencent_quick_deploy():
    """创建腾讯云快速部署配置"""
    print("🚀 创建腾讯云CloudBase快速部署配置...\n")
    
    # 1. 创建cloudbaserc.json
    cloudbase_config = {
        "envId": "请在腾讯云控制台创建环境后填入环境ID",
        "functionRoot": "./functions",
        "functions": [
            {
                "name": "ai-email-coach",
                "timeout": 60,
                "envVariables": {},
                "installDependency": True,
                "handler": "index.main"
            }
        ],
        "framework": {
            "name": "ai-email-coach",
            "plugins": {
                "function": {
                    "use": "@cloudbase/framework-plugin-function",
                    "inputs": {
                        "functionRootPath": "./functions",
                        "functions": [
                            {
                                "name": "ai-email-coach",
                                "config": {
                                    "timeout": 60,
                                    "envVariables": {},
                                    "runtime": "Python3.7",
                                    "installDependency": True
                                }
                            }
                        ]
                    }
                }
            }
        }
    }
    
    with open("cloudbaserc.json", "w", encoding="utf-8") as f:
        json.dump(cloudbase_config, f, indent=2, ensure_ascii=False)
    
    # 2. 创建functions目录和入口文件
    os.makedirs("functions", exist_ok=True)
    
    # 3. 创建CloudBase适配的main函数
    cloudbase_main = '''
"""
腾讯云CloudBase入口文件
"""

import json
import os
import sys

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main(event, context):
    """CloudBase函数入口"""
    try:
        # 导入主应用
        from main import process_webhook_sync
        
        # 解析事件
        method = event.get("httpMethod", "GET")
        path = event.get("path", "/")
        headers = event.get("headers", {})
        body = event.get("body", "")
        
        print(f"收到请求: {method} {path}")
        
        if method == "POST" and path.endswith("/inbound-email"):
            # 处理webhook
            result = process_webhook_sync(body, headers)
            return {
                "statusCode": 200,
                "headers": {
                    "Content-Type": "application/json",
                    "Access-Control-Allow-Origin": "*"
                },
                "body": json.dumps(result, ensure_ascii=False)
            }
        
        elif path.endswith("/health"):
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "status": "healthy", 
                    "platform": "tencent-cloudbase",
                    "message": "AI邮件督导系统运行正常"
                }, ensure_ascii=False)
            }
        
        else:
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({
                    "message": "AI邮件督导系统",
                    "version": "1.0.0",
                    "endpoints": ["/inbound-email", "/health"]
                }, ensure_ascii=False)
            }
            
    except Exception as e:
        print(f"处理请求时出错: {str(e)}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)}, ensure_ascii=False)
        }
'''
    
    with open("functions/index.py", "w", encoding="utf-8") as f:
        f.write(cloudbase_main.strip())
    
    # 4. 创建requirements.txt for functions
    with open("functions/requirements.txt", "w") as f:
        f.write("""fastapi
httpx
python-dotenv
supabase
pydantic[email]
""")
    
    # 5. 复制必要文件到functions目录
    files_to_copy = ["main.py", "notification_manager.py", ".env"]
    for file in files_to_copy:
        if os.path.exists(file):
            import shutil
            shutil.copy2(file, f"functions/{file}")
    
    print("✅ 腾讯云CloudBase配置已创建")
    print("📁 文件结构：")
    print("  cloudbaserc.json - CloudBase配置")
    print("  functions/index.py - 入口函数")
    print("  functions/main.py - 主应用")
    print("  functions/requirements.txt - 依赖列表")

def create_aliyun_config():
    """创建阿里云函数计算配置"""
    print("☁️ 创建阿里云函数计算配置...\n")
    
    # template.yml for 阿里云Funcraft
    template_content = '''
ROSTemplateFormatVersion: '2015-09-01'
Transform: 'Aliyun::Serverless-2018-04-03'
Resources:
  ai-email-coach:
    Type: 'Aliyun::Serverless::Service'
    Properties:
      Description: 'AI邮件督导系统'
    ai-email-coach-function:
      Type: 'Aliyun::Serverless::Function'
      Properties:
        Description: 'AI邮件督导主函数'
        CodeUri: './'
        Handler: 'index.handler'
        Runtime: python3.9
        Timeout: 60
        MemorySize: 512
        EnvironmentVariables:
          SUPABASE_URL: '${SUPABASE_URL}'
          SUPABASE_KEY: '${SUPABASE_KEY}'
          RESEND_API_KEY: '${RESEND_API_KEY}'
          DEEPSEEK_API_KEY: '${DEEPSEEK_API_KEY}'
        Events:
          httpTrigger:
            Type: HTTP
            Properties:
              AuthType: ANONYMOUS
              Methods: ['GET', 'POST']
'''
    
    with open("template.yml", "w") as f:
        f.write(template_content.strip())
    
    print("✅ 阿里云函数计算配置已创建")

def show_deployment_commands():
    """显示部署命令"""
    print("🚀 部署命令指南\n")
    
    print("腾讯云CloudBase部署：")
    print("1. 安装CLI：npm install -g @cloudbase/cli")
    print("2. 登录：tcb login")
    print("3. 部署：tcb framework:deploy")
    print("4. 获取访问链接")
    print()
    
    print("阿里云函数计算部署：")
    print("1. 安装Funcraft：npm install -g @alicloud/fun")
    print("2. 配置：fun config")
    print("3. 部署：fun deploy")
    print("4. 配置HTTP触发器")
    print()

def main():
    """主菜单"""
    print("🇨🇳 AI邮件督导系统 - 中国大陆免费部署\n")
    
    options = [
        "查看最佳部署方案",
        "创建腾讯云CloudBase配置（推荐）",
        "创建阿里云函数计算配置",
        "显示部署命令",
        "创建所有配置",
        "退出"
    ]
    
    while True:
        print("请选择操作:")
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")
        
        try:
            choice = int(input("\n请输入选择 (数字): "))
            
            if choice == 1:
                show_best_options()
            elif choice == 2:
                create_tencent_quick_deploy()
            elif choice == 3:
                create_aliyun_config()
            elif choice == 4:
                show_deployment_commands()
            elif choice == 5:
                print("🔄 创建所有配置...")
                create_tencent_quick_deploy()
                create_aliyun_config()
                print("✅ 所有配置已创建完成！")
            elif choice == 6:
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