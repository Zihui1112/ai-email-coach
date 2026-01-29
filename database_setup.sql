-- AI邮件督导系统数据库表结构
-- 在Supabase中执行此SQL脚本创建所需的表

-- 1. 任务表
CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_email VARCHAR(255) NOT NULL,
    task_name VARCHAR(500) NOT NULL,
    progress_percentage INTEGER DEFAULT 0 CHECK (progress_percentage >= 0 AND progress_percentage <= 100),
    quadrant INTEGER CHECK (quadrant IN (1, 2, 3, 4)),
    status VARCHAR(20) DEFAULT 'active' CHECK (status IN ('active', 'completed', 'backlog')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    stalled_days INTEGER DEFAULT 0,
    UNIQUE(user_email, task_name)
);

-- 2. 用户配置表
CREATE TABLE IF NOT EXISTS user_configs (
    user_email VARCHAR(255) PRIMARY KEY,
    persona VARCHAR(20) DEFAULT 'neutral' CHECK (persona IN ('toxic', 'warm', 'neutral')),
    daily_edit_count INTEGER DEFAULT 0,
    max_daily_edits INTEGER DEFAULT 2,
    timezone VARCHAR(50) DEFAULT 'UTC',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. 邮件日志表
CREATE TABLE IF NOT EXISTS email_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_email VARCHAR(255) NOT NULL,
    email_type VARCHAR(50) NOT NULL,
    subject VARCHAR(500),
    content TEXT,
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'sent' CHECK (status IN ('sent', 'failed', 'pending'))
);

-- 4. 任务历史记录表
CREATE TABLE IF NOT EXISTS task_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_email VARCHAR(255) NOT NULL,
    task_name VARCHAR(500) NOT NULL,
    old_progress INTEGER,
    new_progress INTEGER,
    old_status VARCHAR(20),
    new_status VARCHAR(20),
    change_type VARCHAR(20) NOT NULL CHECK (change_type IN ('progress_update', 'status_change', 'created', 'deleted')),
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. 统计报告表
CREATE TABLE IF NOT EXISTS statistics_reports (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_email VARCHAR(255) NOT NULL,
    report_type VARCHAR(20) NOT NULL CHECK (report_type IN ('weekly', 'monthly')),
    report_period VARCHAR(20) NOT NULL, -- 例如: '2024-W01', '2024-01'
    completion_rate DECIMAL(5,2),
    quadrant_distribution JSONB,
    achievements JSONB,
    improvements JSONB,
    trend_data JSONB,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_email, report_type, report_period)
);

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_tasks_user_email ON tasks(user_email);
CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status);
CREATE INDEX IF NOT EXISTS idx_tasks_updated_at ON tasks(updated_at);
CREATE INDEX IF NOT EXISTS idx_email_logs_user_email ON email_logs(user_email);
CREATE INDEX IF NOT EXISTS idx_email_logs_sent_at ON email_logs(sent_at);
CREATE INDEX IF NOT EXISTS idx_task_history_user_email ON task_history(user_email);
CREATE INDEX IF NOT EXISTS idx_task_history_changed_at ON task_history(changed_at);
CREATE INDEX IF NOT EXISTS idx_statistics_user_email ON statistics_reports(user_email);
CREATE INDEX IF NOT EXISTS idx_statistics_period ON statistics_reports(report_period);

-- 创建RLS (Row Level Security) 策略确保数据隔离
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_configs ENABLE ROW LEVEL SECURITY;
ALTER TABLE email_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE task_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE statistics_reports ENABLE ROW LEVEL SECURITY;

-- 示例RLS策略（需要根据实际认证方式调整）
-- CREATE POLICY "Users can only access their own tasks" ON tasks
--     FOR ALL USING (user_email = auth.email());

-- CREATE POLICY "Users can only access their own configs" ON user_configs
--     FOR ALL USING (user_email = auth.email());

-- 插入示例数据（可选）
INSERT INTO user_configs (user_email, persona, daily_edit_count, max_daily_edits) 
VALUES 
    ('test@example.com', 'warm', 0, 2),
    ('demo@example.com', 'toxic', 1, 2)
ON CONFLICT (user_email) DO NOTHING;

INSERT INTO tasks (user_email, task_name, progress_percentage, quadrant, status)
VALUES 
    ('test@example.com', '完成项目文档', 60, 1, 'active'),
    ('test@example.com', '学习新技术', 30, 2, 'active'),
    ('test@example.com', '回复邮件', 80, 3, 'active'),
    ('demo@example.com', '整理桌面', 0, 4, 'backlog')
ON CONFLICT (user_email, task_name) DO NOTHING;