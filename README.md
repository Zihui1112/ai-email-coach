# AI Email Coach

一个完全自动化的任务管理系统，通过邮件和飞书提醒你复盘任务，使用 AI 解析你的回复并自动更新数据库。

## ✨ 核心功能

- 📧 **每日复盘提醒**（22:00）- 自动发送任务清单到邮箱和飞书
- ⏰ **每日跟进提醒**（23:00）- 提醒你尽快回复邮件
- 🤖 **智能邮件解析**（23:30）- AI 自动解析回复并更新数据库
- 📊 **周报月报**（自动生成）- 定期汇总任务完成情况
- ☁️ **云端运行**（24/7）- 无需本地电脑，GitHub Actions 自动执行

## 🚀 快速开始

### 1. 配置 GitHub Secrets

在 GitHub 仓库设置中添加以下 Secrets：

- `SUPABASE_URL` - Supabase 项目 URL
- `SUPABASE_KEY` - Supabase service_role key
- `DEEPSEEK_API_KEY` - DeepSeek AI API key
- `FEISHU_WEBHOOK_URL` - 飞书 Webhook URL
- `EMAIL_163_USERNAME` - 163 邮箱地址
- `EMAIL_163_PASSWORD` - 163 邮箱授权码

### 2. 初始化数据库

在 Supabase 中执行 `database_setup.sql` 创建 tasks 表。

### 3. 开始使用

系统会自动在每天 22:00 发送复盘提醒，你只需要回复邮件即可！

## 📅 每日时间安排

| 时间 | 任务 | 说明 |
|------|------|------|
| 22:00 | 每日复盘提醒 | 发送任务清单，提示复盘和制定计划 |
| 23:00 | 每日跟进提醒 | 提醒尽快回复（如已回复可忽略）|
| 23:30 | 检查邮件回复 | AI 解析回复并更新数据库 |

## 📧 如何回复邮件

**重要**：必须回复标题包含以下内容的邮件：
- 回复：📊 每日复盘提醒
- 回复：📊 每日跟进提醒

**回复示例**：
```
完成了用户登录功能90%，这是Q1任务
明天做数据库设计Q2任务
```

AI 会自动识别任务名称、进度、象限和动作。

## 🛠️ 技术栈

- **后端**: Python 3.10
- **数据库**: Supabase (PostgreSQL)
- **AI**: DeepSeek API
- **通知**: 163 邮箱 + 飞书
- **部署**: GitHub Actions
- **邮件协议**: POP3 + SMTP

## 📂 项目结构

```
ai-email-coach/
├── .github/workflows/     # GitHub Actions 工作流
├── scripts/               # Python 脚本
├── database_setup.sql     # 数据库初始化
├── requirements.txt       # Python 依赖
└── README.md             # 项目说明
```

## 📖 详细文档

- [使用指南.md](使用指南.md) - 完整使用说明
- [完全自动化使用指南.md](完全自动化使用指南.md) - 自动化流程详解

## 🔗 相关链接

- GitHub Actions: https://github.com/Zihui1112/ai-email-coach/actions
- Supabase: https://supabase.com
- DeepSeek API: https://platform.deepseek.com

## 📝 License

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！
