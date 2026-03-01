# 需求文档：v4.0任务编号系统

## 简介

v4.0任务编号系统旨在解决AI邮件督导系统中"已完成任务反复出现"的核心问题。通过引入任务编号机制，用户可以使用简单的编号（如"Q1任务1"）来操作任务，系统自动管理任务的生命周期，完成的任务立即软删除不再出现，暂缓任务独立管理并定期提醒。同时，系统提供可视化的成长进度展示，包括经验进度条和解锁阶梯。

## 术语表

- **任务编号系统（Task_Numbering_System）**: 为每个任务分配唯一编号的管理系统
- **显示编号（Display_Number）**: 任务的可读编号格式，如"Q1-1"、"Q2-3"
- **任务顺序（Task_Order）**: 任务在其象限内的排序位置（1, 2, 3...）
- **软删除（Soft_Delete）**: 标记任务为已删除但保留数据库记录
- **任务重排序（Task_Reordering）**: 删除或移动任务后自动调整后续任务编号
- **暂缓待办池（Paused_Task_Pool）**: 独立管理的暂缓任务集合
- **提醒间隔（Reminder_Interval）**: 暂缓任务的提醒周期（2天）
- **经验进度条（Experience_Progress_Bar）**: 可视化显示用户当前等级的经验值进度
- **解锁阶梯（Unlock_Ladder）**: 显示各等级解锁功能的进度展示
- **任务唯一标识（Task_Unique_Identifier）**: 由user_email + quadrant + task_order组成的唯一键
- **数据库（Database）**: Supabase PostgreSQL数据库
- **邮件回复处理器（Email_Reply_Processor）**: 解析用户邮件回复的AI组件
- **每日复盘邮件（Daily_Review_Email）**: 每日发送给用户的任务清单邮件
- **游戏化系统（Gamification_System）**: 现有的等级、经验值、金币管理系统

## 需求

### 需求1：任务编号分配

**用户故事**: 作为用户，我希望每个任务都有唯一的编号，这样我可以快速引用任务而不需要输入完整的任务名称。

#### 验收标准

1. WHEN 用户创建新任务，THE Task_Numbering_System SHALL 为该任务分配该象限内的下一个可用编号
2. THE Task_Numbering_System SHALL 使用格式"Q{象限}-{顺序}"生成Display_Number（例如：Q1-1, Q2-3）
3. THE Task_Numbering_System SHALL 确保Task_Unique_Identifier由user_email + quadrant + task_order组成
4. WHEN 查询任务时，THE Task_Numbering_System SHALL 按quadrant升序和task_order升序返回结果
5. THE Task_Numbering_System SHALL 为每个象限独立维护Task_Order序列（从1开始）

### 需求2：任务完成处理

**用户故事**: 作为用户，我希望完成的任务立即消失不再出现，这样我的任务清单始终保持清爽。

#### 验收标准

1. WHEN 用户标记任务完成，THE Task_Numbering_System SHALL 将该任务的is_deleted字段设置为TRUE
2. WHEN 任务被标记完成，THE Task_Numbering_System SHALL 记录deleted_at时间戳
3. WHEN 任务被标记完成，THE Task_Numbering_System SHALL 将status字段更新为'completed'
4. WHEN 任务被软删除后，THE Task_Numbering_System SHALL 触发该象限的Task_Reordering
5. WHEN 查询活跃任务时，THE Database SHALL 排除所有is_deleted为TRUE的任务
6. WHEN 任务完成时，THE Gamification_System SHALL 计算并发放经验值和金币奖励

### 需求3：任务重新排序

**用户故事**: 作为用户，我希望任务编号始终保持连续，这样我可以轻松记住和引用任务。

#### 验收标准

1. WHEN 任务被删除或暂缓，THE Task_Numbering_System SHALL 重新分配该象限内所有后续任务的task_order
2. WHEN 重新排序时，THE Task_Numbering_System SHALL 确保task_order从1开始连续递增
3. WHEN 重新排序时，THE Task_Numbering_System SHALL 同步更新每个任务的display_number
4. THE Task_Numbering_System SHALL 仅对受影响的象限执行重新排序
5. WHEN 重新排序完成后，THE Task_Numbering_System SHALL 确保该象限内不存在编号间隙

### 需求4：用户回复解析

**用户故事**: 作为用户，我希望使用简单的编号命令操作任务，这样我可以快速回复邮件而不需要输入冗长的任务名称。

#### 验收标准

1. WHEN 用户回复包含"Q{象限}任务{编号}完成"，THE Email_Reply_Processor SHALL 识别为完成操作
2. WHEN 用户回复包含"Q{象限}任务{编号}进度{百分比}%"，THE Email_Reply_Processor SHALL 识别为进度更新操作
3. WHEN 用户回复包含"{任务名} Q{象限}"，THE Email_Reply_Processor SHALL 识别为新增任务操作
4. WHEN 用户回复包含"Q{象限}任务{编号}暂缓"，THE Email_Reply_Processor SHALL 识别为暂缓操作
5. WHEN 用户回复包含"暂缓任务{编号}恢复到Q{象限}"，THE Email_Reply_Processor SHALL 识别为恢复操作
6. THE Email_Reply_Processor SHALL 支持"Q1-1"和"Q1任务1"两种编号格式
7. WHEN 解析失败时，THE Email_Reply_Processor SHALL 返回友好的错误提示和格式示例

### 需求5：任务进度更新

**用户故事**: 作为用户，我希望通过编号快速更新任务进度，这样我可以及时记录工作进展。

#### 验收标准

1. WHEN 用户更新任务进度，THE Task_Numbering_System SHALL 根据象限和编号定位唯一任务
2. WHEN 进度更新时，THE Task_Numbering_System SHALL 计算进度变化量（新进度 - 旧进度）
3. WHEN 进度增加时，THE Gamification_System SHALL 根据进度变化量和象限权重计算经验值奖励
4. WHEN 进度更新时，THE Task_Numbering_System SHALL 更新任务的updated_at时间戳
5. IF 进度更新为100%，THEN THE Task_Numbering_System SHALL 自动标记任务为完成

### 需求6：新增任务

**用户故事**: 作为用户，我希望快速添加新任务到指定象限，这样我可以灵活管理我的待办事项。

#### 验收标准

1. WHEN 用户新增任务，THE Task_Numbering_System SHALL 查询目标象限的最大task_order值
2. WHEN 新增任务时，THE Task_Numbering_System SHALL 分配task_order为最大值加1
3. WHEN 新增任务时，THE Task_Numbering_System SHALL 生成对应的display_number
4. THE Task_Numbering_System SHALL 将新任务的progress_percentage初始化为0
5. THE Task_Numbering_System SHALL 将新任务的status设置为'active'
6. THE Task_Numbering_System SHALL 将新任务的is_deleted设置为FALSE

### 需求7：任务暂缓管理

**用户故事**: 作为用户，我希望将暂时无法处理的任务移入暂缓池，并定期收到提醒，这样我不会忘记这些任务。

#### 验收标准

1. WHEN 用户暂缓任务，THE Task_Numbering_System SHALL 将任务status更新为'paused'
2. WHEN 任务被暂缓时，THE Task_Numbering_System SHALL 记录last_reminded_date为当前日期
3. WHEN 任务被暂缓时，THE Task_Numbering_System SHALL 触发原象限的Task_Reordering
4. WHEN 任务被暂缓时，THE Task_Numbering_System SHALL 触发Paused_Task_Pool的重新编号
5. THE Task_Numbering_System SHALL 为暂缓任务分配独立的编号序列（从1开始）
6. WHEN 查询需要提醒的暂缓任务时，THE Database SHALL 返回last_reminded_date为NULL或距今超过2天的任务
7. WHEN 暂缓任务在每日邮件中显示时，THE Task_Numbering_System SHALL 更新其last_reminded_date为当前日期

### 需求8：暂缓任务恢复

**用户故事**: 作为用户，我希望将暂缓的任务恢复到活跃象限，这样我可以重新开始处理这些任务。

#### 验收标准

1. WHEN 用户恢复暂缓任务，THE Task_Numbering_System SHALL 根据暂缓任务编号定位任务
2. WHEN 恢复任务时，THE Task_Numbering_System SHALL 将任务status更新为'active'
3. WHEN 恢复任务时，THE Task_Numbering_System SHALL 更新任务的quadrant为目标象限
4. WHEN 恢复任务时，THE Task_Numbering_System SHALL 分配目标象限的下一个可用task_order
5. WHEN 恢复任务时，THE Task_Numbering_System SHALL 生成新的display_number
6. WHEN 恢复任务后，THE Task_Numbering_System SHALL 触发Paused_Task_Pool的重新编号

### 需求9：每日复盘邮件显示

**用户故事**: 作为用户，我希望每日邮件清晰展示所有任务及其编号，这样我可以快速了解当前状态并使用编号回复。

#### 验收标准

1. THE Daily_Review_Email SHALL 按象限分组显示所有活跃任务
2. THE Daily_Review_Email SHALL 在每个任务前显示其task_order（不含象限前缀）
3. THE Daily_Review_Email SHALL 为每个任务显示进度条（10个方块，已完成用■，未完成用□）
4. THE Daily_Review_Email SHALL 显示需要提醒的暂缓任务（独立分组）
5. THE Daily_Review_Email SHALL 在邮件底部提供回复格式示例
6. THE Daily_Review_Email SHALL 显示每个象限的经验值倍率
7. WHEN 某象限无任务时，THE Daily_Review_Email SHALL 显示"（暂无任务）"

### 需求10：成长进度可视化

**用户故事**: 作为用户，我希望看到我的成长进度和即将解锁的功能，这样我可以保持动力持续使用系统。

#### 验收标准

1. THE Daily_Review_Email SHALL 显示用户当前等级、经验值和金币
2. THE Daily_Review_Email SHALL 显示Experience_Progress_Bar（10个方块表示当前等级进度）
3. THE Daily_Review_Email SHALL 计算并显示经验值百分比（当前经验/升级所需经验）
4. THE Daily_Review_Email SHALL 显示用户的连击天数和AI性格
5. THE Daily_Review_Email SHALL 显示Unlock_Ladder，包含已解锁和未解锁的功能
6. THE Daily_Review_Email SHALL 为未解锁功能显示所需等级和剩余经验值
7. THE Daily_Review_Email SHALL 估算达到下一个解锁所需的任务更新次数

### 需求11：数据库迁移

**用户故事**: 作为系统管理员，我希望安全地将现有数据迁移到新的编号系统，这样用户可以无缝过渡到新版本。

#### 验收标准

1. THE Database SHALL 为tasks表添加task_order字段（INTEGER类型，默认值0）
2. THE Database SHALL 为tasks表添加display_number字段（VARCHAR(10)类型）
3. THE Database SHALL 为tasks表添加is_deleted字段（BOOLEAN类型，默认值FALSE）
4. THE Database SHALL 为tasks表添加deleted_at字段（TIMESTAMP类型）
5. THE Database SHALL 为tasks表添加last_reminded_date字段（DATE类型）
6. WHEN 执行迁移脚本时，THE Database SHALL 删除所有status为'completed'的任务
7. WHEN 执行迁移脚本时，THE Database SHALL 为每个象限的现有任务按created_at升序分配task_order
8. WHEN 执行迁移脚本时，THE Database SHALL 为所有现有任务生成display_number
9. WHEN 执行迁移脚本时，THE Database SHALL 为所有现有任务设置is_deleted为FALSE

### 需求12：任务查询优化

**用户故事**: 作为系统，我需要高效查询任务数据，这样可以快速响应用户请求。

#### 验收标准

1. THE Database SHALL 创建索引：idx_tasks_user_quadrant_order ON tasks(user_email, quadrant, task_order)
2. THE Database SHALL 创建索引：idx_tasks_is_deleted ON tasks(is_deleted)
3. THE Database SHALL 创建索引：idx_tasks_status_deleted ON tasks(status, is_deleted)
4. WHEN 查询活跃任务时，THE Database SHALL 使用WHERE条件：status='active' AND is_deleted=FALSE
5. WHEN 查询暂缓任务时，THE Database SHALL 使用WHERE条件：status='paused' AND is_deleted=FALSE

### 需求13：错误处理

**用户故事**: 作为用户，我希望系统能够优雅地处理错误情况，这样我可以得到清晰的反馈并知道如何修正。

#### 验收标准

1. WHEN 用户引用不存在的任务编号，THE Task_Numbering_System SHALL 返回"任务不存在"错误消息
2. WHEN 用户引用不存在的象限，THE Task_Numbering_System SHALL 返回"无效的象限"错误消息
3. WHEN 用户尝试恢复不存在的暂缓任务，THE Task_Numbering_System SHALL 返回"暂缓任务不存在"错误消息
4. WHEN 解析用户回复失败，THE Email_Reply_Processor SHALL 返回格式示例和建议
5. WHEN 数据库操作失败，THE Task_Numbering_System SHALL 记录错误日志并返回友好的错误消息
6. WHEN 任务重排序失败，THE Task_Numbering_System SHALL 回滚事务并保持数据一致性

### 需求14：系统兼容性

**用户故事**: 作为开发者，我希望新系统不破坏现有功能，这样可以确保平滑升级。

#### 验收标准

1. THE Task_Numbering_System SHALL 保持与现有Gamification_System的完全兼容
2. THE Task_Numbering_System SHALL 继续支持现有的经验值和金币计算逻辑
3. THE Task_Numbering_System SHALL 保持与现有Email_Reply_Processor的集成
4. THE Task_Numbering_System SHALL 保持与现有Daily_Review_Email生成逻辑的集成
5. THE Task_Numbering_System SHALL 保持tasks表的现有字段不变（仅新增字段）
6. THE Task_Numbering_System SHALL 继续支持现有的四象限权重配置

### 需求15：性能要求

**用户故事**: 作为用户，我希望系统响应迅速，这样我可以高效地管理任务。

#### 验收标准

1. WHEN 用户完成任务时，THE Task_Numbering_System SHALL 在2秒内完成软删除和重排序
2. WHEN 用户新增任务时，THE Task_Numbering_System SHALL 在1秒内完成编号分配
3. WHEN 生成每日邮件时，THE Daily_Review_Email SHALL 在5秒内完成所有任务查询和格式化
4. WHEN 解析用户回复时，THE Email_Reply_Processor SHALL 在3秒内完成解析和操作
5. THE Database SHALL 支持单用户至少100个活跃任务的高效查询

## 特殊需求说明

### 解析器和序列化器需求

本系统涉及用户回复的解析，需要特别注意：

**需求16：用户回复解析器**

**用户故事**: 作为系统，我需要准确解析用户的各种回复格式，这样可以正确执行用户的意图。

#### 验收标准

1. THE Email_Reply_Processor SHALL 解析至少6种回复格式（完成、进度、新增、暂缓、恢复、性格切换）
2. WHEN 解析成功时，THE Email_Reply_Processor SHALL 返回包含operation_type、quadrant、task_number等字段的JSON对象
3. WHEN 解析失败时，THE Email_Reply_Processor SHALL 返回包含错误原因和格式示例的JSON对象
4. THE Email_Reply_Processor SHALL 支持中文和英文关键词（如"完成"/"done"）
5. FOR ALL 有效的用户回复，解析后执行操作再生成反馈邮件再解析 SHALL 产生等效的操作结果（往返属性）

### 暂缓任务提醒间隔

**需求17：暂缓任务提醒逻辑**

**用户故事**: 作为用户，我希望暂缓任务每2天提醒一次，这样既不会忘记也不会被过度打扰。

#### 验收标准

1. THE Task_Numbering_System SHALL 计算提醒间隔为：当前日期 - last_reminded_date
2. WHEN 提醒间隔大于等于2天时，THE Daily_Review_Email SHALL 包含该暂缓任务
3. WHEN 暂缓任务在邮件中显示后，THE Task_Numbering_System SHALL 立即更新last_reminded_date
4. WHEN last_reminded_date为NULL时，THE Daily_Review_Email SHALL 包含该暂缓任务（首次提醒）
5. THE Task_Numbering_System SHALL 确保同一暂缓任务在2天内最多提醒一次

## 附录：回复格式示例

用户可以使用以下格式回复邮件：

```
✅ 标记完成：
   Q1任务1完成
   Q1-1完成
   Q1任务1 done

📊 更新进度：
   Q1任务2进度60%
   Q1-2 60%
   Q1任务2 80%

🆕 新增任务：
   答辩准备 Q1
   新增：答辩准备 Q1

⏸️ 暂缓任务：
   Q2任务1暂缓
   Q2-1暂缓
   Q2任务1 pause

🔄 恢复任务：
   暂缓任务1恢复到Q1
   暂缓1恢复Q1

🎭 切换性格：
   切换性格：专业型
   性格：毒舌型
```

## 附录：数据库字段说明

tasks表新增字段：

| 字段名 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| task_order | INTEGER | 0 | 任务在象限内的排序位置 |
| display_number | VARCHAR(10) | NULL | 显示编号（如Q1-1） |
| is_deleted | BOOLEAN | FALSE | 软删除标记 |
| deleted_at | TIMESTAMP | NULL | 删除时间 |
| last_reminded_date | DATE | NULL | 最后提醒日期（暂缓任务） |

## 附录：象限经验值倍率

| 象限 | 名称 | 经验值倍率 |
|------|------|-----------|
| Q1 | 重要且紧急 | 2.0x |
| Q2 | 重要非紧急 | 1.5x |
| Q3 | 紧急非重要 | 1.0x |
| Q4 | 非紧急非重要 | 0.5x |
