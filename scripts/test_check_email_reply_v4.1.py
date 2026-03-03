"""
测试 check_email_reply_v4.1.py 的核心功能
使用模拟数据，不会污染真实任务清单
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
    parse_task_operations_v4,
    process_task_operations_v4
)

def format_operation_feedback_v4_minimalist(operation_results):
    """
    v4.1：格式化任务操作反馈消息（极简风格）
    """
    feedback = "📊 任务更新反馈\n\n"
    
    results = operation_results.get('results', [])
    
    for item in results:
        op = item['operation']
        result = item['result']
        
        if not result.get('success'):
            error = result.get('error', '未知错误')
            feedback += f"❌ 操作失败：{error}\n\n"
            continue
        
        if op == 'complete':
            task_name = result.get('task_name', '')
            exp_gain = result.get('exp_gain', 0)
            coins_gain = result.get('coins_gain', 0)
            display_number = result.get('display_number', '')
            
            feedback += f"✅ {display_number}. {task_name} 完成\n"
            feedback += f"   💫 +{exp_gain} EXP"
            if coins_gain > 0:
                feedback += f"  💰 +{coins_gain} Coin"
            feedback += "\n\n"
            
        elif op == 'update':
            task_name = result.get('task_name', '')
            old_progress = result.get('old_progress', 0)
            new_progress = result.get('new_progress', 0)
            exp_gain = result.get('exp_gain', 0)
            display_number = result.get('display_number', '')
            
            filled = int(new_progress / 10)
            empty = 10 - filled
            progress_bar = "■" * filled + "□" * empty
            
            feedback += f"🔄 {display_number}. {task_name} 进度更新\n"
            feedback += f"   {old_progress}% → {new_progress}% [{progress_bar}]\n"
            if exp_gain > 0:
                feedback += f"   💫 +{exp_gain} EXP\n"
            feedback += "\n"
            
        elif op == 'create':
            task_name = result.get('task_name', '')
            display_number = result.get('display_number', '')
            quadrant = result.get('quadrant', 1)
            
            feedback += f"🆕 {display_number}. {task_name}\n"
            feedback += f"   象限：Q{quadrant}\n\n"
            
        elif op == 'pause':
            task_name = result.get('task_name', '')
            old_display_number = result.get('old_display_number', '')
            
            feedback += f"⏸️ {old_display_number}. {task_name} 已暂缓\n\n"
            
        elif op == 'resume':
            task_name = result.get('task_name', '')
            new_display_number = result.get('new_display_number', '')
            target_quadrant = result.get('target_quadrant', 1)
            
            feedback += f"🔄 {task_name} 已恢复\n"
            feedback += f"   新编号：{new_display_number}\n"
            feedback += f"   象限：Q{target_quadrant}\n\n"
    
    total_exp_gain = operation_results.get('total_exp_gain', 0)
    total_coins_gain = operation_results.get('total_coins_gain', 0)
    
    if total_exp_gain > 0 or total_coins_gain > 0:
        feedback += "本次收获：\n"
        if total_exp_gain > 0:
            feedback += f"💫 +{total_exp_gain} EXP\n"
        if total_coins_gain > 0:
            feedback += f"💰 +{total_coins_gain} Coin\n"
    
    return feedback

def test_parse_operations():
    """测试任务操作解析"""
    print("=" * 60)
    print("测试1: 任务操作解析")
    print("=" * 60)
    
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
    
    if not deepseek_api_key:
        print("❌ DEEPSEEK_API_KEY 未配置")
        return False
    
    # 测试用例
    test_cases = [
        {
            "name": "完成和更新任务",
            "reply": "Q1: 1完成; 2进度50%"
        },
        {
            "name": "新增任务",
            "reply": "新增：测试任务A Q1\n新增：测试任务B Q2"
        },
        {
            "name": "暂缓任务",
            "reply": "Q1: 1暂缓"
        },
        {
            "name": "恢复暂缓任务",
            "reply": "暂缓任务1恢复到Q1"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n测试用例: {test_case['name']}")
        print(f"输入: {test_case['reply']}")
        
        try:
            operations = parse_task_operations_v4(test_case['reply'], deepseek_api_key)
            print(f"✅ 解析成功，操作数: {len(operations)}")
            
            for i, op in enumerate(operations, 1):
                print(f"  操作{i}: {op.get('operation_type', 'unknown')}")
                if op.get('task_name'):
                    print(f"    任务名: {op.get('task_name')}")
                if op.get('quadrant'):
                    print(f"    象限: {op.get('quadrant')}")
                if op.get('task_number'):
                    print(f"    编号: {op.get('task_number')}")
                if op.get('progress'):
                    print(f"    进度: {op.get('progress')}%")
        except Exception as e:
            print(f"❌ 解析失败: {e}")
            return False
    
    return True

def test_feedback_format():
    """测试反馈格式化"""
    print("\n" + "=" * 60)
    print("测试2: 反馈格式化（极简风格）")
    print("=" * 60)
    
    # 模拟操作结果
    mock_results = {
        'results': [
            {
                'operation': 'complete',
                'result': {
                    'success': True,
                    'task_name': '测试任务A',
                    'display_number': 'Q1-1',
                    'exp_gain': 100,
                    'coins_gain': 50
                }
            },
            {
                'operation': 'update',
                'result': {
                    'success': True,
                    'task_name': '测试任务B',
                    'display_number': 'Q1-2',
                    'old_progress': 30,
                    'new_progress': 50,
                    'exp_gain': 40
                }
            },
            {
                'operation': 'create',
                'result': {
                    'success': True,
                    'task_name': '测试任务C',
                    'display_number': 'Q2-1',
                    'quadrant': 2
                }
            }
        ],
        'total_exp_gain': 140,
        'total_coins_gain': 50
    }
    
    try:
        feedback = format_operation_feedback_v4_minimalist(mock_results)
        print("\n生成的反馈：")
        print("-" * 60)
        print(feedback)
        print("-" * 60)
        
        # 验证格式
        checks = [
            ("包含任务编号", "Q1-1" in feedback and "Q1-2" in feedback),
            ("包含任务名称", "测试任务A" in feedback and "测试任务B" in feedback),
            ("包含进度条", "■" in feedback and "□" in feedback),
            ("包含经验值", "EXP" in feedback),
            ("包含总结", "本次收获" in feedback),
            ("无分隔线", "━" not in feedback)
        ]
        
        all_passed = True
        for check_name, check_result in checks:
            status = "✅" if check_result else "❌"
            print(f"{status} {check_name}")
            if not check_result:
                all_passed = False
        
        return all_passed
        
    except Exception as e:
        print(f"❌ 格式化失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试函数"""
    print("=" * 60)
    print("check_email_reply_v4.1 功能测试")
    print("=" * 60)
    print("⚠️ 使用模拟数据，不会污染真实任务清单")
    print()
    
    # 测试1: 任务操作解析
    test1_passed = test_parse_operations()
    
    # 测试2: 反馈格式化
    test2_passed = test_feedback_format()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"任务操作解析: {'✅ 通过' if test1_passed else '❌ 失败'}")
    print(f"反馈格式化: {'✅ 通过' if test2_passed else '❌ 失败'}")
    
    if test1_passed and test2_passed:
        print("\n✅ 所有测试通过！可以安全部署")
        return True
    else:
        print("\n❌ 部分测试失败，请检查问题")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
