# 修复 GitHub Secrets 配置问题

## 问题诊断

错误信息：`Invalid leading whitespace, reserved character(s), or return character(s) in header value`

这说明你的某个 GitHub Secret 包含了**换行符、空格或其他特殊字符**。

## 解决步骤

### 步骤 1：运行诊断测试

1. 前往 GitHub 仓库：https://github.com/Zihui1112/ai-email-coach
2. 点击 **Actions** 标签
3. 选择 **"测试Secrets配置"** workflow
4. 点击 **"Run workflow"**
5. 查看运行结果，找出哪个 Secret 有问题

### 步骤 2：重新配置有问题的 Secrets

前往 GitHub 仓库设置：
1. 点击 **Settings** 标签
2. 左侧菜单选择 **Secrets and variables** → **Actions**
3. 找到有问题的 Secret，点击 **Update**

### 步骤 3：正确配置每个 Secret

**重要提示**：
- ✅ 直接复制粘贴，不要手动输入
- ✅ 确保没有多余的空格或换行符
- ✅ 从下面的正确值复制

#### SUPABASE_URL
```
https://cnmxhxapwksjczfxugtx.supabase.co
```

#### SUPABASE_KEY
```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNubXhoeGFwd2tzamN6Znh1Z3R4Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njk2NDU1NzYsImV4cCI6MjA4NTIyMTU3Nn0.SN5os0906ICGcLn6rvRGY8H0BZxXxG0tUsgD6gMwqE4
```

#### DEEPSEEK_API_KEY
```
sk-86436af0f3784ea5b99c66e08be29b23
```

#### FEISHU_WEBHOOK_URL
```
https://open.feishu.cn/open-apis/bot/v2/hook/902a2c44-8edc-4cb4-a7cd-c3d935c8ed8c
```

#### EMAIL_163_USERNAME
```
15302814198@163.com
```

### 步骤 4：配置方法

对于每个 Secret：

1. **点击 Update 按钮**
2. **清空现有值**（全选删除）
3. **从上面复制正确的值**
4. **直接粘贴**（Ctrl+V 或 Cmd+V）
5. **不要按回车键！**
6. **直接点击 Update secret 按钮**

### 步骤 5：验证配置

重新配置所有 Secrets 后：

1. 再次运行 **"测试Secrets配置"** workflow
2. 确认所有检查都通过（显示 ✅）
3. 运行 **"每日复盘提醒"** workflow
4. 检查飞书是否收到消息

## 常见错误

### ❌ 错误做法
- 在文本编辑器中编辑后复制（可能引入换行符）
- 手动输入（容易出错）
- 复制时包含了前后的空格
- 按回车键后才点保存

### ✅ 正确做法
- 直接从上面的代码块复制
- 使用浏览器的复制功能
- 粘贴后立即保存，不要按回车
- 确保没有多余的空格

## 如果还是失败

如果按照上述步骤操作后仍然失败，请：

1. **删除所有 Secrets**
   - 在 GitHub Settings → Secrets 中逐个删除

2. **重新创建 Secrets**
   - 点击 **New repository secret**
   - Name: 输入 Secret 名称（如 `SUPABASE_URL`）
   - Value: 粘贴对应的值
   - 点击 **Add secret**

3. **再次测试**
   - 运行 "测试Secrets配置" workflow
   - 确认所有检查通过

## 技术说明

我已经在代码中添加了 `.strip()` 方法来自动清理空格和换行符：

```python
supabase_url = os.getenv("SUPABASE_URL", "").strip()
supabase_key = os.getenv("SUPABASE_KEY", "").strip()
```

这样即使 Secret 中有少量空格，也能自动清理。但最好还是在 GitHub 中正确配置。

## 下一步

配置完成后，运行 **"每日复盘提醒"** workflow，应该就能成功收到飞书消息了！
