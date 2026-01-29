"""
部署指南 - 帮助用户部署AI邮件督导系统到云平台
"""

import os
import json

def create_railway_config():
    """创建Railway部署配置"""
    print("🚂 创建Railway部署配置...")
    
    # railway.json
    railway_config = {
        "build": {
            "builder": "NIXPACKS"
        },
        "deploy": {
            "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
            "healthcheckPath": "/health"
        }
    }
    
    with open("railway.json", "w") as f:
        json.dump(railway_config, f, indent=2)
    
    # Procfile
    with open("Procfile", "w") as f:
        f.write("web: uvicorn main:app --host 0.0.0.0 --port $PORT\n")
    
    print("✅ Railway配置文件已创建")

def create_render_config():
    """创建Render部署配置"""
    print("🎨 创建Render部署配置...")
    
    render_config = {
        "services": [
            {
                "type": "web",
                "name": "ai-email-coach",
                "env": "python",
                "buildCommand": "pip install -r requirements.txt",
                "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
                "healthCheckPath": "/health"
            }
        ]
    }
    
    with open("render.yaml", "w") as f:
        import yaml
        yaml.dump(render_config, f, default_flow_style=False)
    
    print("✅ Render配置文件已创建")

def create_dockerfile():
    """创建Docker配置"""
    print("🐳 创建Docker配置...")
    
    dockerfile_content = """
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
"""
    
    with open("Dockerfile", "w") as f:
        f.write(dockerfile_content.strip())
    
    # .dockerignore
    dockerignore_content = """
__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis
.env
.venv
"""
    
    with open(".dockerignore", "w") as f:
        f.write(dockerignore_content.strip())
    
    print("✅ Docker配置文件已创建")

def show_deployment_guide():
    """显示部署指南"""
    print("📖 部署指南\n")
    
    print("🚂 Railway部署步骤:")
    print("1. 访问 https://railway.app")
    print("2. 使用GitHub账号登录")
    print("3. 点击 'New Project' → 'Deploy from GitHub repo'")
    print("4. 选择你的项目仓库")
    print("5. Railway会自动检测Python项目并部署")
    print("6. 部署完成后，复制生成的HTTPS URL")
    print()
    
    print("🎨 Render部署步骤:")
    print("1. 访问 https://render.com")
    print("2. 使用GitHub账号登录")
    print("3. 点击 'New' → 'Web Service'")
    print("4. 连接你的GitHub仓库")
    print("5. 配置:")
    print("   - Build Command: pip install -r requirements.txt")
    print("   - Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT")
    print("6. 点击 'Create Web Service'")
    print("7. 部署完成后，复制生成的HTTPS URL")
    print()
    
    print("🔧 环境变量配置:")
    print("在部署平台的环境变量设置中添加:")
    env_vars = [
        "SUPABASE_URL",
        "SUPABASE_KEY", 
        "RESEND_API_KEY",
        "DEEPSEEK_API_KEY",
        "EMAIL_163_USERNAME",
        "EMAIL_163_PASSWORD"
    ]
    
    for var in env_vars:
        value = os.getenv(var, "")
        if value:
            # 隐藏敏感信息
            if len(value) > 10:
                masked_value = value[:6] + "..." + value[-4:]
            else:
                masked_value = value[:3] + "..."
            print(f"   {var} = {masked_value}")
        else:
            print(f"   {var} = (需要设置)")

def create_github_workflow():
    """创建GitHub Actions工作流"""
    print("⚙️ 创建GitHub Actions工作流...")
    
    os.makedirs(".github/workflows", exist_ok=True)
    
    workflow_content = """
name: Deploy to Railway

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Use Node.js
      uses: actions/setup-node@v3
      with:
        node-version: '18'
    
    - name: Install Railway CLI
      run: npm install -g @railway/cli
    
    - name: Deploy to Railway
      run: railway up --service ${{ secrets.RAILWAY_SERVICE_ID }}
      env:
        RAILWAY_TOKEN: ${{ secrets.RAILWAY_TOKEN }}
"""
    
    with open(".github/workflows/deploy.yml", "w") as f:
        f.write(workflow_content.strip())
    
    print("✅ GitHub Actions工作流已创建")

def show_webhook_config_guide():
    """显示webhook配置指南"""
    print("🔗 Webhook配置指南\n")
    
    print("部署完成后，你会得到一个HTTPS URL，例如:")
    print("https://your-app-name.railway.app")
    print("或")
    print("https://your-app-name.onrender.com")
    print()
    
    print("然后在Resend控制台配置webhook:")
    print("1. 访问 https://resend.com/webhooks")
    print("2. 点击 'Create Webhook'")
    print("3. 填写信息:")
    print("   - Name: AI Email Coach Webhook")
    print("   - Endpoint URL: https://your-domain.com/inbound-email")
    print("   - Events: 选择 'email.received'")
    print("4. 创建后复制Secret到环境变量 RESEND_WEBHOOK_SECRET")
    print()
    
    print("🧪 测试webhook:")
    print("1. 发送邮件到你配置的邮箱地址")
    print("2. 邮件内容: '项目文档60%完成，Q1重要紧急'")
    print("3. 系统会自动解析并发送反馈邮件")

def main():
    """主菜单"""
    print("🚀 AI邮件督导系统 - 部署向导\n")
    
    options = [
        "创建Railway部署配置",
        "创建Render部署配置", 
        "创建Docker配置",
        "创建GitHub Actions工作流",
        "查看部署指南",
        "查看Webhook配置指南",
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
                create_railway_config()
            elif choice == 2:
                create_render_config()
            elif choice == 3:
                create_dockerfile()
            elif choice == 4:
                create_github_workflow()
            elif choice == 5:
                show_deployment_guide()
            elif choice == 6:
                show_webhook_config_guide()
            elif choice == 7:
                print("🔄 创建所有配置文件...")
                create_railway_config()
                create_render_config()
                create_dockerfile()
                create_github_workflow()
                print("✅ 所有配置文件已创建完成！")
            elif choice == 8:
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