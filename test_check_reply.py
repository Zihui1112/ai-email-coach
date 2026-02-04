"""
测试检查邮件回复功能
"""
import os
import sys

# 设置环境变量
os.environ["EMAIL_163_USERNAME"] = "15302814198@163.com"
os.environ["EMAIL_163_PASSWORD"] = "JSewF34VrE5GGNwQ"
os.environ["SUPABASE_URL"] = "https://cnmxhxapwksjczfxugtx.supabase.co"
os.environ["SUPABASE_KEY"] = os.getenv("SUPABASE_KEY", "")  # 需要你的 service_role key
os.environ["DEEPSEEK_API_KEY"] = "sk-86436af0f3784ea5b99c66e08be29b23"
os.environ["FEISHU_WEBHOOK_URL"] = "https://open.feishu.cn/open-apis/bot/v2/hook/902a2c44-8edc-4cb4-a7cd-c3d935c8ed8c"

# 导入并运行检查脚本
sys.path.insert(0, 'scripts')
from check_email_reply import check_and_process_email_reply

if __name__ == "__main__":
    print("=" * 60)
    print("测试检查邮件回复功能")
    print("=" * 60)
    print("\n请确保：")
    print("1. 你已经收到测试邮件")
    print("2. 你已经回复了测试邮件")
    print("3. SUPABASE_KEY 环境变量已设置（service_role key）")
    print("\n开始测试...\n")
    
    success = check_and_process_email_reply()
    
    if success:
        print("\n✅ 测试成功！")
        print("请检查飞书是否收到反馈消息")
    else:
        print("\n❌ 测试失败")
