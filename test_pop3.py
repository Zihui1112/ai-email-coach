"""
测试POP3连接
"""
import os
import poplib
from dotenv import load_dotenv

load_dotenv()

def test_pop3_connection():
    """测试POP3连接"""
    print("="*60)
    print("🧪 测试163邮箱POP3连接")
    print("="*60)
    print()
    
    email_address = os.getenv("EMAIL_163_USERNAME")
    email_password = os.getenv("EMAIL_163_PASSWORD")
    
    print(f"📧 邮箱地址: {email_address}")
    print(f"🔑 密码长度: {len(email_password) if email_password else 0} 字符")
    print()
    
    try:
        # 连接POP3服务器
        print("🔌 正在连接 pop.163.com:995...")
        mail = poplib.POP3_SSL("pop.163.com", 995)
        print("✅ SSL连接成功")
        
        # 登录
        print(f"🔐 正在登录 {email_address}...")
        mail.user(email_address)
        mail.pass_(email_password)
        print("✅ 登录成功")
        
        # 获取邮件统计
        print("\n📊 邮箱统计:")
        num_messages, total_size = mail.stat()
        print(f"   邮件总数: {num_messages}")
        print(f"   总大小: {total_size / 1024:.2f} KB")
        
        # 列出最新5封邮件
        print("\n📋 最新5封邮件:")
        response, listings, octets = mail.list()
        if num_messages > 0:
            start = max(1, num_messages - 4)
            for i in range(num_messages, start - 1, -1):
                print(f"   邮件 #{i}")
        
        # 关闭连接
        mail.quit()
        print("\n✅ 测试完成，POP3连接正常！")
        print("\n💡 POP3模式可以正常使用，建议使用 simple_email_coach_pop3.py")
        
    except poplib.error_proto as e:
        print(f"\n❌ POP3协议错误: {e}")
        print("\n💡 可能的原因:")
        print("   1. 邮箱密码错误（需要使用授权码）")
        print("   2. 未开启POP3服务")
    except Exception as e:
        print(f"\n❌ 连接失败: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_pop3_connection()
