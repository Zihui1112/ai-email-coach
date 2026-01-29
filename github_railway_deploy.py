"""
GitHub + Railway 部署指南 - 最简单的部署方式
"""

import os
import subprocess
import json

def check_git_status():
    """检查Git状态"""
    print("📁 检查Git仓库状态...")
    
    if not os.path.exists(".git"):
        print("❌ 当前目录不是Git仓库")
        return False
    
    try:
        # 检查是否有未提交的更改
        result = subprocess.run(["git", "status", "--porcelain"], 
                              capture_output=True, text=True, check=True)
        
        if result.stdout.strip():
            print("⚠️ 有未提交的更改")
            return False
        else:
            print("✅ Git仓库状态正常")
            return True
            
    except subprocess.CalledProcessError:
        print("❌ 检查Git状态失败")
        return False

def init_git_repo():
    """初始化Git仓库"""
    print("🔄 初始化Git仓库...")
    
    try:
        # 初始化Git仓库
        subprocess.run(["git", "init"], check=True)
        
        # 创建.gitignore
        gitignore_content = """
# Python
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

# 环境变量
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDE
.vscode/
.idea/
*.swp
*.swo

# 操作系统
.DS_Store
Thumbs.db

# 测试和覆盖率
.pytest_cache/
.coverage
htmlcov/
.tox/

# 日志
*.log

# 临时文件
*.tmp
*.temp
        """.strip()
        
        with open(".gitignore", "w") as f:
            f.write(gitignore_content)
        
        print("✅ Git仓库初始化完成")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git初始化失败: {e}")
        return False

def commit_all_changes():
    """提交所有更改"""
    print("📝 提交代码更改...")
    
    try:
        # 添加所有文件
        subprocess.run(["git", "add", "."], check=True)
        
        # 提交更改
        subprocess.run(["git", "commit", "-m", "Initial commit: AI Email Coach system"], check=True)
        
        print("✅ 代码提交完成")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 提交失败: {e}")
        return False

def create_github_repo():
    """创建GitHub仓库指导"""
    print("🐙 GitHub仓库创建指导\n")
    
    print("请按照以下步骤创建GitHub仓库：")
    print("1. 访问 https://github.com")
    print("2. 点击右上角的 '+' 按钮")
    print("3. 选择 'New repository'")
    print("4. 填写仓库信息：")
    print("   - Repository name: ai-email-coach")
    print("   - Description: AI邮件督导系统")
    print("   - 选择 Public 或 Private")
    print("   - 不要勾选 'Initialize this repository with a README'")
    print("5. 点击 'Create repository'")
    print()
    
    repo_url = input("请输入创建的GitHub仓库URL (例如: https://github.com/username/ai-email-coach.git): ").strip()
    
    if not repo_url:
        print("❌ 未提供仓库URL")
        return None
    
    return repo_url

def push_to_github(repo_url):
    """推送代码到GitHub"""
    print("🚀 推送代码到GitHub...")
    
    try:
        # 添加远程仓库
        subprocess.run(["git", "remote", "add", "origin", repo_url], check=True)
        
        # 推送代码
        subprocess.run(["git", "branch", "-M", "main"], check=True)
        subprocess.run(["git", "push", "-u", "origin", "main"], check=True)
        
        print("✅ 代码推送成功")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 推送失败: {e}")
        print("💡 可能的原因：")
        print("  - 仓库URL错误")
        print("  - 没有GitHub访问权限")
        print("  - 网络连接问题")
        return False

def deploy_to_railway():
    """部署到Railway指导"""
    print("🚂 Railway部署指导\n")
    
    print("请按照以下步骤部署到Railway：")
    print()
    print("1. 访问 Railway")
    print("   https://railway.app")
    print()
    print("2. 注册/登录账号")
    print("   - 推荐使用GitHub账号登录")
    print("   - 这样可以直接访问你的仓库")
    print()
    print("3. 创建新项目")
    print("   - 点击 'New Project'")
    print("   - 选择 'Deploy from GitHub repo'")
    print("   - 选择你刚才创建的 'ai-email-coach' 仓库")
    print()
    print("4. 配置环境变量")
    print("   在Railway项目设置中添加以下环境变量：")
    
    env_vars = [
        ("SUPABASE_URL", os.getenv("SUPABASE_URL", "")),
        ("SUPABASE_KEY", os.getenv("SUPABASE_KEY", "")),
        ("RESEND_API_KEY", os.getenv("RESEND_API_KEY", "")),
        ("DEEPSEEK_API_KEY", os.getenv("DEEPSEEK_API_KEY", "")),
        ("EMAIL_163_USERNAME", os.getenv("EMAIL_163_USERNAME", "")),
        ("EMAIL_163_PASSWORD", os.getenv("EMAIL_163_PASSWORD", ""))
    ]
    
    for var_name, var_value in env_vars:
        if var_value:
            # 隐藏敏感信息
            if len(var_value) > 10:
                masked_value = var_value[:6] + "..." + var_value[-4:]
            else:
                masked_value = var_value[:3] + "..."
            print(f"   {var_name} = {masked_value}")
        else:
            print(f"   {var_name} = (需要设置)")
    
    print()
    print("5. 部署")
    print("   - Railway会自动检测Python项目")
    print("   - 自动安装依赖并部署")
    print("   - 等待部署完成（通常2-5分钟）")
    print()
    print("6. 获取部署URL")
    print("   - 部署完成后，Railway会提供一个HTTPS URL")
    print("   - 例如: https://your-app-name.railway.app")
    print("   - 记录这个URL，用于配置webhook")
    print()

def configure_webhook_guide():
    """配置webhook指导"""
    print("🔗 配置Resend Webhook\n")
    
    railway_url = input("请输入Railway部署后的URL (例如: https://your-app-name.railway.app): ").strip()
    
    if railway_url:
        webhook_url = f"{railway_url}/inbound-email"
        
        print(f"📧 Webhook配置步骤：")
        print("1. 访问 Resend控制台")
        print("   https://resend.com/webhooks")
        print()
        print("2. 创建新Webhook")
        print("   - 点击 'Create Webhook'")
        print("   - Name: AI Email Coach Webhook")
        print(f"   - Endpoint URL: {webhook_url}")
        print("   - Events: 选择 'email.received'")
        print()
        print("3. 获取Webhook Secret")
        print("   - 创建后复制生成的Secret")
        print("   - 在Railway环境变量中添加:")
        print("     RESEND_WEBHOOK_SECRET = 你的secret")
        print()
        print("4. 测试Webhook")
        print(f"   - 访问 {railway_url}/health 检查服务状态")
        print("   - 发送测试邮件验证功能")
    else:
        print("⚠️ 未提供Railway URL，请手动配置webhook")

def show_final_steps():
    """显示最终步骤"""
    print("🎉 部署完成！最终步骤\n")
    
    print("✅ 已完成：")
    print("  - Git仓库初始化")
    print("  - 代码推送到GitHub")
    print("  - Railway部署配置")
    print("  - Webhook配置指导")
    print()
    
    print("🧪 测试系统：")
    print("1. 访问你的Railway应用URL")
    print("2. 检查 /health 端点")
    print("3. 发送测试邮件：")
    print("   '项目文档60%完成，Q1重要紧急'")
    print("4. 检查163邮箱是否收到反馈")
    print()
    
    print("📱 日常使用：")
    print("- 发送邮件更新任务进度")
    print("- 系统自动解析并发送反馈")
    print("- 支持163邮箱和飞书通知")
    print()
    
    print("🔧 如果遇到问题：")
    print("- 检查Railway日志")
    print("- 验证环境变量配置")
    print("- 确认webhook URL正确")

def main():
    """主部署流程"""
    print("🚀 GitHub + Railway 部署向导\n")
    print("这个向导将帮助你：")
    print("1. 准备Git仓库")
    print("2. 推送代码到GitHub")
    print("3. 部署到Railway")
    print("4. 配置Webhook")
    print()
    
    try:
        # 检查或初始化Git仓库
        if not check_git_status():
            if not os.path.exists(".git"):
                if not init_git_repo():
                    return
            
            if not commit_all_changes():
                return
        
        # 创建GitHub仓库
        print("\n" + "="*60)
        repo_url = create_github_repo()
        if not repo_url:
            return
        
        # 推送到GitHub
        print("\n" + "="*60)
        if not push_to_github(repo_url):
            return
        
        # Railway部署指导
        print("\n" + "="*60)
        deploy_to_railway()
        
        input("\n按回车键继续到webhook配置...")
        
        # Webhook配置指导
        print("\n" + "="*60)
        configure_webhook_guide()
        
        # 最终步骤
        print("\n" + "="*60)
        show_final_steps()
        
    except KeyboardInterrupt:
        print("\n👋 部署已取消")
    except Exception as e:
        print(f"❌ 部署过程中出现错误: {e}")

if __name__ == "__main__":
    main()