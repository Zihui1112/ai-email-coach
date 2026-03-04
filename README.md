# 📧 AI邮件教练

> 一个完全自动化的任务管理系统，通过邮件和AI帮助你管理任务、养成习惯、持续成长

[![GitHub stars](https://img.shields.io/github/stars/Zihui1112/ai-email-coach?style=social)](https://github.com/Zihui1112/ai-email-coach/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/Zihui1112/ai-email-coach?style=social)](https://github.com/Zihui1112/ai-email-coach/network/members)
[![GitHub issues](https://img.shields.io/github/issues/Zihui1112/ai-email-coach)](https://github.com/Zihui1112/ai-email-coach/issues)
[![License](https://img.shields.io/github/license/Zihui1112/ai-email-coach)](LICENSE)

---

## ✨ 核心特性

- 📧 **每日复盘提醒** - 自动发送任务清单到邮箱和飞书
- 🤖 **AI智能解析** - 自动理解你的回复并更新任务
- 🎮 **游戏化系统** - 等级、经验值、金币、连击让任务管理更有趣
- 📊 **四象限管理** - 科学的任务优先级管理方法
- 📈 **成长报告** - 每周、每月自动生成故事化成长报告
- ☁️ **云端运行** - 基于 GitHub Actions，24/7 自动运行
- 🔒 **数据隔离** - 每个用户独立数据库，完全隔离

---

## 🎯 快速开始

### 1. Fork 项目

点击右上角的 `Fork` 按钮，将项目复制到你的 GitHub 账号

### 2. 配置服务

注册以下免费服务：
- [Supabase](https://supabase.com) - 数据库
- [DeepSeek](https://platform.deepseek.com) - AI 解析
- 163 邮箱 - 邮件收发

### 3. 配置 GitHub Secrets

在你的仓库中添加以下 Secrets：
- `SUPABASE_URL`
- `SUPABASE_KEY`
- `DEEPSEEK_API_KEY`
- `EMAIL_163_USERNAME`
- `EMAIL_163_PASSWORD`
- `FEISHU_WEBHOOK_URL`（可选）

### 4. 初始化数据库

在 Supabase SQL Editor 中执行 `database_setup.sql`

### 5. 开始使用

等待今晚 21:30 收到第一封邮件，回复邮件即可管理任务！

📖 **详细步骤请查看** → [部署指南.md](部署指南.md)

---

## 📅 自动化时间表

| 时间 | 任务 | 说明 |
|------|------|------|
| 21:30 | 每日复盘 | 发送任务清单 + 智能提示 |
| 23:00 | 每日跟进 | 提醒尽快回复 |
| 23:30 | 检查回复 | AI 解析并更新任务 |
| 周日 20:00 | 周报 | 故事化成长报告 |
| 月末 20:00 | 月报 | 史诗风格月度总结 |

---

## 💬 使用示例

### 回复邮件管理任务

```
Q1: 1完成; 2进度50%
Q2: 1暂缓
新增：写论文 Q1
暂缓任务1恢复到Q1
```

AI 会自动理解你的意图并更新任务！

---

## 🎮 游戏化系统

### 等级系统
- LV1-20 等级系统
- 完成任务获得经验值
- 不同象限任务经验值倍率不同

### 四象限管理
- Q1 🔴 重要且紧急 (EXP x2.0)
- Q2 🟡 重要非紧急 (EXP x1.5)
- Q3 🔵 紧急非重要 (EXP x1.0)
- Q4 ⚪ 非紧急非重要 (EXP x0.5)

### 金币系统
- 完成任务获得金币
- 购买商店道具（LV13+解锁）
- 提升效率和体验

### 连击系统
- 连续完成 Q1 任务获得连击
- 连续回复邮件获得奖励
- 达到里程碑获得特殊奖励

---

## 📊 功能特性

### 智能提示
根据你的等级显示相关提示和建议

### AI 性格系统
- 🌟 友好型 (LV1+)
- 💼 专业型 (LV4+)
- 🔥 严格型 (LV8+)
- 💀 毒舌型 (LV13+)

### 商店系统 (LV13+)
购买道具提升效率：
- 🛡️ 惩罚减免券
- ⚡ 经验加速卡
- 💰 金币翻倍卡
- 🎯 专注加成卡
- 更多道具...

### 成长报告
- 📖 故事化周报
- 📜 史诗风格月报
- 📊 ASCII 图表可视化
- 💡 智能分析和建议

---

## 🛠️ 技术栈

- **语言**: Python 3.10+
- **数据库**: PostgreSQL (Supabase)
- **AI**: DeepSeek API
- **自动化**: GitHub Actions
- **通知**: SMTP + 飞书 Webhook

---

## 📖 文档

- [部署指南.md](部署指南.md) - 📦 完整部署步骤
- [用户手册.md](用户手册.md) - 📖 功能说明和使用技巧
- [开发文档.md](开发文档.md) - 🛠️ 自定义开发指南

---

## 🔒 数据安全

- ✅ 每个用户独立的 Supabase 数据库
- ✅ 所有密钥存储在 GitHub Secrets
- ✅ 使用 Supabase RLS 行级安全策略
- ✅ 用户之间数据完全隔离
- ✅ 不收集任何用户数据

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

---

## 📝 License

本项目采用 MIT License - 查看 [LICENSE](LICENSE) 文件了解详情

---

## 🌟 Star History

如果这个项目对你有帮助，请给个 Star ⭐️

---

## 📞 联系方式

- 提交 Issue: [GitHub Issues](https://github.com/Zihui1112/ai-email-coach/issues)
- 项目主页: [GitHub](https://github.com/Zihui1112/ai-email-coach)

---

## 🎉 致谢

感谢所有贡献者和使用者！

---

**开始你的成长之旅** → [部署指南.md](部署指南.md)

祝你使用愉快！🚀
