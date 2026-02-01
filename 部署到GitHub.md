# 部署到GitHub - 详细步骤

## 步骤1：在GitHub创建仓库

1. 打开浏览器，访问 https://github.com
2. 登录你的GitHub账号（如果没有，先注册一个）
3. 点击右上角的 "+" 号，选择 "New repository"
4. 填写信息：
   - Repository name: `ai-email-coach`（或其他你喜欢的名字）
   - Description: `AI邮件督导系统`
   - 选择 **Public**（公开）或 **Private**（私有）
   - **不要**勾选 "Initialize this repository with a README"
   - 点击 "Create repository"

5. 创建后，GitHub会显示一个页面，复制仓库地址，类似：
   ```
   https://github.com/你的用户名/ai-email-coach.git
   ```

## 步骤2：推送代码到GitHub

打开命令行（在当前项目目录），运行：

```bash
# 添加远程仓库（替换成你的实际地址）
git remote add origin https://github.com/你的用户名/ai-email-coach.git

# 推送代码
git push -u origin master
```

如果提示需要登录，输入你的GitHub用户名和密码（或Personal Access Token）。

## 步骤3：配置GitHub Secrets

1. 在GitHub仓库页面，点击 **Settings**（设置）
2. 左侧菜单找到 **Secrets and variables** → **Actions**
3. 点击 **New repository secret**
4. 依次添加以下5个secrets：

### Secret 1: SUPABASE_URL
- Name: `SUPABASE_URL`
- Value: `https://cnmxhxapwksjczfxugtx.supabase.co`

### Secret 2: SUPABASE_KEY
- Name: `SUPABASE_KEY`
- Value: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNubXhoeGFwd2tzamN6Znh1Z3R4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk2NDU1NzYsImV4cCI6MjA4NTIyMTU3Nn0.SN5os0906ICGcLn6rvRGY8H0BZxXxG0tUsgD6gMwqE4`

### Secret 3: DEEPSEEK_API_KEY
- Name: `DEEPSEEK_API_KEY`
- Value: `sk-86436af0f3784ea5b99c66e08be29b23`

### Secret 4: FEISHU_WEBHOOK_URL
- Name: `FEISHU_WEBHOOK_URL`
- Value: `https://open.feishu.cn/open-apis/bot/v2/hook/902a2c44-8edc-4cb4-a7cd-c3d935c8ed8c`

### Secret 5: EMAIL_163_USERNAME
- Name: `EMAIL_163_USERNAME`
- Value: `15302814198@163.com`

## 步骤4：测试GitHub Actions

1. 在GitHub仓库页面，点击 **Actions** 标签
2. 你会看到 "每日复盘提醒" workflow
3. 点击该workflow
4. 点击右侧的 **Run workflow** 按钮
5. 选择 `master` 分支
6. 点击绿色的 **Run workflow** 按钮
7. 等待30秒左右
8. 查看你的飞书群，应该会收到消息！

## 步骤5：查看运行日志

1. 在Actions页面，点击刚才运行的workflow
2. 点击 "send-review" job
3. 查看详细日志，确认是否成功

## 常见问题

### Q: 推送时提示需要密码，但我输入密码后还是失败？

A: GitHub已经不支持密码登录了，需要使用Personal Access Token：

1. 访问 https://github.com/settings/tokens
2. 点击 "Generate new token" → "Generate new token (classic)"
3. 勾选 `repo` 权限
4. 生成token并复制
5. 推送时，用户名输入你的GitHub用户名，密码输入这个token

### Q: 如何修改定时时间？

A: 编辑 `.github/workflows/daily_review.yml` 文件，修改cron表达式：

```yaml
schedule:
  - cron: '0 14 * * *'  # 22:00 北京时间 = 14:00 UTC
```

改成其他时间，例如：
- `0 13 * * *` = 21:00 北京时间
- `0 15 * * *` = 23:00 北京时间

### Q: GitHub Actions没有自动运行？

A: 检查：
1. workflow文件是否在 `.github/workflows/` 目录下
2. 文件格式是否正确（YAML格式）
3. 是否已经推送到GitHub
4. 仓库的Actions是否启用（Settings → Actions → 允许所有actions）

---

## 🎉 完成！

配置完成后，系统会：
- ✅ 每天22:00自动发送复盘提醒到飞书
- ✅ 你可以随时手动触发workflow测试
- ✅ 完全免费，无需维护

---

## 下一步：处理用户回复

当你在飞书回复任务更新后，有两种方式处理：

### 方式1：手动触发GitHub Actions

1. 复制你在飞书的回复内容
2. 进入GitHub Actions页面
3. 手动运行workflow
4. （需要创建一个接收输入的workflow）

### 方式2：使用简单网页

我可以帮你创建一个简单的HTML页面：
- 输入你的飞书回复
- 点击提交
- 自动触发GitHub Actions处理

你想用哪种方式？
