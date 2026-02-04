"""
测试字段验证逻辑 - 验证修复是否有效
"""

def validate_task_data(task_data):
    """验证任务数据（模拟修复后的逻辑）"""
    task_name = task_data.get('task_name', '')
    progress = task_data.get('progress', 0)
    quadrant = task_data.get('quadrant', 'Q1')
    action = task_data.get('action', 'update')
    
    # 确保所有字段都不是 None
    if not task_name:
        return None, "任务名称为空"
    
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
    
    return {
        'task_name': task_name,
        'progress': progress,
        'quadrant': quadrant,
        'action': action
    }, None


# 测试用例
test_cases = [
    # 正常情况
    {
        'input': {'task_name': '用户登录', 'progress': 80, 'quadrant': 'Q1', 'action': 'update'},
        'expected': {'task_name': '用户登录', 'progress': 80, 'quadrant': 'Q1', 'action': 'update'}
    },
    # quadrant 为 None
    {
        'input': {'task_name': '数据库设计', 'progress': 50, 'quadrant': None, 'action': 'update'},
        'expected': {'task_name': '数据库设计', 'progress': 50, 'quadrant': 'Q1', 'action': 'update'}
    },
    # quadrant 格式错误
    {
        'input': {'task_name': 'API开发', 'progress': 30, 'quadrant': 'Q5', 'action': 'update'},
        'expected': {'task_name': 'API开发', 'progress': 30, 'quadrant': 'Q1', 'action': 'update'}
    },
    # progress 超出范围
    {
        'input': {'task_name': '测试', 'progress': 150, 'quadrant': 'Q2', 'action': 'update'},
        'expected': {'task_name': '测试', 'progress': 100, 'quadrant': 'Q2', 'action': 'update'}
    },
    # progress 为负数
    {
        'input': {'task_name': '部署', 'progress': -10, 'quadrant': 'Q3', 'action': 'update'},
        'expected': {'task_name': '部署', 'progress': 0, 'quadrant': 'Q3', 'action': 'update'}
    },
    # action 为 None
    {
        'input': {'task_name': '文档', 'progress': 60, 'quadrant': 'Q4', 'action': None},
        'expected': {'task_name': '文档', 'progress': 60, 'quadrant': 'Q4', 'action': 'update'}
    },
    # action 值错误
    {
        'input': {'task_name': '优化', 'progress': 40, 'quadrant': 'Q1', 'action': 'delete'},
        'expected': {'task_name': '优化', 'progress': 40, 'quadrant': 'Q1', 'action': 'update'}
    },
    # 所有字段都有问题
    {
        'input': {'task_name': '修复', 'progress': None, 'quadrant': '', 'action': ''},
        'expected': {'task_name': '修复', 'progress': 0, 'quadrant': 'Q1', 'action': 'update'}
    },
    # quadrant 小写
    {
        'input': {'task_name': '重构', 'progress': 70, 'quadrant': 'q2', 'action': 'UPDATE'},
        'expected': {'task_name': '重构', 'progress': 70, 'quadrant': 'Q2', 'action': 'update'}
    },
]

print("🧪 开始测试字段验证逻辑...\n")

passed = 0
failed = 0

for i, test_case in enumerate(test_cases, 1):
    input_data = test_case['input']
    expected = test_case['expected']
    
    result, error = validate_task_data(input_data)
    
    if error:
        print(f"❌ 测试 {i} 失败: {error}")
        print(f"   输入: {input_data}")
        failed += 1
    elif result == expected:
        print(f"✅ 测试 {i} 通过")
        passed += 1
    else:
        print(f"❌ 测试 {i} 失败")
        print(f"   输入: {input_data}")
        print(f"   期望: {expected}")
        print(f"   实际: {result}")
        failed += 1

print(f"\n📊 测试结果: {passed} 通过, {failed} 失败")

if failed == 0:
    print("🎉 所有测试通过！字段验证逻辑工作正常。")
else:
    print("⚠️ 有测试失败，需要检查代码。")
