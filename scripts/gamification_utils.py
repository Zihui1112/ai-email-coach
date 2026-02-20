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


# ==================== 惩罚机制相关函数 ====================

def calculate_no_reply_punishment(consecutive_no_reply_days, user_level):
    """
    计算未回复惩罚
    
    Args:
        consecutive_no_reply_days: 连续未回复天数
        user_level: 用户等级
    
    Returns:
        dict: 包含扣除的金币和经验值
    """
    # 新手保护（LV1-3惩罚减半）
    is_newbie = user_level <= 3
    multiplier = 0.5 if is_newbie else 1.0
    
    if consecutive_no_reply_days < 2:
        return {'coins': 0, 'exp': 0, 'clear_streak': False}
    elif consecutive_no_reply_days == 2:
        return {
            'coins': int(20 * multiplier),
            'exp': int(30 * multiplier),
            'clear_streak': False
        }
    elif consecutive_no_reply_days == 3:
        return {
            'coins': int(40 * multiplier),
            'exp': int(60 * multiplier),
            'clear_streak': False
        }
    elif consecutive_no_reply_days == 4:
        return {
            'coins': int(60 * multiplier),
            'exp': int(100 * multiplier),
            'clear_streak': True
        }
    else:  # 5天及以上
        return {
            'coins': int(80 * multiplier),
            'exp': int(150 * multiplier),
            'clear_streak': True
        }

def calculate_task_delay_punishment(task_quadrant, days_delayed, user_level):
    """
    计算任务拖延惩罚
    
    Args:
        task_quadrant: 任务象限（1-4）
        days_delayed: 拖延天数
        user_level: 用户等级
    
    Returns:
        int: 扣除的金币
    """
    # 新手保护
    is_newbie = user_level <= 3
    multiplier = 0.5 if is_newbie else 1.0
    
    if task_quadrant == 1 and days_delayed > 3:
        # Q1任务超过3天
        return int(15 * multiplier * (days_delayed - 3))
    elif task_quadrant == 2 and days_delayed > 7:
        # Q2任务超过7天
        return int(10 * multiplier * (days_delayed - 7))
    else:
        # Q3/Q4不惩罚
        return 0

def calculate_progress_decline_punishment(progress_decline, user_level):
    """
    计算进度倒退惩罚
    
    Args:
        progress_decline: 进度下降百分比（正数）
        user_level: 用户等级
    
    Returns:
        dict: 包含扣除的金币和经验值
    """
    # 新手保护
    is_newbie = user_level <= 3
    multiplier = 0.5 if is_newbie else 1.0
    
    if progress_decline < 10:
        return {'coins': 0, 'exp': 0}
    elif progress_decline < 20:
        return {
            'coins': int(10 * multiplier),
            'exp': 0
        }
    elif progress_decline < 50:
        return {
            'coins': int(20 * multiplier),
            'exp': int(30 * multiplier)
        }
    else:  # 50%以上
        return {
            'coins': int(40 * multiplier),
            'exp': int(80 * multiplier)
        }

def apply_punishment(supabase_url, headers, user_email, coins_deduct, exp_deduct, punishment_type, reason=""):
    """
    执行惩罚（扣除金币和经验值）
    
    Returns:
        dict: 包含是否降级、新等级等信息
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
        
        # 扣除金币（最低0）
        new_coins = max(0, coins - coins_deduct)
        
        # 扣除经验值
        new_current_exp = current_exp - exp_deduct
        new_total_exp = total_exp  # 总经验值不减少
        
        # 检查是否降级
        downgraded = False
        new_level = current_level
        
        while new_current_exp < 0 and new_level > 1:
            # 降级
            new_level -= 1
            downgraded = True
            
            # 回到上一级的最大经验值
            prev_level_exp = LEVEL_EXP_REQUIRED.get(new_level, 100)
            new_current_exp += prev_level_exp
        
        # 确保不会降到LV1以下
        if new_level == 1:
            new_current_exp = max(0, new_current_exp)
        
        # 更新数据库
        update_url = f"{supabase_url}/rest/v1/user_gamification?user_email=eq.{user_email}"
        update_data = {
            "level": new_level,
            "current_exp": new_current_exp,
            "coins": new_coins,
            "last_punishment_date": date.today().isoformat(),
            "total_punishments": user_data.get('total_punishments', 0) + 1,
            "updated_at": datetime.now().isoformat()
        }
        
        # 如果清零连击，也更新
        if punishment_type == 'no_reply':
            update_data["consecutive_q1_days"] = 0
        
        response = requests.patch(update_url, headers=headers, json=update_data, timeout=30)
        
        if response.status_code in [200, 204]:
            # 记录惩罚历史
            log_punishment_history(
                supabase_url, headers, user_email,
                punishment_type, coins_deduct, exp_deduct,
                current_level, new_level, reason,
                current_level <= 3
            )
            
            return {
                'success': True,
                'downgraded': downgraded,
                'old_level': current_level,
                'new_level': new_level,
                'coins_deducted': coins_deduct,
                'exp_deducted': exp_deduct,
                'new_coins': new_coins,
                'new_current_exp': new_current_exp
            }
        
        return None
    except Exception as e:
        print(f"执行惩罚失败: {e}")
        return None

def log_punishment_history(supabase_url, headers, user_email, punishment_type, 
                          coins_deducted, exp_deducted, level_before, level_after, 
                          reason, is_newbie_protected):
    """记录惩罚历史"""
    try:
        create_url = f"{supabase_url}/rest/v1/punishment_history"
        create_data = {
            "user_email": user_email,
            "punishment_type": punishment_type,
            "coins_deducted": coins_deducted,
            "exp_deducted": exp_deducted,
            "level_before": level_before,
            "level_after": level_after,
            "reason": reason,
            "is_newbie_protected": is_newbie_protected
        }
        
        requests.post(create_url, headers=headers, json=create_data, timeout=30)
    except Exception as e:
        print(f"记录惩罚历史失败: {e}")

def check_and_apply_no_reply_punishment(supabase_url, headers, user_email):
    """
    检查并执行未回复惩罚
    
    Returns:
        dict: 惩罚结果，如果无需惩罚则返回None
    """
    try:
        # 获取用户回复追踪数据
        query_url = f"{supabase_url}/rest/v1/user_reply_tracking?user_email=eq.{user_email}&select=*"
        response = requests.get(query_url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            return None
        
        data = response.json()
        if not data:
            return None
        
        consecutive_no_reply_days = data[0].get('consecutive_no_reply_days', 0)
        
        # 获取用户等级
        user_data = get_user_gamification_data(supabase_url, headers, user_email)
        if not user_data:
            return None
        
        user_level = user_data.get('level', 1)
        
        # 计算惩罚
        punishment = calculate_no_reply_punishment(consecutive_no_reply_days, user_level)
        
        if punishment['coins'] == 0 and punishment['exp'] == 0:
            return None
        
        # 执行惩罚
        result = apply_punishment(
            supabase_url, headers, user_email,
            punishment['coins'], punishment['exp'],
            'no_reply',
            f"连续{consecutive_no_reply_days}天未回复"
        )
        
        if result:
            result['consecutive_no_reply_days'] = consecutive_no_reply_days
            result['clear_streak'] = punishment['clear_streak']
        
        return result
        
    except Exception as e:
        print(f"检查未回复惩罚失败: {e}")
        return None

def format_punishment_message(punishment_result):
    """格式化惩罚消息"""
    if not punishment_result:
        return ""
    
    consecutive_days = punishment_result.get('consecutive_no_reply_days', 0)
    coins_deducted = punishment_result.get('coins_deducted', 0)
    exp_deducted = punishment_result.get('exp_deducted', 0)
    downgraded = punishment_result.get('downgraded', False)
    old_level = punishment_result.get('old_level', 1)
    new_level = punishment_result.get('new_level', 1)
    
    message = f"""
╔═══════════════════════════════════╗
║  ⚠️ 惩罚通知                      ║
╠═══════════════════════════════════╣
║                                   ║
║  连续{consecutive_days}天未回复                ║
║  💰 扣除金币：-{coins_deducted} Coin            ║
║  💫 扣除经验：-{exp_deducted} EXP              ║
"""
    
    if downgraded:
        message += f"║  📉 等级下降：LV{old_level} → LV{new_level}      ║\n"
    
    message += """║                                   ║
║  💡 提示：定期回复可避免惩罚      ║
║                                   ║
╚═══════════════════════════════════╝"""
    
    return message

def update_consecutive_reply_days(supabase_url, headers, user_email):
    """
    更新连续回复天数
    
    Returns:
        int: 当前连续回复天数
    """
    try:
        user_data = get_user_gamification_data(supabase_url, headers, user_email)
        
        if not user_data:
            return 0
        
        consecutive_days = user_data.get('consecutive_reply_days', 0)
        last_reply_date = user_data.get('last_reply_date')
        total_reply_days = user_data.get('total_reply_days', 0)
        
        today = date.today()
        
        # 检查是否是连续的
        if last_reply_date:
            last_date = datetime.strptime(last_reply_date, '%Y-%m-%d').date()
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
            "consecutive_reply_days": consecutive_days,
            "last_reply_date": today.isoformat(),
            "total_reply_days": total_reply_days + 1,
            "updated_at": datetime.now().isoformat()
        }
        
        requests.patch(update_url, headers=headers, json=update_data, timeout=30)
        
        return consecutive_days
    except Exception as e:
        print(f"更新连续回复天数失败: {e}")
        return 0

def check_persistence_milestone(supabase_url, headers, user_email, consecutive_days):
    """
    检查是否达到坚持里程碑
    
    Returns:
        dict: 奖励信息，如果未达到里程碑则返回None
    """
    # 里程碑配置（调整后的奖励）
    milestones = {
        3: {'coins': 20, 'exp': 0, 'name': '🎉 初次坚持'},
        7: {'coins': 50, 'exp': 30, 'name': '🏆 坚持一周'},
        14: {'coins': 100, 'exp': 60, 'name': '🏆 坚持两周'},
        30: {'coins': 300, 'exp': 150, 'name': '🏆 坚持一月'},
        60: {'coins': 600, 'exp': 300, 'name': '🏆 坚持两月'},
        90: {'coins': 1000, 'exp': 500, 'name': '🏆 坚持三月'}
    }
    
    if consecutive_days not in milestones:
        return None
    
    try:
        # 检查是否已经领取过这个里程碑奖励
        query_url = f"{supabase_url}/rest/v1/persistence_rewards?user_email=eq.{user_email}&milestone_days=eq.{consecutive_days}&select=*"
        response = requests.get(query_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                # 已经领取过了
                return None
        
        milestone = milestones[consecutive_days]
        
        # 发放奖励
        reward_result = update_user_exp_and_coins(
            supabase_url, headers, user_email,
            milestone['exp'], milestone['coins'],
            f"坚持{consecutive_days}天奖励"
        )
        
        if reward_result:
            # 记录奖励历史
            create_url = f"{supabase_url}/rest/v1/persistence_rewards"
            create_data = {
                "user_email": user_email,
                "milestone_days": consecutive_days,
                "coins_rewarded": milestone['coins'],
                "exp_rewarded": milestone['exp'],
                "achievement_name": milestone['name']
            }
            
            requests.post(create_url, headers=headers, json=create_data, timeout=30)
            
            return {
                'milestone_days': consecutive_days,
                'coins': milestone['coins'],
                'exp': milestone['exp'],
                'name': milestone['name']
            }
        
        return None
    except Exception as e:
        print(f"检查坚持里程碑失败: {e}")
        return None

def format_persistence_reward_message(reward):
    """格式化坚持奖励消息"""
    if not reward:
        return ""
    
    days = reward.get('milestone_days', 0)
    coins = reward.get('coins', 0)
    exp = reward.get('exp', 0)
    name = reward.get('name', '')
    
    message = f"""
╔═══════════════════════════════════╗
║  {name}                    ║
╠═══════════════════════════════════╣
║                                   ║
║  🎊 恭喜坚持{days}天！               ║
║  💰 奖励金币：+{coins} Coin            ║
"""
    
    if exp > 0:
        message += f"║  💫 奖励经验：+{exp} EXP              ║\n"
    
    message += """║                                   ║
║  💪 继续保持，更多奖励等着你！    ║
║                                   ║
╚═══════════════════════════════════╝"""
    
    return message


# ==================== AI性格系统相关函数 ====================

def parse_personality_switch_command(user_message):
    """
    解析性格切换命令
    
    Args:
        user_message: 用户消息内容
    
    Returns:
        str: 性格代码（friendly/professional/strict/toxic），如果没有切换命令则返回None
    """
    # 匹配格式：切换性格：XXX型
    import re
    
    patterns = [
        r'切换性格[：:]\s*(友好|专业|严格|毒舌)型?',
        r'切换[：:]\s*(友好|专业|严格|毒舌)型?',
        r'性格[：:]\s*(友好|专业|严格|毒舌)型?'
    ]
    
    personality_map = {
        '友好': 'friendly',
        '专业': 'professional',
        '严格': 'strict',
        '毒舌': 'toxic'
    }
    
    for pattern in patterns:
        match = re.search(pattern, user_message)
        if match:
            personality_cn = match.group(1)
            return personality_map.get(personality_cn)
    
    return None

def switch_ai_personality(supabase_url, headers, user_email, new_personality):
    """
    切换AI性格
    
    Args:
        new_personality: 新性格代码（friendly/professional/strict/toxic）
    
    Returns:
        dict: 切换结果
    """
    try:
        # 获取用户数据
        user_data = get_user_gamification_data(supabase_url, headers, user_email)
        
        if not user_data:
            return {'success': False, 'reason': '用户数据不存在'}
        
        current_level = user_data.get('level', 1)
        current_personality = user_data.get('ai_personality', 'friendly')
        
        # 检查性格是否有效
        if new_personality not in AI_PERSONALITIES:
            return {'success': False, 'reason': '无效的性格类型'}
        
        # 检查等级是否足够
        required_level = AI_PERSONALITIES[new_personality]['min_level']
        if current_level < required_level:
            return {
                'success': False,
                'reason': f'等级不足',
                'required_level': required_level,
                'current_level': current_level,
                'personality_name': AI_PERSONALITIES[new_personality]['name']
            }
        
        # 检查是否已经是这个性格
        if current_personality == new_personality:
            return {
                'success': False,
                'reason': '已经是这个性格了',
                'personality_name': AI_PERSONALITIES[new_personality]['name']
            }
        
        # 更新性格
        update_url = f"{supabase_url}/rest/v1/user_gamification?user_email=eq.{user_email}"
        update_data = {
            "ai_personality": new_personality,
            "updated_at": datetime.now().isoformat()
        }
        
        response = requests.patch(update_url, headers=headers, json=update_data, timeout=30)
        
        if response.status_code in [200, 204]:
            return {
                'success': True,
                'old_personality': current_personality,
                'new_personality': new_personality,
                'old_name': AI_PERSONALITIES[current_personality]['name'],
                'new_name': AI_PERSONALITIES[new_personality]['name']
            }
        
        return {'success': False, 'reason': '数据库更新失败'}
    except Exception as e:
        print(f"切换AI性格失败: {e}")
        return {'success': False, 'reason': str(e)}

def format_personality_switch_message(switch_result):
    """格式化性格切换消息"""
    if not switch_result.get('success'):
        reason = switch_result.get('reason', '未知错误')
        
        if reason == '等级不足':
            required_level = switch_result.get('required_level', 1)
            current_level = switch_result.get('current_level', 1)
            personality_name = switch_result.get('personality_name', '')
            
            return f"""
⚠️ 性格切换失败

{personality_name} 需要 LV{required_level} 才能解锁
你当前等级：LV{current_level}

💡 继续升级即可解锁更多性格！"""
        
        elif reason == '已经是这个性格了':
            personality_name = switch_result.get('personality_name', '')
            return f"\n💡 你已经是 {personality_name} 了，无需切换。"
        
        else:
            return f"\n⚠️ 性格切换失败：{reason}"
    
    old_name = switch_result.get('old_name', '')
    new_name = switch_result.get('new_name', '')
    
    return f"""
╔═══════════════════════════════════╗
║  🎭 性格切换成功                  ║
╠═══════════════════════════════════╣
║                                   ║
║  {old_name} → {new_name}          ║
║                                   ║
║  从现在开始，我会用新的风格      ║
║  与你交流！                       ║
║                                   ║
╚═══════════════════════════════════╝"""

def get_personality_prompt(personality_code):
    """
    获取不同性格的AI提示词
    
    Args:
        personality_code: 性格代码
    
    Returns:
        str: 性格提示词
    """
    prompts = {
        'friendly': """你是一个温暖、鼓励的任务管理助手。
特点：
- 语气温暖友好，像朋友一样
- 多用鼓励和赞美的话
- 即使进度慢也要给予理解和支持
- 用积极正面的语言
- 适当使用温暖的表达，但不要过度""",
        
        'professional': """你是一个专业、理性的任务管理顾问。
特点：
- 语气专业客观，像职业顾问
- 基于数据给出分析和建议
- 指出问题但不批评，提供解决方案
- 用理性、逻辑的语言
- 保持专业距离感""",
        
        'strict': """你是一个严格、督导的任务管理教练。
特点：
- 语气严格认真，像严师
- 对拖延和低效率直接指出
- 设定高标准，要求持续进步
- 用坚定、有力的语言
- 适当施加压力，但不要过分""",
        
        'toxic': """你是一个犀利、毒舌的任务管理监督者。
特点：
- 语气犀利直接，像毒舌朋友
- 对拖延和借口进行吐槽
- 用反讽和幽默激励
- 语言犀利但不恶意
- 目标是用"激将法"激发动力"""
    }
    
    return prompts.get(personality_code, prompts['friendly'])

def generate_personality_feedback(tasks_data, progress_changes, personality_code, deepseek_api_key):
    """
    根据性格生成个性化反馈
    
    Args:
        tasks_data: 任务数据
        progress_changes: 进度变化
        personality_code: 性格代码
        deepseek_api_key: DeepSeek API密钥
    
    Returns:
        str: 个性化反馈
    """
    try:
        # 构建任务摘要
        task_summary = []
        for task in tasks_data:
            task_summary.append({
                'name': task.get('task_name', ''),
                'progress': task.get('progress', 0),
                'action': task.get('action', 'update')
            })
        
        # 获取性格提示词
        personality_prompt = get_personality_prompt(personality_code)
        
        prompt = f"""{personality_prompt}

请根据用户的任务更新情况，生成一段符合你性格的反馈。

任务更新情况：
{json.dumps(task_summary, ensure_ascii=False, indent=2)}

进度变化：
{json.dumps(progress_changes, ensure_ascii=False, indent=2) if progress_changes else "无历史数据"}

要求：
1. 严格按照你的性格特点来表达
2. 根据进度变化给出具体的反馈
3. 根据任务数量给出建议
4. 控制在3-5句话以内
5. 不要使用emoji，使用文字表达

只返回反馈内容，不要其他说明。"""
        
        headers = {
            "Authorization": f"Bearer {deepseek_api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.8
        }
        
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            feedback = result['choices'][0]['message']['content'].strip()
            return feedback
        else:
            # 降级到默认反馈
            return "感谢你的更新！继续保持，你做得很好。"
    
    except Exception as e:
        print(f"生成性格化反馈失败: {e}")
        return "感谢你的更新！继续保持，你做得很好。"


# ==================== 商店系统相关函数 ====================

def parse_purchase_command(user_message):
    """
    解析购买命令
    
    Args:
        user_message: 用户消息内容
    
    Returns:
        str: 道具代码，如果没有购买命令则返回None
    """
    import re
    
    # 匹配格式：购买：道具名
    patterns = [
        r'购买[：:]\s*(.+)',
        r'买[：:]\s*(.+)',
        r'兑换[：:]\s*(.+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, user_message)
        if match:
            item_name = match.group(1).strip()
            return item_name
    
    return None

def get_shop_item_by_name(supabase_url, headers, item_name):
    """
    根据道具名称获取道具信息
    
    Returns:
        dict: 道具信息，如果不存在则返回None
    """
    try:
        # 先尝试精确匹配道具名称
        query_url = f"{supabase_url}/rest/v1/shop_items?item_name=eq.{item_name}&select=*"
        response = requests.get(query_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data:
                return data[0]
        
        # 如果精确匹配失败，尝试模糊匹配（去掉emoji）
        query_url = f"{supabase_url}/rest/v1/shop_items?select=*"
        response = requests.get(query_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            all_items = response.json()
            
            # 去掉emoji后匹配
            for item in all_items:
                clean_name = re.sub(r'[^\w\s]', '', item['item_name'])
                clean_input = re.sub(r'[^\w\s]', '', item_name)
                
                if clean_input in clean_name or clean_name in clean_input:
                    return item
        
        return None
    except Exception as e:
        print(f"获取道具信息失败: {e}")
        return None

def check_purchase_eligibility(user_data, item_data):
    """
    检查是否有资格购买道具
    
    Returns:
        dict: 检查结果
    """
    user_level = user_data.get('level', 1)
    user_coins = user_data.get('coins', 0)
    
    required_level = item_data.get('required_level', 1)
    price = item_data.get('price', 0)
    
    # 检查等级
    if user_level < required_level:
        return {
            'eligible': False,
            'reason': 'level_insufficient',
            'required_level': required_level,
            'current_level': user_level
        }
    
    # 检查金币
    if user_coins < price:
        return {
            'eligible': False,
            'reason': 'coins_insufficient',
            'required_coins': price,
            'current_coins': user_coins
        }
    
    return {'eligible': True}

def check_usage_limit(supabase_url, headers, user_email, item_code, item_data):
    """
    检查道具使用限制
    
    Returns:
        dict: 检查结果
    """
    try:
        usage_limit_type = item_data.get('usage_limit_type', 'unlimited')
        usage_limit_count = item_data.get('usage_limit_count', 0)
        
        if usage_limit_type == 'unlimited':
            return {'within_limit': True}
        
        # 查询用户库存
        query_url = f"{supabase_url}/rest/v1/user_inventory?user_email=eq.{user_email}&item_code=eq.{item_code}&select=*"
        response = requests.get(query_url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            return {'within_limit': True}  # 查询失败，允许购买
        
        data = response.json()
        if not data:
            return {'within_limit': True}  # 没有记录，允许购买
        
        inventory = data[0]
        
        # 检查限制
        if usage_limit_type == 'daily':
            usage_count = inventory.get('usage_count_daily', 0)
        elif usage_limit_type == 'weekly':
            usage_count = inventory.get('usage_count_weekly', 0)
        elif usage_limit_type == 'monthly':
            usage_count = inventory.get('usage_count_monthly', 0)
        else:
            return {'within_limit': True}
        
        if usage_count >= usage_limit_count:
            return {
                'within_limit': False,
                'limit_type': usage_limit_type,
                'limit_count': usage_limit_count,
                'current_count': usage_count
            }
        
        return {'within_limit': True}
    except Exception as e:
        print(f"检查使用限制失败: {e}")
        return {'within_limit': True}  # 出错时允许购买

def purchase_item(supabase_url, headers, user_email, item_code, item_data):
    """
    购买道具
    
    Returns:
        dict: 购买结果
    """
    try:
        price = item_data.get('price', 0)
        item_name = item_data.get('item_name', '')
        
        # 扣除金币
        user_data = get_user_gamification_data(supabase_url, headers, user_email)
        if not user_data:
            return {'success': False, 'reason': '用户数据不存在'}
        
        current_coins = user_data.get('coins', 0)
        new_coins = current_coins - price
        
        # 更新金币
        update_url = f"{supabase_url}/rest/v1/user_gamification?user_email=eq.{user_email}"
        update_data = {
            "coins": new_coins,
            "updated_at": datetime.now().isoformat()
        }
        
        response = requests.patch(update_url, headers=headers, json=update_data, timeout=30)
        
        if response.status_code not in [200, 204]:
            return {'success': False, 'reason': '扣除金币失败'}
        
        # 添加到库存
        add_to_inventory(supabase_url, headers, user_email, item_code)
        
        return {
            'success': True,
            'item_name': item_name,
            'price': price,
            'remaining_coins': new_coins
        }
    except Exception as e:
        print(f"购买道具失败: {e}")
        return {'success': False, 'reason': str(e)}

def add_to_inventory(supabase_url, headers, user_email, item_code):
    """添加道具到库存"""
    try:
        # 查询是否已存在
        query_url = f"{supabase_url}/rest/v1/user_inventory?user_email=eq.{user_email}&item_code=eq.{item_code}&select=*"
        response = requests.get(query_url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            
            if data:
                # 已存在，增加数量
                inventory_id = data[0]['id']
                current_quantity = data[0].get('quantity', 0)
                
                update_url = f"{supabase_url}/rest/v1/user_inventory?id=eq.{inventory_id}"
                update_data = {
                    "quantity": current_quantity + 1,
                    "updated_at": datetime.now().isoformat()
                }
                
                requests.patch(update_url, headers=headers, json=update_data, timeout=30)
            else:
                # 不存在，创建新记录
                create_url = f"{supabase_url}/rest/v1/user_inventory"
                create_data = {
                    "user_email": user_email,
                    "item_code": item_code,
                    "quantity": 1
                }
                
                requests.post(create_url, headers=headers, json=create_data, timeout=30)
        
        print(f"✅ 道具已添加到库存: {item_code}")
    except Exception as e:
        print(f"添加到库存失败: {e}")

def format_purchase_result_message(purchase_result):
    """格式化购买结果消息"""
    if not purchase_result.get('success'):
        reason = purchase_result.get('reason', '未知错误')
        return f"\n⚠️ 购买失败：{reason}"
    
    item_name = purchase_result.get('item_name', '')
    price = purchase_result.get('price', 0)
    remaining_coins = purchase_result.get('remaining_coins', 0)
    
    return f"""
╔═══════════════════════════════════╗
║  🛒 购买成功                      ║
╠═══════════════════════════════════╣
║                                   ║
║  道具：{item_name}                ║
║  花费：-{price} Coin              ║
║  余额：{remaining_coins} Coin     ║
║                                   ║
║  💡 道具已添加到你的背包          ║
║                                   ║
╚═══════════════════════════════════╝"""

def format_purchase_error_message(error_type, error_data):
    """格式化购买错误消息"""
    if error_type == 'item_not_found':
        return "\n⚠️ 购买失败：道具不存在\n\n💡 请检查道具名称是否正确"
    
    elif error_type == 'level_insufficient':
        required_level = error_data.get('required_level', 1)
        current_level = error_data.get('current_level', 1)
        return f"""
⚠️ 购买失败：等级不足

需要等级：LV{required_level}
当前等级：LV{current_level}

💡 继续升级即可解锁！"""
    
    elif error_type == 'coins_insufficient':
        required_coins = error_data.get('required_coins', 0)
        current_coins = error_data.get('current_coins', 0)
        shortage = required_coins - current_coins
        return f"""
⚠️ 购买失败：金币不足

需要金币：{required_coins} Coin
当前金币：{current_coins} Coin
还差：{shortage} Coin

💡 完成更多任务获得金币！"""
    
    elif error_type == 'usage_limit_exceeded':
        limit_type = error_data.get('limit_type', 'daily')
        limit_count = error_data.get('limit_count', 0)
        
        limit_type_cn = {
            'daily': '每日',
            'weekly': '每周',
            'monthly': '每月'
        }
        
        return f"""
⚠️ 购买失败：已达到购买限制

{limit_type_cn.get(limit_type, '')}限购：{limit_count}次

💡 请等待限制重置后再购买"""
    
    else:
        return f"\n⚠️ 购买失败：{error_type}"

def get_user_inventory_summary(supabase_url, headers, user_email):
    """
    获取用户背包摘要
    
    Returns:
        str: 背包摘要文本
    """
    try:
        query_url = f"{supabase_url}/rest/v1/user_inventory?user_email=eq.{user_email}&select=*"
        response = requests.get(query_url, headers=headers, timeout=30)
        
        if response.status_code != 200:
            return ""
        
        inventory = response.json()
        
        if not inventory:
            return "\n💼 背包：空"
        
        # 获取道具详情
        summary = "\n💼 背包：\n"
        
        for item in inventory:
            item_code = item.get('item_code', '')
            quantity = item.get('quantity', 0)
            
            if quantity > 0:
                # 获取道具名称
                item_query_url = f"{supabase_url}/rest/v1/shop_items?item_code=eq.{item_code}&select=item_name"
                item_response = requests.get(item_query_url, headers=headers, timeout=30)
                
                if item_response.status_code == 200:
                    item_data = item_response.json()
                    if item_data:
                        item_name = item_data[0].get('item_name', item_code)
                        summary += f"   {item_name} x{quantity}\n"
        
        return summary
    except Exception as e:
        print(f"获取背包摘要失败: {e}")
        return ""


# ==================== 解锁进度提示相关函数 ====================

def get_next_unlock_info(user_level):
    """
    获取下一个解锁信息
    
    Args:
        user_level: 当前等级
    
    Returns:
        dict: 下一个解锁的信息
    """
    unlock_milestones = {
        4: {
            'level': 4,
            'features': ['每日成就盲盒', '专业型性格'],
            'icon': '🎁',
            'description': '每日成就盲盒 + 专业型性格'
        },
        8: {
            'level': 8,
            'features': ['周报多维数据透视', '严格型性格'],
            'icon': '📊',
            'description': '周报数据透视 + 严格型性格'
        },
        13: {
            'level': 13,
            'features': ['高级商店', '毒舌型性格'],
            'icon': '🛒',
            'description': '高级商店 + 毒舌型性格'
        },
        16: {
            'level': 16,
            'features': ['高级道具'],
            'icon': '🏆',
            'description': '高级道具解锁'
        },
        20: {
            'level': 20,
            'features': ['特殊道具', '最高等级'],
            'icon': '👑',
            'description': '特殊道具 + 最高等级'
        }
    }
    
    # 找到下一个里程碑
    for milestone_level in sorted(unlock_milestones.keys()):
        if user_level < milestone_level:
            return unlock_milestones[milestone_level]
    
    # 已经是最高等级
    return None

def format_unlock_progress_message(user_data, exp_gained=0):
    """
    格式化解锁进度激励消息
    
    Args:
        user_data: 用户游戏化数据
        exp_gained: 本次获得的经验值
    
    Returns:
        str: 激励消息
    """
    current_level = user_data.get('level', 1)
    current_exp = user_data.get('current_exp', 0)
    
    # 获取下一个解锁信息
    next_unlock = get_next_unlock_info(current_level)
    
    if not next_unlock:
        # 已经是最高等级
        return "\n🎉 恭喜！你已经达到最高等级LV20，解锁了所有功能！"
    
    # 计算距离下一个里程碑还需要多少经验
    levels_to_go = next_unlock['level'] - current_level
    
    # 计算还需要多少总经验值
    exp_needed = 0
    for level in range(current_level, next_unlock['level']):
        exp_needed += LEVEL_EXP_REQUIRED.get(level, 100)
    
    # 减去当前已有的经验
    exp_needed -= current_exp
    
    # 生成激励消息
    if levels_to_go == 1:
        # 距离下一个里程碑只差1级
        message = f"\n💪 真棒！再升1级就能解锁 {next_unlock['icon']} {next_unlock['description']}！"
        message += f"\n   还需要 {exp_needed} EXP"
        
        if exp_gained > 0:
            # 计算按照当前速度还需要多少次
            times_needed = max(1, exp_needed // exp_gained)
            message += f"（按今天的速度，大约还需要 {times_needed} 次更新）"
    
    elif levels_to_go <= 3:
        # 距离下一个里程碑2-3级
        message = f"\n🎯 加油！还差 {levels_to_go} 级可解锁 {next_unlock['icon']} {next_unlock['description']}！"
        message += f"\n   还需要 {exp_needed} EXP"
    
    else:
        # 距离下一个里程碑较远
        message = f"\n🌟 继续努力！LV{next_unlock['level']} 可解锁 {next_unlock['icon']} {next_unlock['description']}"
        message += f"\n   当前 LV{current_level}，还需要 {exp_needed} EXP"
    
    return message

def format_current_unlocks(user_level):
    """
    格式化当前已解锁的功能列表
    
    Args:
        user_level: 当前等级
    
    Returns:
        str: 已解锁功能列表
    """
    unlocked = []
    
    if user_level >= 1:
        unlocked.append("✅ 四象限报告")
        unlocked.append("✅ 友好型性格")
    
    if user_level >= 4:
        unlocked.append("✅ 每日成就盲盒")
        unlocked.append("✅ 专业型性格")
    
    if user_level >= 8:
        unlocked.append("✅ 周报数据透视")
        unlocked.append("✅ 严格型性格")
    
    if user_level >= 13:
        unlocked.append("✅ 高级商店")
        unlocked.append("✅ 毒舌型性格")
    
    if user_level >= 16:
        unlocked.append("✅ 高级道具")
    
    if user_level >= 20:
        unlocked.append("✅ 特殊道具")
        unlocked.append("✅ 最高等级")
    
    if not unlocked:
        return ""
    
    message = "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
    message += "🎁 已解锁功能：\n"
    for item in unlocked:
        message += f"   {item}\n"
    message += "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    return message
