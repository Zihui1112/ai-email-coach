"""
独立运行的AI督导系统
可以直接运行，无需部署
支持：
1. 立即发送复盘提醒
2. 处理用户回复
3. 定时运行（配合Windows任务计划或crontab）
"""

import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

async def send_daily_review():
    """发送每日复盘提醒"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始发送每日复盘提醒")
    
    try:
        import httpx
        from supabase import create_client
        
        # 环境变量
        webhook_url = os.getenv("FEISHU_WEBHOOK_URL")
        user_email = os.getenv("EMAIL_163_USERNAME")
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not all([webhook_url, user_email, supabase_url, supabase_key]):
            print("❌ 环境变量未配置完整，请检查.env文件")
            return False
        
        # 连接数据库
        supabase = create_client(supabase_url, supabase_key)
        
        # 获取今日任务
        response = supabase.table('tasks').select('*').eq('user_email', user_email).eq('status', 'active').execute()
        tasks = response.data
        
        # 生成消息内容
        content = "🌙 晚上好！今天的任务完成情况如何？\n\n"
        content += "📋 今日任务清单：\n"
        
        if tasks:
            for task in tasks:
                progress = task.get('progress', 0)
                task_name = task.get('task_name', '未命名任务')
                quadrant = task.get('quadrant', 'Q1')
                
                # 生成进度条
                filled = int(progress / 10)
                empty = 10 - filled
                progress_bar = "■" * filled + "□" * empty
                
                status_emoji = "✅" if progress == 100 else "🔄"
                
                content += f"\n{status_emoji} {task_name}\n"
                content += f"   进度：[{progress_bar}] {progress}%\n"
                content += f"   象限: {quadrant}\n"
        else:
            content += "\n暂无进行中的任务\n"
        
        content += "\n\n💬 请回复以下内容：\n"
        content += "1. 今天完成了哪些任务？进度如何？\n"
        content += "2. 明天计划做什么？\n"
        content += "3. 有哪些任务需要暂缓？\n"
        content += "\n示例：完成了用户登录功能80%，明天做数据库设计Q2任务"
        
        # 发送到飞书
        message = {
            "msg_type": "text",
            "content": {
                "text": f"📊 每日复盘\n\n{content}"
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, json=message, timeout=30.0)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("StatusCode") == 0:
                    print("✅ 每日复盘提醒发送成功")
                    return True
                else:
                    print(f"❌ 飞书返回错误: {result}")
                    return False
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ 发送失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def process_user_reply(reply_text: str):
    """处理用户回复"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 开始处理用户回复")
    print(f"回复内容: {reply_text[:100]}...")
    
    try:
        from main import llm_parser, db_syncer, email_generator
        import httpx
        
        user_email = os.getenv("EMAIL_163_USERNAME")
        webhook_url = os.getenv("FEISHU_WEBHOOK_URL")
        
        # 使用LLM解析
        parse_result = await llm_parser.parse_reply(reply_text, user_email)
        
        if parse_result.task_updates:
            print(f"🧠 AI解析结果: {len(parse_result.task_updates)} 个任务")
            
            # 更新数据库
            await db_syncer.sync_task_updates(parse_result.task_updates, user_email)
            
            # 生成反馈
            feedback_content = await email_generator.generate_feedback_email(
                user_email, parse_result.task_updates
            )
            
            # 发送反馈到飞书
            message = {
                "msg_type": "text",
                "content": {
                    "text": f"📊 任务更新反馈\n\n{feedback_content}"
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(webhook_url, json=message, timeout=30.0)
                
                if response.status_code == 200:
                    print("✅ 反馈发送成功")
                    return True
                else:
                    print(f"❌ 反馈发送失败: {response.status_code}")
                    return False
        else:
            print("⚠️ 未能解析出任务信息")
            
            # 发送提示消息
            message = {
                "msg_type": "text",
                "content": {
                    "text": "⚠️ 未能识别任务信息，请提供更清晰的描述\n\n示例：完成了用户登录功能80%，这是Q1任务"
                }
            }
            
            async with httpx.AsyncClient() as client:
                await client.post(webhook_url, json=message, timeout=30.0)
            
            return False
            
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def print_menu():
    """打印菜单"""
    print("\n" + "="*60)
    print("🤖 AI督导系统 - 独立运行版")
    print("="*60)
    print("\n请选择操作：")
    print("1. 发送每日复盘提醒")
    print("2. 处理用户回复")
    print("3. 测试飞书连接")
    print("4. 查看配置")
    print("0. 退出")
    print()

async def test_feishu():
    """测试飞书连接"""
    print("测试飞书连接...")
    
    try:
        import httpx
        webhook_url = os.getenv("FEISHU_WEBHOOK_URL")
        
        if not webhook_url:
            print("❌ 未配置FEISHU_WEBHOOK_URL")
            return False
        
        message = {
            "msg_type": "text",
            "content": {
                "text": f"🧪 测试消息\n\n时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n如果你看到这条消息，说明飞书连接正常！"
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(webhook_url, json=message, timeout=30.0)
            
            if response.status_code == 200:
                result = response.json()
                if result.get("StatusCode") == 0:
                    print("✅ 飞书连接测试成功")
                    return True
                else:
                    print(f"❌ 飞书返回错误: {result}")
                    return False
            else:
                print(f"❌ HTTP请求失败: {response.status_code}")
                return False
                
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        return False

def show_config():
    """显示配置"""
    print("\n当前配置：")
    print(f"SUPABASE_URL: {os.getenv('SUPABASE_URL', '未配置')}")
    print(f"SUPABASE_KEY: {'已配置' if os.getenv('SUPABASE_KEY') else '未配置'}")
    print(f"DEEPSEEK_API_KEY: {'已配置' if os.getenv('DEEPSEEK_API_KEY') else '未配置'}")
    print(f"FEISHU_WEBHOOK_URL: {'已配置' if os.getenv('FEISHU_WEBHOOK_URL') else '未配置'}")
    print(f"EMAIL_163_USERNAME: {os.getenv('EMAIL_163_USERNAME', '未配置')}")

async def main():
    """主函数"""
    # 如果有命令行参数，直接执行
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "review":
            # 发送复盘提醒
            success = await send_daily_review()
            sys.exit(0 if success else 1)
        
        elif command == "reply":
            # 处理回复（从命令行参数或文件读取）
            if len(sys.argv) > 2:
                reply_text = sys.argv[2]
            else:
                print("请提供回复内容：python standalone_coach.py reply \"你的回复内容\"")
                sys.exit(1)
            
            success = await process_user_reply(reply_text)
            sys.exit(0 if success else 1)
        
        elif command == "test":
            # 测试飞书连接
            success = await test_feishu()
            sys.exit(0 if success else 1)
        
        else:
            print(f"未知命令: {command}")
            print("可用命令: review, reply, test")
            sys.exit(1)
    
    # 交互式菜单
    while True:
        print_menu()
        
        try:
            choice = input("请输入选项 (0-4): ").strip()
            
            if choice == "0":
                print("\n👋 再见！")
                break
            
            elif choice == "1":
                print("\n📤 发送每日复盘提醒...")
                await send_daily_review()
            
            elif choice == "2":
                print("\n请输入用户回复内容（多行输入，输入END结束）：")
                lines = []
                while True:
                    line = input()
                    if line.strip().upper() == "END":
                        break
                    lines.append(line)
                
                reply_text = "\n".join(lines)
                if reply_text.strip():
                    await process_user_reply(reply_text)
                else:
                    print("❌ 回复内容为空")
            
            elif choice == "3":
                print("\n🧪 测试飞书连接...")
                await test_feishu()
            
            elif choice == "4":
                show_config()
            
            else:
                print("❌ 无效选项，请重新输入")
            
            input("\n按回车键继续...")
            
        except KeyboardInterrupt:
            print("\n\n👋 再见！")
            break
        except Exception as e:
            print(f"\n❌ 错误: {e}")
            input("\n按回车键继续...")

if __name__ == "__main__":
    asyncio.run(main())
