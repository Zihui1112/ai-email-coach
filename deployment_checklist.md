# 🚀 GitHub + Railway 部署检查清单

## 📋 部署前准备

### ✅ 必需文件检查
- [ ] `main.py` - 主应用文件
- [ ] `requirements.txt` - Python依赖
- [ ] `railway.json` - Railway配置
- [ ] `Procfile` - 启动命令
- [ ] `.env` - 环境变量（本地测试用）
- [ ] `.gitignore` - Git忽略文件

### ✅ 环境变量准备
确保以下环境变量已配置：
- [ ] `SUPABASE_URL` - Supabase数据库URL
- [ ] `SUPABASE_KEY` - Supabase API密钥
- [ ] `RESEND_API_KEY` - Resend邮件API密钥
- [ ] `DEEPSEEK_API_KEY` - DeepSeek LLM API密钥
- [ ] `EMAIL_163_USERNAME` - 163邮箱用户名（可选）
- [ ] `EMAIL_163_PASSWORD` - 163邮箱密码（可选）

## 🐙 GitHub 步骤

### 1. 创建GitHub仓库
- [ ] 访问 https://github.com
- [ ] 点击 "New repository"
- [ ] 仓库名: `ai-email-coach`
- [ ] 设置为 Public 或 Private
- [ ] **不要**勾选 "Initialize with README"
- [ ] 点击 "Create repository"

### 2. 推送代码
```bash
# 运行部署脚本
python github_railway_deploy.py
```

或手动执行：
```bash
git init
git add .
git commit -m "Initial commit: AI Email Coach system"
git remote add origin https://github.com/你的用户名/ai-email-coach.git
git branch -M main
git push -u origin main
```

## 🚂 Railway 步骤

### 1. 创建Railway项目
- [ ] 访问 https://railway.app
- [ ] 使用GitHub账号登录
- [ ] 点击 "New Project"
- [ ] 选择 "Deploy from GitHub repo"
- [ ] 选择 `ai-email-coach` 仓库

### 2. 配置环境变量
在Railway项目设置中添加：
- [ ] `SUPABASE_URL`
- [ ] `SUPABASE_KEY`
- [ ] `RESEND_API_KEY`
- [ ] `DEEPSEEK_API_KEY`
- [ ] `EMAIL_163_USERNAME` (可选)
- [ ] `EMAIL_163_PASSWORD` (可选)

### 3. 等待部署
- [ ] Railway自动检测Python项目
- [ ] 安装依赖 (`pip install -r requirements.txt`)
- [ ] 启动应用 (`uvicorn main:app --host 0.0.0.0 --port $PORT`)
- [ ] 获取部署URL (例如: `https://your-app.railway.app`)

## 🔗 Webhook 配置

### 1. 配置Resend Webhook
- [ ] 访问 https://resend.com/webhooks
- [ ] 点击 "Create Webhook"
- [ ] 填写信息：
  - Name: `AI Email Coach Webhook`
  - Endpoint URL: `https://your-app.railway.app/inbound-email`
  - Events: 选择 `email.received`
- [ ] 创建后复制 Secret

### 2. 添加Webhook Secret
- [ ] 在Railway环境变量中添加：
  - `RESEND_WEBHOOK_SECRET` = 你的webhook secret

## 🧪 测试验证

### 1. 基础测试
- [ ] 访问 `https://your-app.railway.app/health`
- [ ] 应该返回: `{"status": "healthy"}`
- [ ] 访问 `https://your-app.railway.app/docs`
- [ ] 查看API文档

### 2. 邮件功能测试
- [ ] 发送测试邮件内容：
  ```
  项目文档60%完成，Q1重要紧急
  学习Python30%，Q2重要不紧急
  ```
- [ ] 检查163邮箱是否收到反馈
- [ ] 检查飞书群聊是否收到通知（如果配置了）

### 3. 数据库验证
- [ ] 登录Supabase控制台
- [ ] 检查 `tasks` 表是否有新记录
- [ ] 检查 `user_configs` 表是否有用户配置

## 🎉 部署完成

### 系统功能
- ✅ 邮件接收和解析
- ✅ LLM任务解析
- ✅ 数据库同步
- ✅ 多平台通知
- ✅ 个性化反馈
- ✅ 四象限管理
- ✅ 进度条显示

### 使用方式
1. **发送邮件**到配置的邮箱地址
2. **内容示例**：`项目文档60%完成，Q1重要紧急`
3. **系统自动**解析并更新数据库
4. **接收反馈**邮件和群聊通知

### 故障排除
- **部署失败**：检查Railway日志
- **邮件不发送**：验证环境变量和webhook配置
- **数据库错误**：检查Supabase连接和表结构
- **LLM解析失败**：验证DeepSeek API密钥

---

🎯 **快速开始**: 运行 `python github_railway_deploy.py` 开始部署！