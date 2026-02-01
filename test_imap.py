"""
测试IMAP连接和邮件获取
"""
import os
import imaplib
from dotenv import load_dotenv

load_dotenv()

def test_imap_connection():
    """测试IMAP连接"""
    print("="*60)
    print("🧪 测试163邮箱IMAP连接")
    print("="*60)
    print()
    
    email_address = os.getenv("EMAIL_163_USERNAME")
    email_password = os.getenv("EMAIL_163_PASSWORD")
    
    print(f"📧 邮箱地址: {email_address}")
    print(f"🔑 密码长度: {len(email_password) if email_password else 0} 字符")
    print()
    
    try:
        # 连接IMAP服务器
        print("🔌 正在连接 imap.163.com:993...")
        mail = imaplib.IMAP4_SSL("imap.163.com", 993)
        print("✅ SSL连接成功")
        
        # 登录
        print(f"🔐 正在登录 {email_address}...")
        mail.login(email_address, email_password)
        print("✅ 登录成功")
        
        # 列出所有文件夹
        print("\n📁 邮箱文件夹列表:")
        status, folders = mail.list()
        if status == "OK":
            for folder in folders:
                print(f"   {folder.decode()}")
        
        # 选择收件箱 - 163邮箱特殊处理
        print("\n📬 选择收件箱...")
        
        try:
            # 先尝试 STATUS 命令查看邮箱状态
            print("   检查INBOX状态...")
            typ, data = mail.status("INBOX", "(MESSAGES UNSEEN)")
            print(f"   STATUS结果: {typ} - {data}")
            
            # 尝试 SELECT
            print("   尝试SELECT INBOX...")
            typ, data = mail.select("INBOX")
            print(f"   SELECT结果: {typ}")
            print(f"   返回数据: {data}")
            
            if typ == "OK":
                print(f"✅ 收件箱选择成功，共 {data[0].decode()} 封邮件")
            else:
                print(f"❌ 选择收件箱失败")
                print("\n💡 可能的原因:")
                print("   1. 163邮箱IMAP服务未完全开启")
                print("   2. 需要在163邮箱设置中开启'IMAP/SMTP服务'")
                print("   3. 授权码权限不足")
                return
        except Exception as e:
            print(f"❌ 选择收件箱异常: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # 搜索未读邮件
        print("\n🔍 搜索未读邮件...")
        status, messages = mail.search(None, "UNSEEN")
        if status == "OK":
            email_ids = messages[0].split()
            print(f"✅ 找到 {len(email_ids)} 封未读邮件")
            
            if email_ids:
                print("\n📋 未读邮件ID列表:")
                for email_id in email_ids[:5]:  # 只显示前5封
                    print(f"   {email_id.decode()}")
                if len(email_ids) > 5:
                    print(f"   ... 还有 {len(email_ids) - 5} 封")
        else:
            print(f"❌ 搜索失败: {status}")
        
        # 搜索所有邮件
        print("\n🔍 搜索所有邮件...")
        status, messages = mail.search(None, "ALL")
        if status == "OK":
            all_email_ids = messages[0].split()
            print(f"✅ 找到 {len(all_email_ids)} 封邮件")
        
        # 关闭连接
        mail.close()
        mail.logout()
        print("\n✅ 测试完成，连接已关闭")
        
    except imaplib.IMAP4.error as e:
        print(f"\n❌ IMAP错误: {e}")
        print("\n💡 可能的原因:")
        print("   1. 邮箱密码错误（需要使用授权码，不是登录密码）")
        print("   2. 未开启IMAP服务")
        print("   3. 网络连接问题")
    except Exception as e:
        print(f"\n❌ 连接失败: {e}")

if __name__ == "__main__":
    test_imap_connection()
