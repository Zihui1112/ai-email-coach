"""
测试 GitHub Secrets 配置
"""
import os
import sys

def test_secrets():
    """测试所有环境变量"""
    print("=" * 60)
    print("测试 GitHub Secrets 配置")
    print("=" * 60)
    
    secrets = {
        "SUPABASE_URL": os.getenv("SUPABASE_URL"),
        "SUPABASE_KEY": os.getenv("SUPABASE_KEY"),
        "DEEPSEEK_API_KEY": os.getenv("DEEPSEEK_API_KEY"),
        "FEISHU_WEBHOOK_URL": os.getenv("FEISHU_WEBHOOK_URL"),
        "EMAIL_163_USERNAME": os.getenv("EMAIL_163_USERNAME")
    }
    
    all_ok = True
    
    for name, value in secrets.items():
        print(f"\n检查 {name}:")
        
        if not value:
            print(f"  ❌ 未设置")
            all_ok = False
            continue
        
        # 检查长度
        print(f"  长度: {len(value)}")
        
        # 检查是否包含换行符
        if '\n' in value or '\r' in value:
            print(f"  ❌ 包含换行符！")
            all_ok = False
        else:
            print(f"  ✅ 无换行符")
        
        # 检查首尾空格
        if value != value.strip():
            print(f"  ❌ 包含首尾空格！")
            print(f"  原始长度: {len(value)}, 去空格后: {len(value.strip())}")
            all_ok = False
        else:
            print(f"  ✅ 无首尾空格")
        
        # 显示前后各10个字符（用于调试）
        if len(value) > 20:
            print(f"  开头: {repr(value[:10])}")
            print(f"  结尾: {repr(value[-10:])}")
        else:
            print(f"  完整值: {repr(value)}")
    
    print("\n" + "=" * 60)
    if all_ok:
        print("✅ 所有 Secrets 配置正确！")
        return True
    else:
        print("❌ 发现配置问题，请修复后重试")
        return False

if __name__ == "__main__":
    success = test_secrets()
    sys.exit(0 if success else 1)
