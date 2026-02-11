-- 数据库更新脚本 v3.1 - 惩罚机制
-- 添加惩罚相关字段和坚持奖励追踪

-- 1. 为 user_gamification 表添加新字段
ALTER TABLE user_gamification 
ADD COLUMN IF NOT EXISTS consecutive_reply_days INTEGER DEFAULT 0 CHECK (consecutive_reply_days >= 0),
ADD COLUMN IF NOT EXISTS last_reply_date DATE,
ADD COLUMN IF NOT EXISTS total_reply_days INTEGER DEFAULT 0 CHECK (total_reply_days >= 0),
ADD COLUMN IF NOT EXISTS last_punishment_date DATE,
ADD COLUMN IF NOT EXISTS total_punishments INTEGER DEFAULT 0 CHECK (total_punishments >= 0);

-- 2. 为 tasks 表添加最后更新时间字段（如果不存在）
ALTER TABLE tasks 
ADD COLUMN IF NOT EXISTS last_progress_update DATE;

-- 3. 创建惩罚历史记录表
CREATE TABLE IF NOT EXISTS punishment_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_email VARCHAR(255) NOT NULL,
    punishment_type VARCHAR(50) NOT NULL CHECK (punishment_type IN ('no_reply', 'task_delay', 'progress_decline')),
    coins_deducted INTEGER DEFAULT 0,
    exp_deducted INTEGER DEFAULT 0,
    level_before INTEGER,
    level_after INTEGER,
    reason TEXT,
    is_newbie_protected BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. 创建坚持奖励记录表
CREATE TABLE IF NOT EXISTS persistence_rewards (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_email VARCHAR(255) NOT NULL,
    milestone_days INTEGER NOT NULL CHECK (milestone_days > 0),
    coins_rewarded INTEGER DEFAULT 0,
    exp_rewarded INTEGER DEFAULT 0,
    achievement_name VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. 更新商店道具 - 添加惩罚相关道具
INSERT INTO shop_items (item_code, item_name, item_description, price, item_type, required_level, usage_limit_type, usage_limit_count) VALUES
('punishment_waiver', '🛡️ 惩罚减免券', '免除一次未回复惩罚', 50, 'basic', 1, 'weekly', 2),
('streak_protector', '🔥 连击保护卡', '保护连续回复记录不中断', 100, 'basic', 1, 'monthly', 1),
('progress_lock', '🔒 进度锁定符', '锁定任务进度3天，防止倒退惩罚', 80, 'basic', 1, 'weekly', 1),
('downgrade_shield', '🛡️ 降级保护盾', '防止降级一次（自动触发）', 200, 'advanced', 13, 'monthly', 1)
ON CONFLICT (item_code) DO NOTHING;

-- 6. 为现有用户初始化新字段
UPDATE user_gamification 
SET 
    consecutive_reply_days = 0,
    total_reply_days = 0,
    total_punishments = 0
WHERE consecutive_reply_days IS NULL;

-- 7. 更新现有任务的最后更新时间
UPDATE tasks 
SET last_progress_update = updated_at::DATE
WHERE last_progress_update IS NULL;

-- 8. 创建索引
CREATE INDEX IF NOT EXISTS idx_punishment_history_email ON punishment_history(user_email);
CREATE INDEX IF NOT EXISTS idx_punishment_history_date ON punishment_history(created_at);
CREATE INDEX IF NOT EXISTS idx_persistence_rewards_email ON persistence_rewards(user_email);
CREATE INDEX IF NOT EXISTS idx_persistence_rewards_milestone ON persistence_rewards(milestone_days);
CREATE INDEX IF NOT EXISTS idx_tasks_last_update ON tasks(last_progress_update);

-- 9. 启用 RLS
ALTER TABLE punishment_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE persistence_rewards ENABLE ROW LEVEL SECURITY;

-- 10. 添加注释
COMMENT ON TABLE punishment_history IS '惩罚历史记录表，记录所有惩罚事件';
COMMENT ON TABLE persistence_rewards IS '坚持奖励记录表，记录所有坚持奖励';

COMMENT ON COLUMN user_gamification.consecutive_reply_days IS '连续回复天数';
COMMENT ON COLUMN user_gamification.last_reply_date IS '最后回复日期';
COMMENT ON COLUMN user_gamification.total_reply_days IS '累计回复天数';
COMMENT ON COLUMN user_gamification.last_punishment_date IS '最后惩罚日期';
COMMENT ON COLUMN user_gamification.total_punishments IS '累计惩罚次数';

COMMENT ON COLUMN tasks.last_progress_update IS '任务进度最后更新日期';

COMMENT ON COLUMN punishment_history.punishment_type IS '惩罚类型：no_reply(未回复), task_delay(任务拖延), progress_decline(进度倒退)';
COMMENT ON COLUMN punishment_history.is_newbie_protected IS '是否受新手保护（LV1-3惩罚减半）';

COMMENT ON COLUMN persistence_rewards.milestone_days IS '里程碑天数（3/7/14/30/60/90）';

