"""
自动化安装脚本 - 确保环境配置正确
"""

import subprocess
import sys
import os

def run_command(command, description):
    """运行命令并显示结果"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} 成功")
            return True
        else:
            print(f"❌ {description} 失败:")
            print(f"   错误: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ {description} 异常: {e}")
        return False

def check_python_version():
    """检查Python版本"""
    print("🐍 检查Python版本...")
    version = sys.version_info
    print(f"   当前版本: Python {version.major}.{version.minor}.{version.micro}")
    
    if version.major >= 3 and version.minor >= 8:
        print("✅ Python版本符合要求 (>=3.8)")
        return True
    else:
        print("❌ Python版本过低，需要Python 3.8或更高版本")
        return False

def create_virtual_env():
    """创建虚拟环境"""
    if os.path.exists("ai-email-coach-env"):
        print("📁 虚拟环境已存在，跳过创建")
        return True
    
    return run_command("python -m venv ai-email-coach-env", "创建虚拟环境")

def install_dependencies():
    """安装依赖包"""
    # 核心依赖列表（按安装顺序）
    dependencies = [
        "pip --upgrade",
        "fastapi",
        "uvicorn",
        "httpx",
        "python-dotenv",
        "pydantic[email]",
        "supabase"
    ]
    
    print("📦 开始安装依赖包...")
    
    for dep in dependencies:
        if dep == "pip --upgrade":
            success = run_command("python -m pip install --upgrade pip", "升级pip")
        else:
            success = run_command(f"pip install {dep}", f"安装 {dep}")
        
        if not success:
            print(f"⚠️ {dep} 安装失败，但继续尝试其他包...")
    
    return True

def verify_installation():
    """验证安装结果"""
    print("🔍 验证安装结果...")
    
    test_imports = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("httpx", "HTTPX"),
        ("supabase", "Supabase"),
        ("pydantic", "Pydantic")
    ]
    
    success_count = 0
    
    for module, name in test_imports:
        try:
            __import__(module)
            print(f"✅ {name} 导入成功")
            success_count += 1
        except ImportError:
            print(f"❌ {name} 导入失败")
    
    print(f"\n📊 安装结果: {success_count}/{len(test_imports)} 个包可用")
    
    return success_count >= 4  # 至少4个核心包可用

def main():
    """主安装流程"""
    print("🚀 AI邮件督导系统 - 自动化安装\n")
    
    # 检查Python版本
    if not check_python_version():
        print("\n❌ 安装失败：Python版本不符合要求")
        return
    
    # 创建虚拟环境
    if not create_virtual_env():
        print("\n⚠️ 虚拟环境创建失败，继续使用全局环境")
    
    # 安装依赖
    install_dependencies()
    
    # 验证安装
    if verify_installation():
        print("\n🎉 安装完成！")
        print("\n下一步:")
        print("1. 运行: python minimal_test.py")
        print("2. 如果测试通过，运行: python simple_test.py")
        print("3. 最后启动应用: python main.py")
    else:
        print("\n⚠️ 安装不完整，但可以尝试运行测试")
        print("运行: python minimal_test.py")

if __name__ == "__main__":
    main()