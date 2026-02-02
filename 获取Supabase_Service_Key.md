# 获取 Supabase Service Role Key

## 问题原因

当前错误：`❌ 数据库查询失败: 401`

这是因为你使用的是 **anon key**（匿名密钥），但由于我们禁用了 RLS（Row Level Security），需要使用 **service_role key**（服务端密钥）才能访问数据库。

## 解决步骤

### 步骤 1：登录 Supabase

1. 访问：https://supabase.com/dashboard
2. 登录你的账号
3. 选择你的项目：`cnmxhxapwksjczfxugtx`

### 步骤 2：获取 Service Role Key

1. 在项目页面，点击左侧菜单的 **Settings**（设置）图标
2. 选择 **API** 选项
3. 找到 **Project API keys** 部分
4. 你会看到两个 key：
   - **anon public**（当前使用的，不够权限）
   - **service_role**（需要使用这个）⚠️ Secret

5. 点击 **service_role** 旁边的 **Reveal** 按钮
6. 复制完整的 key（以 `eyJ` 开头的长字符串）

### 步骤 3：更新 GitHub Secret

1. 前往 GitHub 仓库：https://github.com/Zihui1112/ai-email-coach
2. 点击 **Settings** 标签
3. 左侧菜单选择 **Secrets and variables** → **Actions**
4. 找到 **SUPABASE_KEY**
5. 点击 **Update**
6. 粘贴新的 **service_role key**
7. 点击 **Update secret**

### 步骤 4：更新本地 .env 文件

同时也要更新本地的 `.env` 文件：

```env
SUPABASE_KEY=你的service_role_key
```

### 步骤 5：测试

更新后，重新运行 GitHub Actions 的 **"每日复盘提醒"** workflow，应该就能成功了！

## 两种 Key 的区别

| Key 类型 | 用途 | 权限 |
|---------|------|------|
| **anon** | 前端/客户端使用 | 受 RLS 策略限制 |
| **service_role** | 后端/服务端使用 | 完全访问权限，绕过 RLS |

由于我们禁用了 RLS，必须使用 **service_role key**。

## 安全提示

⚠️ **service_role key** 拥有完全的数据库访问权限，请：
- ✅ 只在服务端使用（GitHub Actions、后端代码）
- ✅ 不要在前端代码中使用
- ✅ 不要提交到公开的代码仓库
- ✅ 只存储在 GitHub Secrets 和本地 .env 文件中

## 如果找不到 Service Role Key

如果在 Supabase 控制台找不到 service_role key：

1. 确认你已经登录正确的账号
2. 确认选择了正确的项目
3. 在 Settings → API 页面向下滚动
4. service_role key 通常在 anon key 下方
5. 可能需要点击 "Reveal" 或 "Show" 按钮才能看到

## 完成后

更新 key 后，系统应该能够：
- ✅ 成功查询数据库
- ✅ 发送每日复盘提醒到飞书
- ✅ 生成周报和月报
- ✅ 处理任务更新

祝顺利！🚀
