# Bug修复：db_headers 变量引用错误

## 🐛 问题描述

**错误信息**：
```
检测到性格切换命令: friendly
❌ 处理失败: local variable 'db_headers' referenced before assignment
Error: Process completed with exit code 1.
```

**原因**：
在 `scripts/check_email_reply.py` 中，`db_headers` 变量在使用前没有定义。

## 📍 问题位置

### 错误的代码顺序：
```python
# 第420行：使用 db_headers（但还没定义）
personality_switch_result = switch_ai_personality(supabase_url, db_headers, email_username, personality_switch_cmd)

# 第530行：定义 db_headers（太晚了）
db_headers = {
    "apikey": supabase_key,
    "Authorization": f"Bearer {supabase_key}",
    "Content-Type": "application/json"
}
```

## ✅ 修复方案

将 `db_headers` 的定义提前到使用之前。

### 修复后的代码：
```python
# 第421行：提前定义 db_headers
db_headers = {
    "apikey": supabase_key,
    "Authorization": f"Bearer {supabase_key}",
    "Content-Type": "application/json"
}

# 第427行：使用 db_headers（现在已经定义了）
personality_switch_result = switch_ai_personality(supabase_url, db_headers, email_username, personality_switch_cmd)
```

## 🔧 修改内容

### 文件：`scripts/check_email_reply.py`

1. **在第421行添加 `db_headers` 定义**（在性格切换命令检测之前）
2. **删除第530行的重复定义**

## 📝 修改详情

### 修改1：提前定义 db_headers
```python
print(f"\n✅ 找到最新回复（{latest_time}）")
print(f"内容预览: {latest_reply[:100]}...")

# 提前定义 db_headers，因为后面的命令检测需要用到
db_headers = {
    "apikey": supabase_key,
    "Authorization": f"Bearer {supabase_key}",
    "Content-Type": "application/json"
}

# 检查是否有性格切换命令
personality_switch_cmd = parse_personality_switch_command(latest_reply)
```

### 修改2：删除重复定义
```python
# 更新数据库
print("\n更新数据库...")

# 删除了这里的 db_headers 定义（已经在前面定义过了）

feedback_content = "📊 任务更新反馈\n\n"
```

## ✅ 验证

修复后，变量使用顺序正确：
1. 第421行：定义 `db_headers`
2. 第427行：使用 `db_headers`（性格切换）
3. 第435行：使用 `db_headers`（购买命令）
4. 第530行：使用 `db_headers`（更新数据库）

## 🚀 部署

```bash
# 提交修复
git add scripts/check_email_reply.py
git commit -m "修复：db_headers 变量引用错误"
git push origin main
```

## 🧪 测试

修复后，性格切换命令应该能正常工作：
1. 回复邮件：`切换性格：专业型`
2. 系统应该能正确识别并切换性格
3. 不再出现 `referenced before assignment` 错误

---

**修复日期**：2026-02-11  
**影响版本**：v3.2  
**修复状态**：已完成  
**测试状态**：待测试
