-- 清理所有任务数据脚本
-- 用于 v4.1 优化前清空旧数据，从头开始

-- ============================================
-- 警告：此操作不可逆！
-- ============================================
-- 执行前请确认：
-- 1. 已备份重要数据（如果需要）
-- 2. 确认要删除所有任务记录
-- 3. 游戏化数据（等级、经验值、金币）不会被删除

-- ============================================
-- 删除所有任务数据
-- ============================================

-- 1. 删除所有任务
DELETE FROM tasks;

-- 2. 删除任务进度快照
DELETE FROM task_progress_snapshot;

-- 3. 删除任务历史记录
DELETE FROM task_history;

-- ============================================
-- 验证清理结果
-- ============================================

-- 检查任务表
DO $$
DECLARE
    task_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO task_count FROM tasks;
    
    IF task_count = 0 THEN
        RAISE NOTICE '✓ 任务表已清空';
    ELSE
        RAISE WARNING '警告：任务表还有 % 条记录', task_count;
    END IF;
END $$;

-- 检查快照表
DO $$
DECLARE
    snapshot_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO snapshot_count FROM task_progress_snapshot;
    
    IF snapshot_count = 0 THEN
        RAISE NOTICE '✓ 快照表已清空';
    ELSE
        RAISE WARNING '警告：快照表还有 % 条记录', snapshot_count;
    END IF;
END $$;

-- 检查历史表
DO $$
DECLARE
    history_count INTEGER;
BEGIN
    SELECT COUNT(*) INTO history_count FROM task_history;
    
    IF history_count = 0 THEN
        RAISE NOTICE '✓ 历史表已清空';
    ELSE
        RAISE WARNING '警告：历史表还有 % 条记录', history_count;
    END IF;
END $$;

-- ============================================
-- 完成
-- ============================================

DO $$
BEGIN
    RAISE NOTICE '========================================';
    RAISE NOTICE '任务数据清理完成';
    RAISE NOTICE '========================================';
    RAISE NOTICE '游戏化数据（等级、经验值、金币）已保留';
    RAISE NOTICE '可以开始添加新任务了';
    RAISE NOTICE '========================================';
END $$;
