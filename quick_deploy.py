"""
快速部署脚本 - 一键部署到Railway
"""

import os
import subprocess
import json

def check_git_repo():
    """检查是否是Git仓库"""
    if not os.path.exists(".git"):
        print("📁 初始化Git仓库...")
        subprocess.run(["git", "init"], check=True)
        
        # 创建.gitignore
        gitignore_content = """
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg

.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

.pytest_cache/
.coverage
htmlcov/

.DS_Store
.vscode/
.idea/
        """.strip()
        
        with open(".gitignore", "w") as f:
            f.write(gitignore_content)
        
        print("✅ Git仓库初始化完成")
    else:
        print("✅ Git仓库已存在")

def commit_changes():
    """提交代码更改"""
    print("📝 提交代码更改...")
    
    subprocess.run(["git", "add", "."], check=True)
    
    try:
        subprocess.run(["git", "commit", "-m", "Deploy AI Email Coach system"], check=True)
        print("✅ 代码提交完成")
    except subprocess.CalledProcessError:
        print("ℹ️ 没有新的更改需要提交")

def deploy_to_railway():
    """部署到Railway"""
    print("🚂 开始部署到Railway...")
    
    # 检查是否安装了Railway CLI
    try:
        subprocess.run(["railway", "--version"], check=True, capture_output=True)
        print("✅ Railway CLI已安装")
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Railway CLI未安装")
        print("请先安装Railway CLI:")
        print("npm install -g @railway/cli")
        print("或访问: https://docs.railway.app/develop/cli")
        return False
    
    # 登录Railway
    print("🔐 请登录Railway...")
    try:
        subprocess.run(["railway", "login"], check=True)
        print("✅ Railway登录成功")
    except subprocess.CalledProcessError:
        print("❌ Railway登录失败")
        return False
    
    # 创建项目
    print("📦 创建Railway项目...")
    try:
        result = subprocess.run(["railway", "init"], check=True, capture_output=True, text=True)
        print("✅ Railway项目创建成功")
    except subprocess.CalledProcessError as e:
        if "already linked" in str(e.stderr):
            print("ℹ️ 项目已经链接到Railway")
        else:
            print(f"❌ 创建项目失败: {e}")
            return False
    
    # 设置环境变量
    print("🔧 设置环境变量...")
    env_vars = [
        "SUPABASE_URL",
        "SUPABASE_KEY",
        "RESEND_API_KEY", 
        "DEEPSEEK_API_KEY",
        "EMAIL_163_USERNAME",
        "EMAIL_163_PASSWORD"
    ]
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            try:
                subprocess.run(["railway", "variables", "set", f"{var}={value}"], check=True)
                print(f"✅ 设置 {var}")
            except subprocess.CalledProcessError:
                print(f"⚠️ 设置 {var} 失败")
    
    # 部署
    print("🚀 开始部署...")
    try:
        subprocess.run(["railway", "up"], check=True)
        print("✅ 部署成功！")
        
        # 获取部署URL
        try:
            result = subprocess.run(["railway", "domain"], capture_output=True, text=True)
            if result.returncode == 0:
                domain = result.stdout.strip()
                print(f"🌐 应用URL: https://{domain}")
                print(f"📧 Webhook URL: https://{domain}/inbound-email")
                return domain
        except:
            print("ℹ️ 无法获取域名，请在Railway控制台查看")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 部署失败: {e}")
        return False

def show_next_steps(domain=None):
    """显示后续步骤"""
    print("\n" + "="*60)
    print("🎉 部署完成！后续步骤:")
    print("="*60)
    
    if domain:
        webhook_url = f"https://{domain}/inbound-email"
        print(f"1. 📧 配置Resend Webhook:")
        print(f"   - 访问: https://resend.com/webhooks")
        print(f"   - 创建新webhook")
        print(f"   - URL: {webhook_url}")
        print(f"   - 事件: email.received")
        print()
    
    print("2. 🧪 测试系统:")
    if domain:
        print(f"   - 访问: https://{domain}/health")
        print(f"   - API文档: https://{domain}/docs")
    print("   - 发送测试邮件验证功能")
    print()
    
    print("3. 📱 使用系统:")
    print("   - 发送邮件内容如: '项目文档60%完成，Q1重要紧急'")
    print("   - 系统会自动解析并发送反馈")
    print("   - 检查你的163邮箱和飞书群聊")

def main():
    """主部署流程"""
    print("🚀 AI邮件督导系统 - 快速部署到Railway\n")
    
    try:
        # 检查Git仓库
        check_git_repo()
        
        # 提交更改
        commit_changes()
        
        # 部署到Railway
        domain = deploy_to_railway()
        
        # 显示后续步骤
        show_next_steps(domain)
        
    except KeyboardInterrupt:
        print("\n👋 部署已取消")
    except Exception as e:
        print(f"❌ 部署过程中出现错误: {e}")
        print("\n💡 你也可以手动部署:")
        print("1. 将代码推送到GitHub")
        print("2. 在Railway.app中连接GitHub仓库")
        print("3. 配置环境变量")
        print("4. 部署项目")

if __name__ == "__main__":
    main()