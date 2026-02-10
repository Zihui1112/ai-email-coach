-- 数据库更新脚本 v2.0
-- 添加新功能所需的字段和表

-- 1. 修改 tasks 表的 status 字段，添加 'paused' 状态
ALTER TABLE tasks DROP CONSTRAINT IF EXISTS tasks_status_check;
ALTER TABLE tasks ADD CONSTRAINT tasks_status_check 
    CHECK (status IN ('active', 'completed', 'paused', 'backlog'));

-- 2. 添加用户回复追踪表
CREATE TABLE IF NOT EXISTS user_reply_tracking (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_email VARCHAR(255) NOT NULL UNIQUE,
    last_reply_date DATE,
    consecutive_no_reply_days INTEGER DEFAULT 0,
    total_replies INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. 添加任务进度历史表（用于AI分析进度变化）
CREATE TABLE IF NOT EXISTS task_progress_snapshot (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_email VARCHAR(255) NOT NULL,
    task_name VARCHAR(500) NOT NULL,
    progress_percentage INTEGER,
    status VARCHAR(20),
    snapshot_date DATE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_email, task_name, snapshot_date)
);

-- 4. 创建索引
CREATE INDEX IF NOT EXISTS idx_user_reply_tracking_email ON user_reply_tracking(user_email);
CREATE INDEX IF NOT EXISTS idx_task_progress_snapshot_email ON task_progress_snapshot(user_email);
CREATE INDEX IF NOT EXISTS idx_task_progress_snapshot_date ON task_progress_snapshot(snapshot_date);

-- 5. 启用 RLS
ALTER TABLE user_reply_tracking ENABLE ROW LEVEL SECURITY;
ALTER TABLE task_progress_snapshot ENABLE ROW LEVEL SECURITY;

-- 6. 初始化用户回复追踪数据
INSERT INTO user_reply_tracking (user_email, last_reply_date, consecutive_no_reply_days, total_replies)
SELECT DISTINCT user_email, CURRENT_DATE, 0, 0
FROM tasks
ON CONFLICT (user_email) DO NOTHING;

-- 7. 更新现有的 'backlog' 状态为 'paused'（如果需要）
-- UPDATE tasks SET status = 'paused' WHERE status = 'backlog';

COMMENT ON TABLE user_reply_tracking IS '用户回复追踪表，记录用户最后回复时间和连续未回复天数';
COMMENT ON TABLE task_progress_snapshot IS '任务进度快照表，用于AI分析进度变化趋势';
COMMENT ON COLUMN user_reply_tracking.consecutive_no_reply_days IS '连续未回复天数，用于生成个性化提醒';
COMMENT ON COLUMN task_progress_snapshot.snapshot_date IS '快照日期，每天记录一次任务进度';
