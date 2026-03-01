"""
v4.0 任务编号系统快速验证脚本
用于部署前验证所有核心函数是否正常工作
"""
import os
import sys
from datetime import datetime

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 手动加载 .env 文件
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
if os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip().strip('"').strip("'")

from gamification_utils import (
    find_task,
    get_max_task_order,
    find_paused_task,
    get_paused_tasks_to_remind,
    complete_task,
    update_task_progress,
    create_task,
    pause_task,
    resume_paused_task
)

def test_v4_functions():
    """测试 v4.0 核心函数"""
    print("=" * 60)
    print("v4.0 任务编号系统 - 快速验证")
    print("=" * 60)
    
    # 获取环境变量
    supabase_url = os.getenv("SUPABASE_URL", "").strip()
    supabase_key = os.getenv("SUPABASE_KEY", "").strip()
    user_email = os.getenv("EMAIL_163_USERNAME", "").strip()
    
    if not all([supabase_url, supabase_key, user_email]):
        print("❌ 环境变量未配置完整")
        return False
    
    headers = {
        "apikey": supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type": "application/json"
    }
    
    print(f"\n测试用户: {user_email}")
    print(f"Supabase URL: {supabase_url}")
    
    # 测试1: 获取最大任务编号
    print("\n" + "=" * 60)
    print("测试1: get_max_task_order()")
    print("=" * 60)
    try:
        max_order = get_max_task_order(supabase_url, headers, user_email, 1)
        print(f"✅ Q1象限最大编号: {max_order}")
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False
    
    # 测试2: 查找任务
    print("\n" + "=" * 60)
    print("测试2: find_task()")
    print("=" * 60)
    try:
        if max_order > 0:
            task = find_task(supabase_url, headers, user_email, 1, 1)
            if task:
                print(f"✅ 找到任务: {task.get('task_name', 'N/A')}")
                print(f"   编号: Q1-{task.get('task_order', 'N/A')}")
                print(f"   进度: {task.get('progress_percentage', 0)}%")
            else:
                print("⚠️  Q1-1 任务不存在（可能正常）")
        else:
            print("⚠️  Q1象限暂无任务")
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False
    
    # 测试3: 获取暂缓任务
    print("\n" + "=" * 60)
    print("测试3: get_paused_tasks_to_remind()")
    print("=" * 60)
    try:
        paused_tasks = get_paused_tasks_to_remind(supabase_url, headers, user_email)
        print(f"✅ 需要提醒的暂缓任务数: {len(paused_tasks)}")
        for task in paused_tasks[:3]:  # 只显示前3个
            print(f"   - {task.get('task_name', 'N/A')} (编号: {task.get('task_order', 'N/A')})")
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False
    
    # 测试4: 创建测试任务
    print("\n" + "=" * 60)
    print("测试4: create_task()")
    print("=" * 60)
    test_task_name = f"v4.0测试任务_{datetime.now().strftime('%H%M%S')}"
    try:
        result = create_task(supabase_url, headers, user_email, test_task_name, 4)
        if result.get('success'):
            print(f"✅ 创建成功: {result.get('display_number', 'N/A')}")
            test_task_number = result.get('task_order')
        else:
            print(f"❌ 创建失败: {result.get('message', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False
    
    # 测试5: 更新任务进度
    print("\n" + "=" * 60)
    print("测试5: update_task_progress()")
    print("=" * 60)
    try:
        result = update_task_progress(supabase_url, headers, user_email, 4, test_task_number, 50)
        if result.get('success'):
            print(f"✅ 更新成功")
            print(f"   进度: {result.get('new_progress', 0)}%")
            print(f"   经验值: +{result.get('exp_gain', 0)} EXP")
        else:
            print(f"❌ 更新失败: {result.get('message', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False
    
    # 测试6: 暂缓任务
    print("\n" + "=" * 60)
    print("测试6: pause_task()")
    print("=" * 60)
    try:
        result = pause_task(supabase_url, headers, user_email, 4, test_task_number)
        if result.get('success'):
            print(f"✅ 暂缓成功")
            print(f"   任务: {result.get('task_name', 'N/A')}")
        else:
            print(f"❌ 暂缓失败: {result.get('message', 'Unknown error')}")
            return False
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False
    
    # 测试7: 查找暂缓任务
    print("\n" + "=" * 60)
    print("测试7: find_paused_task()")
    print("=" * 60)
    try:
        # 获取最新的暂缓任务编号
        paused_tasks = get_paused_tasks_to_remind(supabase_url, headers, user_email)
        if paused_tasks:
            paused_task_number = paused_tasks[-1].get('task_order')  # 最后一个应该是我们刚暂缓的
            task = find_paused_task(supabase_url, headers, user_email, paused_task_number)
            if task:
                print(f"✅ 找到暂缓任务: {task.get('task_name', 'N/A')}")
            else:
                print("⚠️  未找到暂缓任务")
        else:
            print("⚠️  暂无暂缓任务")
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False
    
    # 测试8: 恢复暂缓任务
    print("\n" + "=" * 60)
    print("测试8: resume_paused_task()")
    print("=" * 60)
    try:
        if paused_tasks:
            paused_task_number = paused_tasks[-1].get('task_order')
            result = resume_paused_task(supabase_url, headers, user_email, paused_task_number, 4)
            if result.get('success'):
                print(f"✅ 恢复成功")
                print(f"   新编号: {result.get('new_display_number', 'N/A')}")
                resumed_task_number = result.get('new_task_order')
            else:
                print(f"❌ 恢复失败: {result.get('message', 'Unknown error')}")
                return False
        else:
            print("⚠️  跳过（无暂缓任务）")
            resumed_task_number = test_task_number
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False
    
    # 测试9: 完成任务（清理测试数据）
    print("\n" + "=" * 60)
    print("测试9: complete_task() - 清理测试数据")
    print("=" * 60)
    try:
        result = complete_task(supabase_url, headers, user_email, 4, resumed_task_number)
        if result.get('success'):
            print(f"✅ 完成成功（测试任务已清理）")
            print(f"   经验值: +{result.get('exp_gain', 0)} EXP")
        else:
            print(f"❌ 完成失败: {result.get('message', 'Unknown error')}")
            print("⚠️  请手动删除测试任务")
            return False
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False
    
    # 全部测试通过
    print("\n" + "=" * 60)
    print("✅ 所有测试通过！v4.0 系统运行正常")
    print("=" * 60)
    print("\n可以安全部署到生产环境。")
    
    return True

if __name__ == "__main__":
    success = test_v4_functions()
    sys.exit(0 if success else 1)
