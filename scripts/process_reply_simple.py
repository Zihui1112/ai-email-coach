"""
简化的处理用户回复脚本 - 不依赖 FastAPI
"""
import os
import sys
import requests
import json
import re
from datetime import datetime

def process_user_reply(reply_content):
    """处理用户回复"""
    print(f"[{datetime.now()}] 开始处理用户回复")
    print(f"回复内容: {reply_content[:100]}...")
    
    # 获取环境变量
    supabase_url = os.getenv("SUPABASE_URL", "").strip()
    supabase_key = os.getenv("SUPABASE_KEY", "").strip()
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    webhook_url = os.getenv("FEISHU_WEBHOOK_URL", "").strip()
    user_email = os.getenv("EMAIL_163_USERNAME", "").strip()
    
    if not all([supabase_url, supabase_key, deepseek_api_key, user_email]):
        print("❌ 环境变量未配置完整")
        return False
    
    try:
        # 使用 DeepSeek AI 解析回复
        print("\n使用 AI 解析回复...")
        
        headers = {
            "Authorization": f"Bearer {deepseek_api_key}",
            "Content-Type": "application/json"
        }
        
        prompt = f"""请解析以下任务更新内容，提取任务信息。

用户回复：
{reply_content}

请以JSON格式返回，包含以下字段：
- task_name: 任务名称
- progress: 进度百分比(0-100)
- quadrant: 象限(Q1/Q2/Q3/Q4)
- action: 动作(update/pause/complete)

如果有多个任务，返回JSON数组。
只返回JSON，不要其他内容。"""
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7
        }
        
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ AI 解析失败: {response.status_code}")
            return False
        
        result = response.json()
        ai_response = result['choices'][0]['message']['content'].strip()
        
        # 清理 markdown 代码块
        ai_response = re.sub(r'```json\s*', '', ai_response)
        ai_response = re.sub(r'```\s*$', '', ai_response)
        ai_response = ai_response.strip()
        
        print(f"AI 解析结果: {ai_response}")
        
        # 解析 JSON
        try:
            tasks_data = json.loads(ai_response)
            if not isinstance(tasks_data, list):
                tasks_data = [tasks_data]
        except:
            print("❌ 无法解析 AI 返回的 JSON")
            return False
        
        # 更新数据库
        print("\n更新数据库...")
        
        db_headers = {
            "apikey": supabase_key,
            "Authorization": f"Bearer {supabase_key}",
            "Content-Type": "application/json"
        }
        
        feedback_content = "📊 任务更新反馈\n\n"
        
        for task_data in tasks_data:
            task_name = task_data.get('task_name', '')
            progress = task_data.get('progress', 0)
            quadrant = task_data.get('quadrant', 'Q1')
            action = task_data.get('action', 'update')
            
            # 确保所有字段都不是 None
            if not task_name:
                continue
            
            # 确保 quadrant 不是 None 并且格式正确
            if not quadrant or not isinstance(quadrant, str) or not quadrant.strip():
                quadrant = 'Q1'
            else:
                quadrant = quadrant.strip().upper()
                # 如果不是 Q1-Q4 格式，默认为 Q1
                if not (quadrant.startswith('Q') and len(quadrant) == 2 and quadrant[1] in '1234'):
                    quadrant = 'Q1'
            
            # 确保 progress 是数字
            try:
                progress = int(progress) if progress else 0
                # 限制在 0-100 范围内
                progress = max(0, min(100, progress))
            except:
                progress = 0
            
            # 确保 action 不是 None
            if not action or not isinstance(action, str):
                action = 'update'
            else:
                action = action.strip().lower()
                # 只允许特定的 action 值
                if action not in ['update', 'pause', 'complete']:
                    action = 'update'
            
            # 查询任务是否存在
            query_url = f"{supabase_url}/rest/v1/tasks?user_email=eq.{user_email}&task_name=eq.{task_name}&select=*"
            query_response = requests.get(query_url, headers=db_headers, timeout=30)
            
            if query_response.status_code == 200:
                existing_tasks = query_response.json()
                
                if existing_tasks:
                    # 更新现有任务
                    task_id = existing_tasks[0]['id']
                    update_url = f"{supabase_url}/rest/v1/tasks?id=eq.{task_id}"
                    
                    update_data = {
                        "progress_percentage": progress,
                        "quadrant": int(quadrant[1]) if quadrant.startswith('Q') else 1,
                        "status": "completed" if action == "complete" else ("paused" if action == "pause" else "active"),
                        "updated_at": datetime.now().isoformat()
                    }
                    
                    update_response = requests.patch(update_url, headers=db_headers, json=update_data, timeout=30)
                    
                    if update_response.status_code in [200, 204]:
                        status_emoji = "✅" if action == "complete" else ("⏸️" if action == "pause" else "🔄")
                        filled = int(progress / 10)
                        empty = 10 - filled
                        progress_bar = "■" * filled + "□" * empty
                        
                        feedback_content += f"{status_emoji} {task_name}\n"
                        feedback_content += f"   进度：[{progress_bar}] {progress}%\n"
                        feedback_content += f"   象限: {quadrant}\n\n"
                    else:
                        print(f"更新任务失败: {update_response.status_code}")
                else:
                    # 创建新任务
                    create_url = f"{supabase_url}/rest/v1/tasks"
                    
                    create_data = {
                        "user_email": user_email,
                        "task_name": task_name,
                        "progress_percentage": progress,
                        "quadrant": int(quadrant[1]) if quadrant.startswith('Q') else 1,
                        "status": "active",
                        "created_at": datetime.now().isoformat(),
                        "updated_at": datetime.now().isoformat()
                    }
                    
                    create_response = requests.post(create_url, headers=db_headers, json=create_data, timeout=30)
                    
                    if create_response.status_code in [200, 201]:
                        filled = int(progress / 10)
                        empty = 10 - filled
                        progress_bar = "■" * filled + "□" * empty
                        
                        feedback_content += f"🆕 {task_name}\n"
                        feedback_content += f"   进度：[{progress_bar}] {progress}%\n"
                        feedback_content += f"   象限: {quadrant}\n\n"
                    else:
                        print(f"创建任务失败: {create_response.status_code}")
        
        feedback_content += "💪 继续加油！"
        
        # 发送反馈到飞书
        if webhook_url:
            message = {
                "msg_type": "text",
                "content": {
                    "text": feedback_content
                }
            }
            
            response = requests.post(webhook_url, json=message, timeout=30)
            
            if response.status_code == 200:
                print("✅ 反馈已发送到飞书")
            else:
                print(f"❌ 发送飞书消息失败: {response.status_code}")
        
        print("\n✅ 用户回复处理完成")
        return True
        
    except Exception as e:
        print(f"❌ 处理失败: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ 缺少回复内容参数")
        sys.exit(1)
    
    reply_content = sys.argv[1]
    success = process_user_reply(reply_content)
    sys.exit(0 if success else 1)
