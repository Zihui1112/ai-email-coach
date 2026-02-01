"""
简化版AI邮件督导 - 使用POP3接收邮件
POP3比IMAP更简单，163邮箱支持更好
"""

import os
import poplib
import email
from email.header import decode_header
from datetime import datetime
import asyncio
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 导入已有的组件
from notification_manager import notification_manager

class SimpleEmailCoachPOP3:
    def __init__(self):
        # 163邮箱配置
        self.email_address = os.getenv("EMAIL_163_USERNAME")
        self.email_password = os.getenv("EMAIL_163_PASSWORD")
        
        # POP3服务器配置
        self.pop3_server = "pop.163.com"
        self.pop3_port = 995
        
        # 已处理的邮件ID集合
        self.processed_emails = set()
        
        print(f"📧 AI邮件督导初始化完成 (POP3模式)")
        print(f"   监听邮箱: {self.email_address}")
    
    def connect_pop3(self):
        """连接到POP3服务器"""
        try:
            mail = poplib.POP3_SSL(self.pop3_server, self.pop3_port)
            mail.user(self.email_address)
            mail.pass_(self.email_password)
            print("✅ POP3连接成功")
            return mail
        except Exception as e:
            print(f"❌ POP3连接失败: {e}")
            return None
    
    def get_emails(self, mail, limit=10):
        """获取最新的邮件"""
        try:
            # 获取邮件数量
            num_messages = len(mail.list()[1])
            print(f"📬 邮箱共有 {num_messages} 封邮件")
            
            if num_messages == 0:
                return []
            
            # 获取最新的N封邮件
            emails = []
            start = max(1, num_messages - limit + 1)
            
            for i in range(num_messages, start - 1, -1):
                # 获取邮件
                response, lines, octets = mail.retr(i)
                
                # 解析邮件
                msg_content = b'\r\n'.join(lines)
                email_data = self.parse_email(msg_content, str(i))
                
                if email_data and email_data["email_id"] not in self.processed_emails:
                    emails.append(email_data)
            
            return emails
            
        except Exception as e:
            print(f"❌ 获取邮件失败: {e}")
            return []
    
    def parse_email(self, msg_content, email_id):
        """解析邮件内容"""
        try:
            # 解析邮件
            email_message = email.message_from_bytes(msg_content)
            
            # 获取发件人
            from_header = email_message.get("From", "")
            from_email = email.utils.parseaddr(from_header)[1]
            
            # 获取主题
            subject = email_message.get("Subject", "")
            if subject:
                decoded_subject = decode_header(subject)[0]
                if isinstance(decoded_subject[0], bytes):
                    subject = decoded_subject[0].decode(decoded_subject[1] or "utf-8")
                else:
                    subject = decoded_subject[0]
            
            # 获取日期
            date_str = email_message.get("Date", "")
            
            # 获取邮件正文
            body = ""
            if email_message.is_multipart():
                for part in email_message.walk():
                    if part.get_content_type() == "text/plain":
                        try:
                            payload = part.get_payload(decode=True)
                            if payload:
                                # 尝试多种编码
                                for encoding in ['utf-8', 'gbk', 'gb2312']:
                                    try:
                                        body = payload.decode(encoding)
                                        break
                                    except:
                                        continue
                            if body:
                                break
                        except:
                            pass
            else:
                try:
                    payload = email_message.get_payload(decode=True)
                    if payload:
                        for encoding in ['utf-8', 'gbk', 'gb2312']:
                            try:
                                body = payload.decode(encoding)
                                break
                            except:
                                continue
                except:
                    body = str(email_message.get_payload())
            
            return {
                "from": from_email,
                "subject": subject,
                "body": body.strip(),
                "date": date_str,
                "email_id": email_id
            }
            
        except Exception as e:
            print(f"❌ 解析邮件失败: {e}")
            return None
    
    async def process_email(self, email_data):
        """处理邮件并发送回复"""
        try:
            from_email = email_data["from"]
            subject = email_data["subject"]
            body = email_data["body"]
            
            print(f"\n📬 收到新邮件:")
            print(f"   发件人: {from_email}")
            print(f"   主题: {subject}")
            print(f"   日期: {email_data['date']}")
            print(f"   内容: {body[:100]}...")
            
            # 使用LLM解析邮件内容
            from main import llm_parser, db_syncer
            
            parse_result = await llm_parser.parse_reply(body, from_email)
            
            if parse_result.task_updates:
                print(f"   🧠 AI解析结果: {len(parse_result.task_updates)} 个任务")
                
                # 更新数据库
                await db_syncer.sync_task_updates(parse_result.task_updates, from_email)
                
                # 生成回复邮件
                from main import email_generator
                feedback_content = await email_generator.generate_feedback_email(
                    from_email, parse_result.task_updates
                )
                
                # 发送回复
                reply_subject = f"Re: {subject}" if not subject.startswith("Re:") else subject
                
                results = await notification_manager.send_notification(
                    from_email,
                    reply_subject,
                    feedback_content
                )
                
                success_count = sum(1 for success in results.values() if success)
                if success_count > 0:
                    print(f"   ✅ 回复已发送 ({success_count} 个平台)")
                else:
                    print(f"   ❌ 回复发送失败")
            else:
                print(f"   ⚠️ 未能解析出任务信息")
                
        except Exception as e:
            print(f"❌ 处理邮件失败: {e}")
            import traceback
            traceback.print_exc()
    
    async def check_and_process_emails(self):
        """检查并处理新邮件"""
        mail = self.connect_pop3()
        
        if not mail:
            return
        
        try:
            # 获取最新邮件
            emails = self.get_emails(mail, limit=10)
            
            if not emails:
                print("📭 没有新邮件需要处理")
                return
            
            print(f"📬 发现 {len(emails)} 封新邮件需要处理")
            
            # 处理每封邮件
            for email_data in emails:
                # 处理邮件
                await self.process_email(email_data)
                
                # 记录已处理
                self.processed_emails.add(email_data["email_id"])
                
                # 避免处理过快
                await asyncio.sleep(2)
                
        except Exception as e:
            print(f"❌ 检查邮件失败: {e}")
            import traceback
            traceback.print_exc()
        finally:
            try:
                mail.quit()
            except:
                pass
    
    async def run(self, check_interval=60):
        """运行邮件监听循环"""
        print(f"\n🚀 AI邮件督导开始运行 (POP3模式)")
        print(f"   检查间隔: {check_interval}秒")
        print(f"   按 Ctrl+C 停止\n")
        
        try:
            while True:
                print(f"🔍 [{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 检查新邮件...")
                
                await self.check_and_process_emails()
                
                print(f"⏳ 等待 {check_interval} 秒后再次检查...\n")
                await asyncio.sleep(check_interval)
                
        except KeyboardInterrupt:
            print("\n👋 AI邮件督导已停止")

async def main():
    """主函数"""
    print("="*60)
    print("🤖 简化版AI邮件督导系统 (POP3)")
    print("="*60)
    print()
    
    # 检查配置
    email_address = os.getenv("EMAIL_163_USERNAME")
    email_password = os.getenv("EMAIL_163_PASSWORD")
    
    if not email_address or not email_password:
        print("❌ 错误：未配置163邮箱")
        print("请在.env文件中设置:")
        print("  EMAIL_163_USERNAME=你的163邮箱")
        print("  EMAIL_163_PASSWORD=你的163邮箱授权码")
        return
    
    # 创建并运行邮件督导
    coach = SimpleEmailCoachPOP3()
    
    # 询问检查间隔
    try:
        interval_input = input("请输入邮件检查间隔（秒，默认60秒，直接回车使用默认值）: ").strip()
        check_interval = int(interval_input) if interval_input else 60
    except ValueError:
        check_interval = 60
    
    await coach.run(check_interval)

if __name__ == "__main__":
    asyncio.run(main())
