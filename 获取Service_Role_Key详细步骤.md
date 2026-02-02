# 获取 Supabase Service Role Key - 详细步骤

## 当前问题

你的 anon key 在本地可以工作，但在 GitHub Actions 中被拒绝（401 错误）。

**必须使用 service_role key 才能在 GitHub Actions 中正常工作。**

---

## 详细操作步骤

### 步骤 1：登录 Supabase

1. 打开浏览器，访问：**https://supabase.com/dashboard**
2. 使用你的账号登录
3. 你会看到项目列表

### 步骤 2：选择项目

1. 找到你的项目：**cnmxhxapwksjczfxugtx**
2. 点击进入项目

### 步骤 3：进入 API 设置页面

1. 在项目页面，查看左侧菜单栏
2. 找到并点击 **Settings**（设置）图标（通常是齿轮图标）
3. 在 Settings 子菜单中，点击 **API**

### 步骤 4：找到 Service Role Key

在 API 页面，你会看到 **Project API keys** 部分，包含两个 key：

#### 1. anon (public)
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNubXhoeGFwd2tzamN6Znh1Z3R4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk2NDU1NzYsImV4cCI6MjA4NTIyMTU3Nn0.SN5os0906ICGcLn6rvRGY8H0BZxXxG0tUsgD6gMwqE4
```
- 这是你当前使用的 key
- ❌ 在 GitHub Actions 中不工作

#### 2. service_role (secret) ⚠️
```
[点击 "Reveal" 或 "Show" 按钮显示]
```
- 这是我们需要的 key
- ✅ 在 GitHub Actions 中可以工作
- ⚠️ 默认是隐藏的，需要点击按钮显示

### 步骤 5：显示并复制 Service Role Key

1. 找到 **service_role** 那一行
2. 点击右侧的 **"Reveal"** 或 **"Show"** 按钮
3. 完整的 key 会显示出来（以 `eyJ` 开头，很长的字符串）
4. 点击 **"Copy"** 按钮，或者手动全选复制整个 key

**重要提示**：
- ✅ 确保复制了完整的 key（从头到尾）
- ✅ 不要包含任何空格或换行符
- ✅ key 应该以 `eyJ` 开头

### 步骤 6：更新 GitHub Secret

1. 打开新标签页，访问：**https://github.com/Zihui1112/ai-email-coach/settings/secrets/actions**
2. 找到 **SUPABASE_KEY**
3. 点击右侧的 **"Update"** 按钮
4. 在 **Value** 输入框中：
   - 先清空现有内容（全选删除）
   - 粘贴刚才复制的 service_role key
   - **不要按回车键！**
5. 直接点击 **"Update secret"** 按钮保存

### 步骤 7：更新本地 .env 文件（可选）

如果你也想在本地使用 service_role key：

1. 打开 `.env` 文件
2. 找到这一行：
   ```
   SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNubXhoeGFwd2tzamN6Znh1Z3R4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk2NDU1NzYsImV4cCI6MjA4NTIyMTU3Nn0.SN5os0906ICGcLn6rvRGY8H0BZxXxG0tUsgD6gMwqE4
   ```
3. 替换为新的 service_role key：
   ```
   SUPABASE_KEY=你的service_role_key
   ```
4. 保存文件

### 步骤 8：测试

1. 前往 GitHub 仓库：**https://github.com/Zihui1112/ai-email-coach**
2. 点击 **Actions** 标签
3. 选择 **"每日复盘提醒"** workflow
4. 点击 **"Run workflow"** 按钮
5. 选择 **main** 分支
6. 点击 **"Run workflow"** 确认

等待约 30 秒，你应该会在飞书收到消息！

---

## 如何识别 Service Role Key

Service role key 的特征：
- ✅ 以 `eyJ` 开头
- ✅ 长度通常在 200-300 字符
- ✅ JWT payload 中包含 `"role":"service_role"`
- ✅ 在 Supabase 控制台中标记为 "secret" 或有警告图标

Anon key 的特征：
- 以 `eyJ` 开头
- 长度通常在 200-300 字符
- JWT payload 中包含 `"role":"anon"`
- 在 Supabase 控制台中标记为 "public"

---

## 常见问题

### Q: 找不到 service_role key？
A: 
1. 确认你在正确的项目中
2. 确认你在 Settings → API 页面
3. 向下滚动，service_role key 通常在 anon key 下方
4. 可能需要点击 "Show" 或 "Reveal" 按钮

### Q: 复制后还是 401 错误？
A: 
1. 检查是否复制了完整的 key
2. 检查是否有多余的空格或换行符
3. 尝试删除 GitHub Secret 后重新创建
4. 确认复制的是 service_role key，不是 anon key

### Q: 本地测试成功，GitHub Actions 失败？
A: 
这是正常的，因为：
- 本地环境可能没有网络限制
- GitHub Actions 环境更严格
- 必须使用 service_role key

---

## 安全提示

⚠️ **service_role key 拥有完全的数据库访问权限**

请务必：
- ✅ 只在服务端使用（GitHub Actions、后端代码）
- ✅ 不要在前端代码中使用
- ✅ 不要提交到公开的代码仓库
- ✅ 只存储在 GitHub Secrets 和本地 .env 文件中
- ✅ 不要分享给他人

---

## 完成后

更新 service_role key 后，你的系统将能够：
- ✅ 在 GitHub Actions 中成功查询数据库
- ✅ 每天 22:00 自动发送复盘提醒到飞书
- ✅ 每周日 21:00 自动发送周报
- ✅ 每月1号 21:00 自动发送月报
- ✅ 24/7 云端运行，无需本地电脑

祝顺利！🚀
