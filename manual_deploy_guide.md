# 🚀 手动部署指南 - GitHub + Railway

## 第1步：配置Git

```bash
# 配置Git用户信息（必须）
git config --global user.email "你的邮箱@163.com"
git config --global user.name "你的名字"

# 验证配置
git config --global user.email
git config --global user.name
```

## 第2步：初始化Git仓库

```bash
# 初始化Git仓库
git init

# 添加所有文件
git add .

# 提交代码
git commit -m "Initial commit: AI Email Coach system"
```

## 第3步：创建GitHub仓库

1. 访问 https://github.com
2. 点击右上角 "+" → "New repository"
3. 仓库名：`ai-email-coach`
4. 选择 Public 或 Private
5. **不要**勾选 "Initialize with README"
6. 点击 "Create repository"

## 第4步：推送代码到GitHub

```bash
# 添加远程仓库（替换为你的GitHub用户名）
git remote add origin https://github.com/你的用户名/ai-email-coach.git

# 推送代码
git branch -M main
git push -u origin main
```

## 第5步：部署到Railway

1. 访问 https://railway.app
2. 使用GitHub账号登录
3. 点击 "New Project"
4. 选择 "Deploy from GitHub repo"
5. 选择 `ai-email-coach` 仓库
6. Railway会自动开始部署

## 第6步：配置环境变量

在Railway项目设置中添加：

```
SUPABASE_URL=https://cnmxhxapwksjczfxugtx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNubXhoeGFwd2tzamN6Znh1Z3R4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk2NDU1NzYsImV4cCI6MjA4NTIyMTU3Nn0.SN5os0906ICGcLn6rvRGY8H0BZxXxG0tUsgD6gMwqE4
RESEND_API_KEY=re_R6y7e69R_xV4WhsUPaMPyEFac1oGg23hE
DEEPSEEK_API_KEY=sk-86436af0f3784ea5b99c66e08be29b23
EMAIL_163_USERNAME=15302814198@163.com
EMAIL_163_PASSWORD=你的163邮箱密码或授权码
```

## 第7步：获取部署URL

部署完成后，Railway会提供一个URL，例如：
`https://your-app-name.railway.app`

## 第8步：配置Resend Webhook

1. 访问 https://resend.com/webhooks
2. 点击 "Create Webhook"
3. 填写：
   - Name: `AI Email Coach Webhook`
   - Endpoint URL: `https://your-app-name.railway.app/inbound-email`
   - Events: 选择 `email.received`
4. 创建后复制Secret
5. 在Railway环境变量中添加：
   `RESEND_WEBHOOK_SECRET=你的webhook_secret`

## 第9步：测试系统

1. 访问 `https://your-app-name.railway.app/health`
2. 应该看到：`{"status": "healthy"}`
3. 发送测试邮件：`项目文档60%完成，Q1重要紧急`
4. 检查163邮箱是否收到反馈

## 🎉 完成！

你的AI邮件督导系统现在已经部署完成，可以通过邮件进行任务管理了！