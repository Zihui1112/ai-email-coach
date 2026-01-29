# AI邮件督导系统

一个通过邮件交互的智能任务管理和督导系统。用户可以通过发送邮件来更新任务进度，系统会使用AI分析用户的自然语言输入，自动更新任务状态，并根据用户配置的个性化风格发送反馈邮件。

## 🚀 核心功能

- **邮件交互**: 通过回复邮件更新任务进度，支持自然语言输入
- **AI解析**: 使用DeepSeek LLM智能解析用户意图和任务信息
- **四象限管理**: 基于重要性和紧急性的任务分类（Q1-Q4）
- **个性化反馈**: 支持毒舌/暖心两种督导风格
- **防抖机制**: 10分钟内多封邮件只处理最后一封
- **计划修改限制**: 每日最多修改2次计划，培养执行力
- **ASCII进度条**: 直观显示任务完成情况
- **待办池管理**: 智能推荐暂缓的任务

## 🛠 技术栈

- **后端框架**: FastAPI (Python)
- **数据库**: Supabase (PostgreSQL)
- **邮件服务**: Resend
- **AI模型**: DeepSeek LLM
- **部署**: 支持Docker容器化

## 📦 安装和配置

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd ai-email-coach
```

### 2. 创建虚拟环境

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入以下配置：

```env
# Supabase配置
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-supabase-anon-key

# Resend邮件服务配置
RESEND_API_KEY=re_your-resend-api-key
RESEND_WEBHOOK_SECRET=your-webhook-secret

# DeepSeek LLM配置
DEEPSEEK_API_KEY=sk-your-deepseek-api-key
```

### 5. 设置数据库

在Supabase控制台中执行 `database_setup.sql` 脚本创建所需的表结构。

### 6. 配置Resend Webhook

在Resend控制台中配置webhook：
- URL: `https://your-domain.com/inbound-email`
- 事件: `email.received`

## 🚀 运行应用

### 开发环境

```bash
python main.py
```

或使用uvicorn：

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 生产环境

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 📧 使用方法

### 1. 初始设置

首先发送邮件到系统邮箱，系统会自动为你创建用户配置。

### 2. 更新任务进度

发送邮件内容示例：

```
项目文档写了60%，属于Q1重要紧急
学习Python进度30%，Q2重要不紧急
回复客户邮件80%完成，Q3象限
```

### 3. 修改计划

```
我想调整一下计划，把学习Python改到Q1，进度提升到50%
```

### 4. 暂缓任务

```
整理桌面这个任务先暂缓吧，以后再说
```

### 5. 个性化设置

系统支持两种督导风格：
- **毒舌模式**: 犀利语气，对拖延行为进行反讽
- **暖心模式**: 温柔语气，提供温暖的建议和鼓励

## 🎯 四象限说明

- **Q1 (重要紧急)**: 危机处理、紧急问题
- **Q2 (重要不紧急)**: 预防、能力建设、计划
- **Q3 (不重要紧急)**: 打断、某些电话、邮件
- **Q4 (不重要不紧急)**: 浪费时间、娱乐活动

## 📊 邮件反馈示例

```
📊 任务进度更新：

• 项目文档
  进度：[■■■■■■□□□□] 60%

🎯 明日四象限清单：

Q1 重要紧急：
• 项目文档
  进度：[■■■■■■□□□□] 60%

Q2 重要不紧急：
• 学习Python
  进度：[■■■□□□□□□□] 30%

📝 待办池推荐：
• 整理桌面 - 要重新开始吗？

继续努力，保持专注！

---
回复此邮件更新你的任务进度吧！
```

## 🔧 API接口

### POST /inbound-email
接收Resend webhook的入站邮件

### GET /health
健康检查接口

### GET /
系统状态接口

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_llm_parser.py

# 生成覆盖率报告
pytest --cov=main --cov-report=html
```

## 📝 开发计划

- [ ] 添加每日复盘功能
- [ ] 实现周度/月度统计报告
- [ ] 支持任务优先级排序
- [ ] 添加任务提醒功能
- [ ] 实现多语言支持
- [ ] 添加Web管理界面

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

## 📞 支持

如有问题，请提交Issue或联系开发者。