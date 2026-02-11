-- 数据库更新脚本 v3.0 - 游戏化系统
-- 添加等级、经验值、金币系统

-- 1. 创建用户游戏化数据表
CREATE TABLE IF NOT EXISTS user_gamification (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_email VARCHAR(255) NOT NULL UNIQUE,
    level INTEGER DEFAULT 1 CHECK (level >= 1 AND level <= 20),
    current_exp INTEGER DEFAULT 0 CHECK (current_exp >= 0),
    total_exp INTEGER DEFAULT 0 CHECK (total_exp >= 0),
    coins INTEGER DEFAULT 200 CHECK (coins >= 0),
    ai_personality VARCHAR(50) DEFAULT 'friendly' CHECK (ai_personality IN ('friendly', 'professional', 'strict', 'toxic')),
    consecutive_q1_days INTEGER DEFAULT 0 CHECK (consecutive_q1_days >= 0),
    last_q1_complete_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. 创建等级配置表（升级所需经验值）
CREATE TABLE IF NOT EXISTS level_config (
    level INTEGER PRIMARY KEY CHECK (level >= 1 AND level <= 20),
    exp_required INTEGER NOT NULL CHECK (exp_required > 0),
    unlocked_features JSONB,
    unlocked_personalities JSONB
);

-- 3. 创建商店道具表
CREATE TABLE IF NOT EXISTS shop_items (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    item_code VARCHAR(50) NOT NULL UNIQUE,
    item_name VARCHAR(100) NOT NULL,
    item_description TEXT,
    price INTEGER NOT NULL CHECK (price > 0),
    item_type VARCHAR(50) NOT NULL CHECK (item_type IN ('basic', 'incentive', 'advanced', 'special')),
    required_level INTEGER DEFAULT 13 CHECK (required_level >= 1 AND required_level <= 20),
    usage_limit_type VARCHAR(20) CHECK (usage_limit_type IN ('daily', 'weekly', 'monthly', 'unlimited')),
    usage_limit_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. 创建用户道具库存表
CREATE TABLE IF NOT EXISTS user_inventory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_email VARCHAR(255) NOT NULL,
    item_code VARCHAR(50) NOT NULL,
    quantity INTEGER DEFAULT 0 CHECK (quantity >= 0),
    last_used_date DATE,
    usage_count_daily INTEGER DEFAULT 0,
    usage_count_weekly INTEGER DEFAULT 0,
    usage_count_monthly INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_email, item_code)
);

-- 5. 创建经验值历史记录表
CREATE TABLE IF NOT EXISTS exp_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_email VARCHAR(255) NOT NULL,
    task_name VARCHAR(500),
    quadrant INTEGER CHECK (quadrant IN (1, 2, 3, 4)),
    progress_change INTEGER,
    exp_gained INTEGER NOT NULL,
    coins_gained INTEGER DEFAULT 0,
    reason VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. 插入等级配置数据
INSERT INTO level_config (level, exp_required, unlocked_features, unlocked_personalities) VALUES
(1, 100, '["四象限报告"]', '["friendly"]'),
(2, 200, '["四象限报告"]', '["friendly"]'),
(3, 300, '["四象限报告"]', '["friendly"]'),
(4, 400, '["四象限报告", "每日成就盲盒"]', '["friendly", "professional"]'),
(5, 500, '["四象限报告", "每日成就盲盒"]', '["friendly", "professional"]'),
(6, 600, '["四象限报告", "每日成就盲盒"]', '["friendly", "professional"]'),
(7, 700, '["四象限报告", "每日成就盲盒"]', '["friendly", "professional"]'),
(8, 800, '["四象限报告", "每日成就盲盒", "周报多维数据透视"]', '["friendly", "professional", "strict"]'),
(9, 900, '["四象限报告", "每日成就盲盒", "周报多维数据透视"]', '["friendly", "professional", "strict"]'),
(10, 1000, '["四象限报告", "每日成就盲盒", "周报多维数据透视"]', '["friendly", "professional", "strict"]'),
(11, 1100, '["四象限报告", "每日成就盲盒", "周报多维数据透视"]', '["friendly", "professional", "strict"]'),
(12, 1200, '["四象限报告", "每日成就盲盒", "周报多维数据透视"]', '["friendly", "professional", "strict"]'),
(13, 1300, '["四象限报告", "每日成就盲盒", "周报多维数据透视", "高级商店"]', '["friendly", "professional", "strict", "toxic"]'),
(14, 1400, '["四象限报告", "每日成就盲盒", "周报多维数据透视", "高级商店"]', '["friendly", "professional", "strict", "toxic"]'),
(15, 1500, '["四象限报告", "每日成就盲盒", "周报多维数据透视", "高级商店"]', '["friendly", "professional", "strict", "toxic"]'),
(16, 1600, '["四象限报告", "每日成就盲盒", "周报多维数据透视", "高级商店", "高级道具"]', '["friendly", "professional", "strict", "toxic"]'),
(17, 1700, '["四象限报告", "每日成就盲盒", "周报多维数据透视", "高级商店", "高级道具"]', '["friendly", "professional", "strict", "toxic"]'),
(18, 1800, '["四象限报告", "每日成就盲盒", "周报多维数据透视", "高级商店", "高级道具"]', '["friendly", "professional", "strict", "toxic"]'),
(19, 1900, '["四象限报告", "每日成就盲盒", "周报多维数据透视", "高级商店", "高级道具"]', '["friendly", "professional", "strict", "toxic"]'),
(20, 2000, '["四象限报告", "每日成就盲盒", "周报多维数据透视", "高级商店", "高级道具", "特殊道具"]', '["friendly", "professional", "strict", "toxic"]')
ON CONFLICT (level) DO NOTHING;

-- 7. 插入商店道具数据（基础道具）
INSERT INTO shop_items (item_code, item_name, item_description, price, item_type, required_level, usage_limit_type, usage_limit_count) VALUES
('delay_voucher', '🛡️ 拖延对冲券', '免除惩罚，任务顺延明天', 100, 'basic', 13, 'weekly', 1),
('quadrant_swap', '🔄 象限置换权', 'Q1→Q4合法降级', 50, 'basic', 13, 'weekly', 1),
('time_rewind', '⏰ 时间回溯卡', '撤销今天的任务更新', 80, 'basic', 13, 'weekly', 1),
('task_splitter', '📝 任务分解器', 'AI帮你把大任务拆成小任务', 60, 'basic', 13, 'unlimited', 0),
('focus_boost', '🎯 专注加成卡', '当日Q1任务EXP x1.5', 70, 'basic', 13, 'weekly', 3),
('praise_box', '💬 AI夸夸盲盒', '500字小作文赞美', 30, 'incentive', 13, 'unlimited', 0),
('exp_boost', '⚡ 经验加速卡', '当日所有EXP x2', 80, 'incentive', 13, 'weekly', 2),
('coin_double', '💰 金币翻倍卡', '当日金币收入 x2', 100, 'incentive', 13, 'weekly', 1),
('lucky_dice', '🎲 幸运骰子', '随机获得50-200币', 50, 'incentive', 13, 'daily', 1),
('monthly_badge', '🏆 月度勋章', '生成精美月报卡片', 500, 'advanced', 16, 'monthly', 1),
('personality_unlock', '🎭 性格解锁卡', '永久解锁一个新性格', 300, 'advanced', 16, 'unlimited', 0),
('data_lens', '📊 数据透视镜', '查看详细的任务分析报告', 200, 'advanced', 16, 'weekly', 1),
('future_predict', '🔮 未来预测', 'AI预测你下周的任务完成率', 150, 'advanced', 16, 'weekly', 1),
('vip_card', '👑 VIP特权卡', '7天内所有EXP和金币 x1.5', 1000, 'special', 20, 'monthly', 1),
('achievement_harvest', '🌟 成就收割机', '立即完成所有连击成就', 800, 'special', 20, 'monthly', 1),
('custom_ai', '🎨 定制AI', '自定义AI的说话风格', 2000, 'special', 20, 'unlimited', 0)
ON CONFLICT (item_code) DO NOTHING;

-- 8. 为现有用户初始化游戏化数据
INSERT INTO user_gamification (user_email, level, current_exp, total_exp, coins, ai_personality)
SELECT DISTINCT user_email, 1, 0, 0, 200, 'friendly'
FROM tasks
ON CONFLICT (user_email) DO NOTHING;

-- 9. 创建索引
CREATE INDEX IF NOT EXISTS idx_user_gamification_email ON user_gamification(user_email);
CREATE INDEX IF NOT EXISTS idx_user_gamification_level ON user_gamification(level);
CREATE INDEX IF NOT EXISTS idx_shop_items_code ON shop_items(item_code);
CREATE INDEX IF NOT EXISTS idx_shop_items_level ON shop_items(required_level);
CREATE INDEX IF NOT EXISTS idx_user_inventory_email ON user_inventory(user_email);
CREATE INDEX IF NOT EXISTS idx_exp_history_email ON exp_history(user_email);
CREATE INDEX IF NOT EXISTS idx_exp_history_date ON exp_history(created_at);

-- 10. 启用 RLS
ALTER TABLE user_gamification ENABLE ROW LEVEL SECURITY;
ALTER TABLE shop_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_inventory ENABLE ROW LEVEL SECURITY;
ALTER TABLE exp_history ENABLE ROW LEVEL SECURITY;

-- 11. 添加注释
COMMENT ON TABLE user_gamification IS '用户游戏化数据表，存储等级、经验值、金币等信息';
COMMENT ON TABLE level_config IS '等级配置表，定义每个等级的升级要求和解锁内容';
COMMENT ON TABLE shop_items IS '商店道具表，定义所有可购买的道具';
COMMENT ON TABLE user_inventory IS '用户道具库存表，记录用户拥有的道具';
COMMENT ON TABLE exp_history IS '经验值历史记录表，记录每次获得经验值的详情';

COMMENT ON COLUMN user_gamification.level IS '用户等级（1-20）';
COMMENT ON COLUMN user_gamification.current_exp IS '当前等级的经验值';
COMMENT ON COLUMN user_gamification.total_exp IS '累计总经验值';
COMMENT ON COLUMN user_gamification.coins IS '虚拟货币余额';
COMMENT ON COLUMN user_gamification.ai_personality IS 'AI性格类型';
COMMENT ON COLUMN user_gamification.consecutive_q1_days IS '连续完成Q1任务的天数';
