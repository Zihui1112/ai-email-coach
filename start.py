"""
安全启动脚本 - 检查配置后再启动应用
"""

import os
import sys
from dotenv import load_dotenv

def check_environment():
    """检查环境变量配置"""
    print("🔧 检查环境配置...")
    
    # 加载.env文件
    load_dotenv()
    
    required_vars = {
        "SUPABASE_URL": "Supabase数据库URL",
        "SUPABASE_KEY": "Supabase API密钥", 
        "RESEND_API_KEY": "Resend邮件API密钥",
        "DEEPSEEK_API_KEY": "DeepSeek LLM API密钥"
    }
    
    missing_vars = []
    invalid_vars = []
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if not value:
            missing_vars.append(f"{var} ({description})")
        elif value in ["your-webhook-secret-will-be-generated", "whsec_你从resend获取的实际secret"]:
            invalid_vars.append(f"{var} ({description})")
        else:
            print(f"   ✅ {var}: 已配置")
    
    if missing_vars:
        print(f"\n❌ 缺少环境变量:")
        for var in missing_vars:
            print(f"   - {var}")
        return False
    
    if invalid_vars:
        print(f"\n⚠️ 需要更新的环境变量:")
        for var in invalid_vars:
            print(f"   - {var}")
        print("   (这些是示例值，需要替换为真实的API密钥)")
    
    print("✅ 环境配置检查完成")
    return True

def test_imports():
    """测试必要的包导入"""
    print("\n📦 检查依赖包...")
    
    required_packages = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("httpx", "HTTPX"),
        ("supabase", "Supabase"),
        ("pydantic", "Pydantic")
    ]
    
    missing_packages = []
    
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"   ✅ {name}: 已安装")
        except ImportError:
            missing_packages.append(name)
            print(f"   ❌ {name}: 未安装")
    
    if missing_packages:
        print(f"\n❌ 缺少依赖包: {', '.join(missing_packages)}")
        print("请运行: python setup.py")
        return False
    
    print("✅ 所有依赖包检查完成")
    return True

def start_application():
    """启动应用"""
    print("\n🚀 启动AI邮件督导系统...")
    
    try:
        # 导入并启动应用
        import uvicorn
        from main import app
        
        print("✅ 应用模块加载成功")
        print("🌐 服务启动中...")
        print("📍 访问地址: http://localhost:8000")
        print("📍 API文档: http://localhost:8000/docs")
        print("📍 健康检查: http://localhost:8000/health")
        print("\n按 Ctrl+C 停止服务\n")
        
        # 启动服务
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
        
    except KeyboardInterrupt:
        print("\n👋 服务已停止")
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        print("\n建议:")
        print("1. 检查.env文件配置")
        print("2. 运行 python minimal_test.py 进行诊断")
        print("3. 确保Supabase数据库表已创建")

def main():
    """主函数"""
    print("🔍 AI邮件督导系统 - 启动前检查\n")
    
    # 检查环境变量
    if not check_environment():
        print("\n❌ 环境配置不完整，无法启动")
        print("\n解决方案:")
        print("1. 检查.env文件是否存在")
        print("2. 确保所有API密钥都已正确配置")
        return
    
    # 检查依赖包
    if not test_imports():
        print("\n❌ 依赖包不完整，无法启动")
        return
    
    # 启动应用
    start_application()

if __name__ == "__main__":
    main()