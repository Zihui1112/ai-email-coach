-- 修复Supabase行级安全策略（RLS）
-- 在Supabase SQL编辑器中执行此脚本

-- 1. 启用RLS（如果还没启用）
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_configs ENABLE ROW LEVEL SECURITY;

-- 2. 删除旧策略（如果存在）
DROP POLICY IF EXISTS "允许所有操作" ON tasks;
DROP POLICY IF EXISTS "允许用户访问自己的任务" ON tasks;
DROP POLICY IF EXISTS "允许用户创建任务" ON tasks;
DROP POLICY IF EXISTS "允许用户更新任务" ON tasks;
DROP POLICY IF EXISTS "允许用户删除任务" ON tasks;

-- 3. 创建新的RLS策略 - 允许所有操作（开发环境）
-- 注意：生产环境应该使用更严格的策略

-- 方案A：完全开放（适合开发测试）
CREATE POLICY "允许所有操作" ON tasks
    FOR ALL
    USING (true)
    WITH CHECK (true);

CREATE POLICY "允许所有操作" ON user_configs
    FOR ALL
    USING (true)
    WITH CHECK (true);

-- 方案B：基于用户邮箱的策略（更安全，但需要认证）
-- 取消下面的注释来使用方案B
/*
-- 允许查询自己的任务
CREATE POLICY "允许用户查询自己的任务" ON tasks
    FOR SELECT
    USING (true);

-- 允许创建任务
CREATE POLICY "允许用户创建任务" ON tasks
    FOR INSERT
    WITH CHECK (true);

-- 允许更新自己的任务
CREATE POLICY "允许用户更新自己的任务" ON tasks
    FOR UPDATE
    USING (true)
    WITH CHECK (true);

-- 允许删除自己的任务
CREATE POLICY "允许用户删除自己的任务" ON tasks
    FOR DELETE
    USING (true);

-- user_configs表的策略
CREATE POLICY "允许用户访问自己的配置" ON user_configs
    FOR ALL
    USING (true)
    WITH CHECK (true);
*/

-- 4. 验证策略
SELECT schemaname, tablename, policyname, permissive, roles, cmd, qual, with_check
FROM pg_policies
WHERE tablename IN ('tasks', 'user_configs');
