# GitHub Actions 完整部署指南

## 🎯 功能说明

部署后，系统将自动提供：

1. ✅ **每日复盘提醒**：每天22:00自动发送
2. ✅ **每周报告**：每周日21:00自动发送
3. ✅ **每月报告**：每月1号21:00自动发送
4. ✅ **处理回复**：手动触发，处理你的任务更新

---

## 📋 步骤1：创建GitHub仓库

### 1.1 在GitHub创建新仓库

1. 访问 https://github.com
2. 登录你的账号
3. 点击右上角 "+" → "New repository"
4. 填写信息：
   - Repository name: `ai-email-coach`
   - Description: `AI邮件督导系统`
   - 选择 **Public**（公开）
   - **不要**勾选任何初始化选项
5. 点击 "Create repository"

### 1.2 记录仓库地址

创建后会显示类似这样的地址：
```
https://github.com/你的用户名/ai-email-coach.git
```

---

## 📋 步骤2：推送代码到GitHub

### 2.1 配置Git用户信息（如果还没配置）

```bash
git config --global user.name "你的名字"
git config --global user.email "你的邮箱"
```

### 2.2 初始化并推送代码

在项目目录（D:\Plan_maker）打开命令行，执行：

```bash
# 如果还没初始化Git
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit: AI邮件督导系统"

# 添加远程仓库（替换成你的实际地址）
git remote add origin https://github.com/你的用户名/ai-email-coach.git

# 推送代码
git branch -M main
git push -u origin main
```

### 2.3 如果推送需要认证

GitHub不再支持密码登录，需要使用Personal Access Token：

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token" → "Generate new token (classic)"
3. 勾选 `repo` 权限
4. 生成并复制token
5. 推送时，用户名输入GitHub用户名，密码输入token

---

## 📋 步骤3：配置GitHub Secrets

### 3.1 进入仓库设置

1. 在GitHub仓库页面，点击 **Settings**
2. 左侧菜单找到 **Secrets and variables** → **Actions**
3. 点击 **New repository secret**

### 3.2 添加5个Secrets

依次添加以下secrets（点击"New repository secret"，输入Name和Value）：

#### Secret 1: SUPABASE_URL
- Name: `SUPABASE_URL`
- Value: `https://cnmxhxapwksjczfxugtx.supabase.co`

#### Secret 2: SUPABASE_KEY
- Name: `SUPABASE_KEY`
- Value: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNubXhoeGFwd2tzamN6Znh1Z3R4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk2NDU1NzYsImV4cCI6MjA4NTIyMTU3Nn0.SN5os0906ICGcLn6rvRGY8H0BZxXxG0tUsgD6gMwqE4`

#### Secret 3: DEEPSEEK_API_KEY
- Name: `DEEPSEEK_API_KEY`
- Value: `sk-86436af0f3784ea5b99c66e08be29b23`

#### Secret 4: FEISHU_WEBHOOK_URL
- Name: `FEISHU_WEBHOOK_URL`
- Value: `https://open.feishu.cn/open-apis/bot/v2/hook/902a2c44-8edc-4cb4-a7cd-c3d935c8ed8c`

#### Secret 5: EMAIL_163_USERNAME
- Name: `EMAIL_163_USERNAME`
- Value: `15302814198@163.com`

### 3.3 验证Secrets

添加完成后，你应该看到5个secrets：
- SUPABASE_URL
- SUPABASE_KEY
- DEEPSEEK_API_KEY
- FEISHU_WEBHOOK_URL
- EMAIL_163_USERNAME

---

## 📋 步骤4：启用GitHub Actions

### 4.1 检查Actions是否启用

1. 在仓库页面，点击 **Settings**
2. 左侧菜单找到 **Actions** → **General**
3. 确保选择了 "Allow all actions and reusable workflows"
4. 点击 "Save"

### 4.2 查看Workflows

1. 点击仓库顶部的 **Actions** 标签
2. 你应该看到4个workflows：
   - 每日复盘提醒
   - 每周报告
   - 每月报告
   - 处理用户回复

---

## 📋 步骤5：测试Workflows

### 5.1 测试每日复盘提醒

1. 进入 **Actions** 标签
2. 左侧选择 "每日复盘提醒"
3. 点击右侧 "Run workflow" 按钮
4. 选择 `main` 分支
5. 点击绿色的 "Run workflow" 按钮
6. 等待30秒左右
7. 查看飞书群，应该收到复盘提醒！

### 5.2 测试周报

1. 左侧选择 "每周报告"
2. 点击 "Run workflow"
3. 查看飞书群，应该收到周报！

### 5.3 测试月报

1. 左侧选择 "每月报告"
2. 点击 "Run workflow"
3. 查看飞书群，应该收到月报！

### 5.4 测试处理回复

1. 左侧选择 "处理用户回复"
2. 点击 "Run workflow"
3. 在弹出的输入框中输入：`完成了数据库设计60%，这是Q2任务`
4. 点击 "Run workflow"
5. 等待处理完成
6. 查看飞书群，应该收到反馈！

---

## 📋 步骤6：查看运行日志

### 6.1 查看workflow运行状态

1. 在 **Actions** 标签页
2. 点击任意一个workflow运行记录
3. 点击 "send-review" 或其他job名称
4. 查看详细日志

### 6.2 如果失败了

1. 查看错误日志
2. 常见问题：
   - Secrets配置错误
   - 代码路径问题
   - 依赖安装失败

---

## 🎯 使用说明

### 自动运行时间表

| 功能 | 运行时间 | 说明 |
|------|---------|------|
| 每日复盘 | 每天 22:00 | 自动发送任务清单 |
| 每周报告 | 每周日 21:00 | 发送本周统计 |
| 每月报告 | 每月1号 21:00 | 发送本月统计 |

### 手动处理回复

当你在飞书回复任务更新后：

1. 复制你的回复内容
2. 进入GitHub → Actions → "处理用户回复"
3. 点击 "Run workflow"
4. 粘贴回复内容
5. 点击运行
6. 等待处理完成，查看飞书反馈

---

## 🔧 修改定时时间

如果想修改自动运行时间，编辑对应的workflow文件：

### 修改每日复盘时间

编辑 `.github/workflows/daily_review.yml`：

```yaml
schedule:
  - cron: '0 14 * * *'  # 22:00 北京时间 = 14:00 UTC
```

改成其他时间，例如：
- `0 13 * * *` = 21:00 北京时间
- `0 15 * * *` = 23:00 北京时间

### Cron表达式说明

格式：`分 时 日 月 星期`

- `0 14 * * *` = 每天14:00 UTC（22:00北京时间）
- `0 13 * * 0` = 每周日13:00 UTC（21:00北京时间）
- `0 13 1 * *` = 每月1号13:00 UTC（21:00北京时间）

**注意**：GitHub Actions使用UTC时间，北京时间需要减8小时。

---

## 💡 常见问题

### Q: Workflow没有自动运行？

A: 检查：
1. workflow文件是否在 `.github/workflows/` 目录
2. cron表达式是否正确
3. Actions是否启用
4. 等待时间是否足够（首次可能需要几分钟）

### Q: 手动运行失败？

A: 检查：
1. Secrets是否配置正确
2. 查看运行日志中的错误信息
3. 确认Supabase数据库权限已修复

### Q: 如何停止自动运行？

A: 两种方法：
1. 禁用workflow：Actions → 选择workflow → 右上角 "..." → "Disable workflow"
2. 删除workflow文件：删除 `.github/workflows/` 中对应的yml文件

### Q: 可以修改发送内容吗？

A: 可以！编辑 `scripts/` 目录下的对应Python文件：
- `daily_review.py` - 每日复盘
- `weekly_report.py` - 周报
- `monthly_report.py` - 月报

---

## 🎉 完成！

现在你的AI督导系统已经完全部署到GitHub Actions上了！

### 系统会自动：
- ✅ 每天22:00发送复盘提醒
- ✅ 每周日21:00发送周报
- ✅ 每月1号21:00发送月报

### 你需要做的：
- 📱 在飞书查看提醒和报告
- ✍️ 回复任务更新
- 🖱️ 在GitHub手动触发"处理回复"

---

## 📞 需要帮助？

如果遇到问题：
1. 查看GitHub Actions运行日志
2. 检查Secrets配置
3. 确认Supabase数据库权限
4. 测试飞书webhook是否正常

祝使用愉快！🎉
