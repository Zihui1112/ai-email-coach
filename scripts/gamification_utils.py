"""
游戏化系统辅助函数
包含等级、经验值、金币计算等功能
"""
import requests
from datetime import datetime, date

# 象限权重配置
QUADRANT_WEIGHTS = {
    1: 2.0,  # Q1: 重要且紧急
    2: 1.5,  # Q2: 重要非紧急
    3: 1.0,  # Q3: 紧急非重要
    4: 0.5   # Q4: 非紧急非重要
}

# 等级升级所需经验值
LEVEL_EXP_REQUIRED = {
    1: 100, 2: 200, 3: 300, 4: 400, 5: 500,
    6: 600, 7: 700, 8: 800, 9: 900, 10: 1000,
    11: 1100, 12: 1200, 13: 1300, 14: 1400, 15: 1500,
    16: 1600, 17: 1700, 18: 1800, 19: 1900, 20: 2000
}

# AI性格配置
AI_PERSONALITIES = {
    'friendly': {
        'name': '🌟 友好型',
        'description': '温暖鼓励，适合新手',
        'min_level': 1
    },
    'professional': {
        'name': '💼 专业型',
        'description': '理性分析，给出建议',
        'min_level': 4
    },
    'strict': {
        'name': '🔥 严格型',
        'description': '督导为主，要求高',
        'min_level': 8
    },
    'toxic': {
        'name': '💀 毒舌型',
        'description': '犀利吐槽，激励效果强',
        'min_level': 13
    }
}

def calculate_exp_gain(progress_change, quadrant):
    """
    计算经验值获得
    
    Args:
        progress_change: 进度变化百分比（0-100）
        quadrant: 象限（1-4）
    
    Returns:
        int: 获得的经验值
    """
    if progress_change <= 0:
        return 0
    
    weight = QUADRANT_WEIGHTS.get(quadrant, 1.0)
    exp = int(progress_change * weight)
    
    return max(exp, 1)  # 至少获得1点经验

def calculate_coins_gain(completion_rate):
    """
    计算金币获得
    
    Args:
        completion_rate: 完成度（0-100）
    
    Returns:
        int: 获得的金币
    """
    if completion_rate >= 100:
        return 100
    elif completion_rate >= 80:
        return 50
    elif completion_rate >= 60:
        return 20
    else:
        return 5  # 保底

def get_user_gamification_data(supabase_url, headers, user_email):
    """获取用户游戏化数据"""
    try:
        query_url = f"{supabase_url}/rest/v1/user_gamification?user_email=eq.{user_email}&select=*"
        response = requests.get(query_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                return data[0]
        
        # 如果没有记录，创建一个
        create_url = f"{supabase_url}/rest/v1/user_gamification"
        create_data = {
            "user_email": user_email,
            "level": 1,
            "current_exp": 0,
            "total_exp": 0,
            "coins": 200,
            "ai_personality": "friendly",
            "consecutive_q1_days": 0
        }
        
        response = requests.post(create_url, headers=headers, json=create_data, timeout=30)
        
        if response.status_code in [200, 201]:
            return create_data
        
        return None
    except Exception as e:
        print(f"获取用户游戏化数据失败: {e}")
        return None

def update_user_exp_and_coins(supabase_url, headers, user_email, exp_gain, coins_gain, reason=""):
    """
    更新用户经验值和金币
    
    Returns:
        dict: 包含是否升级、新等级等信息
    """
    try:
        # 获取当前数据
        user_data = get_user_gamification_data(supabase_url, headers, user_email)
        
        if not user_data:
            return None
        
        current_level = user_data.get('level', 1)
        current_exp = user_data.get('current_exp', 0)
        total_exp = user_data.get('total_exp', 0)
        coins = user_data.get('coins', 0)
        
        # 计算新的经验值和金币
        new_current_exp = current_exp + exp_gain
        new_total_exp = total_exp + exp_gain
        new_coins = coins + coins_gain
        
        # 检查是否升级
        level_up = False
        new_level = current_level
        
        while new_level < 20:
            exp_required = LEVEL_EXP_REQUIRED.get(new_level, 9999)
            
            if new_current_exp >= exp_required:
                new_current_exp -= exp_required
                new_level += 1
                level_up = True
            else:
                break
        
        # 更新数据库
        update_url = f"{supabase_url}/rest/v1/user_gamification?user_email=eq.{user_email}"
        update_data = {
            "level": new_level,
            "current_exp": new_current_exp,
            "total_exp": new_total_exp,
            "coins": new_coins,
            "updated_at": datetime.now().isoformat()
        }
        
        response = requests.patch(update_url, headers=headers, json=update_data, timeout=30)
        
        if response.status_code in [200, 204]:
            # 记录经验值历史
            log_exp_history(supabase_url, headers, user_email, exp_gain, coins_gain, reason)
            
            return {
                'success': True,
                'level_up': level_up,
                'old_level': current_level,
                'new_level': new_level,
                'exp_gain': exp_gain,
                'coins_gain': coins_gain,
                'current_exp': new_current_exp,
                'total_exp': new_total_exp,
                'coins': new_coins
            }
        
        return None
    except Exception as e:
        print(f"更新用户经验值和金币失败: {e}")
        return None

def log_exp_history(supabase_url, headers, user_email, exp_gained, coins_gained, reason):
    """记录经验值历史"""
    try:
        create_url = f"{supabase_url}/rest/v1/exp_history"
        create_data = {
            "user_email": user_email,
            "exp_gained": exp_gained,
            "coins_gained": coins_gained,
            "reason": reason
        }
        
        requests.post(create_url, headers=headers, json=create_data, timeout=30)
    except Exception as e:
        print(f"记录经验值历史失败: {e}")

def get_available_personalities(level):
    """获取当前等级可用的性格列表"""
    available = []
    
    for key, config in AI_PERSONALITIES.items():
        if level >= config['min_level']:
            available.append({
                'code': key,
                'name': config['name'],
                'description': config['description']
            })
    
    return available

def format_quadrant_guide():
    """生成四象限说明"""
    return """━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📋 四象限说明：
  Q1 🔴 重要且紧急   - 必须立即处理（EXP x2.0）
  Q2 🟡 重要非紧急   - 计划安排处理（EXP x1.5）
  Q3 🔵 紧急非重要   - 可委托他人（EXP x1.0）
  Q4 ⚪ 非紧急非重要 - 有空再处理（EXP x0.5）
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""

def format_user_status(user_data):
    """格式化用户状态显示"""
    level = user_data.get('level', 1)
    current_exp = user_data.get('current_exp', 0)
    coins = user_data.get('coins', 0)
    consecutive_q1_days = user_data.get('consecutive_q1_days', 0)
    personality = user_data.get('ai_personality', 'friendly')
    
    # 获取下一级所需经验
    exp_required = LEVEL_EXP_REQUIRED.get(level, 2000)
    
    # 生成经验值进度条
    exp_percentage = int((current_exp / exp_required) * 100) if exp_required > 0 else 0
    exp_filled = int(exp_percentage / 10)
    exp_empty = 10 - exp_filled
    exp_bar = "■" * exp_filled + "□" * exp_empty
    
    # 获取性格名称
    personality_name = AI_PERSONALITIES.get(personality, {}).get('name', '🌟 友好型')
    
    status = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 你的状态：
  ⭐ 等级：LV{level} (EXP: {current_exp}/{exp_required})
     [{exp_bar}] {exp_percentage}%
  💰 金币：{coins} Coin
  🔥 连击：{consecutive_q1_days}天
  🎭 性格：{personality_name}
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"""
    
    return status

def format_level_up_message(old_level, new_level):
    """格式化升级消息"""
    message = f"""
╔═══════════════════════════════════╗
║  ⬆️ 等级提升：LV{old_level} → LV{new_level}           ║
╠═══════════════════════════════════╣
║                                   ║
║  🎊 恭喜升级！                    ║
"""
    
    # 检查解锁的功能
    if new_level == 4:
        message += "║     🎁 解锁：每日成就盲盒卡片    ║\n"
        message += "║     🎭 解锁：专业型性格          ║\n"
    elif new_level == 8:
        message += "║     📊 解锁：周报多维数据透视    ║\n"
        message += "║     🎭 解锁：严格型性格          ║\n"
    elif new_level == 13:
        message += "║     🛒 解锁：高级商店            ║\n"
        message += "║     🎭 解锁：毒舌型性格          ║\n"
    elif new_level == 16:
        message += "║     🏆 解锁：高级道具            ║\n"
    elif new_level == 20:
        message += "║     👑 解锁：特殊道具            ║\n"
        message += "║     🎉 恭喜达到最高等级！        ║\n"
    
    message += "║                                   ║\n"
    message += "╚═══════════════════════════════════╝"
    
    return message

def check_and_update_q1_streak(supabase_url, headers, user_email, has_q1_task, q1_completed):
    """检查并更新Q1连击"""
    try:
        user_data = get_user_gamification_data(supabase_url, headers, user_email)
        
        if not user_data:
            return 0
        
        consecutive_days = user_data.get('consecutive_q1_days', 0)
        last_complete_date = user_data.get('last_q1_complete_date')
        
        today = date.today()
        
        # 如果今天有Q1任务且全部完成
        if has_q1_task and q1_completed:
            # 检查是否是连续的
            if last_complete_date:
                last_date = datetime.strptime(last_complete_date, '%Y-%m-%d').date()
                days_diff = (today - last_date).days
                
                if days_diff == 1:
                    # 连续
                    consecutive_days += 1
                elif days_diff == 0:
                    # 今天已经记录过了
                    pass
                else:
                    # 中断了
                    consecutive_days = 1
            else:
                consecutive_days = 1
            
            # 更新数据库
            update_url = f"{supabase_url}/rest/v1/user_gamification?user_email=eq.{user_email}"
            update_data = {
                "consecutive_q1_days": consecutive_days,
                "last_q1_complete_date": today.isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            requests.patch(update_url, headers=headers, json=update_data, timeout=30)
            
            return consecutive_days
        
        return consecutive_days
    except Exception as e:
        print(f"更新Q1连击失败: {e}")
        return 0
