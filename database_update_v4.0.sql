-- 数据库更新脚本 v4.0 - 任务编号系统
-- 添加任务编号、软删除、暂缓提醒相关字段

-- ============================================
-- 第零部分：更新约束（确保支持 paused 状态）
-- ============================================

-- 0. 更新 status 字段约束，确保支持 'paused' 状态
ALTER TABLE tasks DROP CONSTRAINT IF EXISTS tasks_status_check;
ALTER TABLE tasks ADD CONSTRAINT tasks_status_check 
    CHECK (status IN ('active', 'completed', 'paused', 'backlog'));

-- ============================================
-- 第一部分：添加新字段
-- ============================================

-- 1. 为 tasks 表添加任务编号相关字段
ALTER TABLE tasks 
ADD COLUMN IF NOT EXISTS task_order INTEGER DEFAULT 0 CHECK (task_order >= 0),
ADD COLUMN IF NOT EXISTS display_number VARCHAR(10),
ADD COLUMN IF NOT EXISTS is_deleted BOOLEAN DEFAULT FALSE,
ADD COLUMN IF NOT EXISTS deleted_at TIMESTAMP WITH TIME ZONE,
ADD COLUMN IF NOT EXISTS last_reminded_date DATE;

-- 2. 添加注释
COMMENT ON COLUMN tasks.task_order IS '任务在象限内的排序位置（1, 2, 3...）';
COMMENT ON COLUMN tasks.display_number IS '显示编号（如Q1-1, Q2-3）';
COMMENT ON COLUMN tasks.is_deleted IS '软删除标记';
COMMENT ON COLUMN tasks.deleted_at IS '删除时间';
COMMENT ON COLUMN tasks.last_reminded_date IS '最后提醒日期（用于暂缓任务）';

-- ============================================
-- 第二部分：创建索引优化查询性能
-- ============================================

-- 3. 创建复合索引：用户+象限+编号（用于快速查找任务）
CREATE INDEX IF NOT EXISTS idx_tasks_user_quadrant_order 
ON tasks(user_email, quadrant, task_order);

-- 4. 创建索引：软删除标记（用于过滤已删除任务）
CREATE INDEX IF NOT EXISTS idx_tasks_is_deleted 
ON tasks(is_deleted);

-- 5. 创建复合索引：状态+软删除（用于查询活跃/暂缓任务）
CREATE INDEX IF NOT EXISTS idx_tasks_status_deleted 
ON tasks(status, is_deleted);

-- ============================================
-- 第三部分：数据迁移
-- ============================================

-- 6. 删除所有已完成的任务（status='completed'）
-- 注意：这是永久删除，不是软删除
DELETE FROM tasks WHERE status = 'completed';

-- 7. 将 'backlog' 状态改为 'paused'（统一暂缓任务状态）
UPDATE tasks 
SET status = 'paused' 
WHERE status = 'backlog';

-- 8. 为现有活跃任务分配编号（按象限和创建时间排序）
-- Q1 任务编号
WITH numbered_q1 AS (
    SELECT 
        id,
        ROW_NUMBER() OVER (PARTITION BY user_email ORDER BY created_at ASC) as new_order
    FROM tasks
    WHERE quadrant = 1 AND status = 'active' AND is_deleted = FALSE
)
UPDATE tasks t
SET 
    task_order = n.new_order,
    display_number = 'Q1-' || n.new_order
FROM numbered_q1 n
WHERE t.id = n.id;

-- Q2 任务编号
WITH numbered_q2 AS (
    SELECT 
        id,
        ROW_NUMBER() OVER (PARTITION BY user_email ORDER BY created_at ASC) as new_order
    FROM tasks
    WHERE quadrant = 2 AND status = 'active' AND is_deleted = FALSE
)
UPDATE tasks t
SET 
    task_order = n.new_order,
    display_number = 'Q2-' || n.new_order
FROM numbered_q2 n
WHERE t.id = n.id;

-- Q3 任务编号
WITH numbered_q3 AS (
    SELECT 
        id,
        ROW_NUMBER() OVER (PARTITION BY user_email ORDER BY created_at ASC) as new_order
    FROM tasks
    WHERE quadrant = 3 AND status = 'active' AND is_deleted = FALSE
)
UPDATE tasks t
SET 
    task_order = n.new_order,
    display_number = 'Q3-' || n.new_order
FROM numbered_q3 n
WHERE t.id = n.id;

-- Q4 任务编号
WITH numbered_q4 AS (
    SELECT 
        id,
        ROW_NUMBER() OVER (PARTITION BY user_email ORDER BY created_at ASC) as new_order
    FROM tasks
    WHERE quadrant = 4 AND status = 'active' AND is_deleted = FALSE
)
UPDATE tasks t
SET 
    task_order = n.new_order,
    display_number = 'Q4-' || n.new_order
FROM numbered_q4 n
WHERE t.id = n.id;

-- 9. 为暂缓任务分配编号
WITH numbered_paused AS (
    SELECT 
        id,
        ROW_NUMBER() OVER (PARTITION BY user_email ORDER BY created_at ASC) as new_order
    FROM tasks
    WHERE status = 'paused' AND is_deleted = FALSE
)
UPDATE tasks t
SET 
    task_order = n.new_order,
    display_number = '暂缓-' || n.new_order
FROM numbered_paused n
WHERE t.id = n.id;

-- 10. 确保所有现有任务的 is_deleted 字段为 FALSE
UPDATE tasks 
SET is_deleted = FALSE 
WHERE is_deleted IS NULL;

-- ============================================
-- 第四部分：验证数据完整性
-- ============================================

-- 11. 验证：检查是否有任务没有分配编号
DO $$
DECLARE
    unassigned_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO unassigned_count
    FROM tasks
    WHERE is_deleted = FALSE 
      AND (task_order IS NULL OR task_order = 0 OR display_number IS NULL);
    
    IF unassigned_count > 0 THEN
        RAISE WARNING '警告：有 % 个任务没有分配编号', unassigned_count;
    ELSE
        RAISE NOTICE '✓ 所有任务已成功分配编号';
    END IF;
END $$;

-- 12. 验证：检查编号是否连续（每个用户的每个象限）
DO $$
DECLARE
    gap_count INTEGER;
BEGIN
    WITH task_gaps AS (
        SELECT 
            user_email,
            quadrant,
            task_order,
            LAG(task_order) OVER (PARTITION BY user_email, quadrant ORDER BY task_order) as prev_order
        FROM tasks
        WHERE status = 'active' AND is_deleted = FALSE
    )
    SELECT COUNT(*) INTO gap_count
    FROM task_gaps
    WHERE prev_order IS NOT NULL 
      AND task_order != prev_order + 1;
    
    IF gap_count > 0 THEN
        RAISE WARNING '警告：发现 % 个编号间隙', gap_count;
    ELSE
        RAISE NOTICE '✓ 所有任务编号连续无间隙';
    END IF;
END $$;

-- ============================================
-- 第五部分：统计信息
-- ============================================

-- 13. 显示迁移统计
DO $$
DECLARE
    total_active INTEGER;
    total_paused INTEGER;
    total_users INTEGER;
BEGIN
    SELECT COUNT(*) INTO total_active FROM tasks WHERE status = 'active' AND is_deleted = FALSE;
    SELECT COUNT(*) INTO total_paused FROM tasks WHERE status = 'paused' AND is_deleted = FALSE;
    SELECT COUNT(DISTINCT user_email) INTO total_users FROM tasks WHERE is_deleted = FALSE;
    
    RAISE NOTICE '========================================';
    RAISE NOTICE 'v4.0 数据库迁移完成';
    RAISE NOTICE '========================================';
    RAISE NOTICE '活跃任务数：%', total_active;
    RAISE NOTICE '暂缓任务数：%', total_paused;
    RAISE NOTICE '用户数：%', total_users;
    RAISE NOTICE '========================================';
END $$;

-- ============================================
-- 完成
-- ============================================
