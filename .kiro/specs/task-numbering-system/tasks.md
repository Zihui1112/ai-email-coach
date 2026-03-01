# 实施计划：v4.0任务编号系统

## 概述

本计划将v4.0任务编号系统分解为可执行的编码任务。实施重点是数据库迁移、核心函数实现、AI解析器重写和邮件显示优化。所有任务按照依赖关系排序，确保每一步都能在前一步的基础上构建。

## 任务清单

- [x] 1. 数据库迁移和初始化
  - 创建database_update_v4.0.sql文件
  - 添加5个新字段：task_order, display_number, is_deleted, deleted_at, last_reminded_date
  - 创建3个索引：idx_tasks_user_quadrant_order, idx_tasks_is_deleted, idx_tasks_status_deleted
  - 删除所有status='completed'的任务
  - 为现有活跃任务按象限和created_at分配task_order和display_number
  - _需求: 11.1-11.9, 12.1-12.5_

- [x] 2. 实现核心任务查询和编号函数
  - [x] 2.1 实现find_task()函数
    - 根据user_email + quadrant + task_order查找任务
    - 添加is_deleted=FALSE过滤条件
    - 返回任务对象或None
    - _需求: 1.3, 2.5, 13.1_

  - [x] 2.2 实现get_max_task_order()函数
    - 查询指定象限的最大task_order值
    - 仅查询status='active'且is_deleted=FALSE的任务
    - 返回最大值，如果无任务返回0
    - _需求: 6.1_

  - [x] 2.3 实现find_paused_task()函数
    - 根据user_email + task_order查找暂缓任务
    - 添加status='paused'且is_deleted=FALSE过滤条件
    - 返回任务对象或None
    - _需求: 8.1, 13.3_

  - [x] 2.4 实现get_paused_tasks_to_remind()函数
    - 查询需要提醒的暂缓任务
    - 条件：status='paused', is_deleted=FALSE, (last_reminded_date IS NULL OR last_reminded_date <= today - 2天)
    - 按task_order升序排序
    - _需求: 7.6, 17.1-17.5_

- [x] 3. 实现任务重新排序逻辑
  - [x] 3.1 实现reorder_tasks()函数
    - 获取指定象限所有活跃任务（按task_order排序）
    - 重新分配task_order为1, 2, 3...
    - 同步更新display_number为Q{quadrant}-{task_order}
    - 批量更新数据库
    - _需求: 3.1-3.5_

  - [x] 3.2 实现reorder_paused_tasks()函数
    - 获取所有暂缓任务（按task_order排序）
    - 重新分配task_order为1, 2, 3...
    - 批量更新数据库
    - _需求: 7.4, 8.6_

- [x] 4. 实现任务操作函数
  - [x] 4.1 实现complete_task()函数
    - 调用find_task()查找任务
    - 设置is_deleted=TRUE, deleted_at=NOW(), status='completed'
    - 计算经验值奖励（100 - 当前进度）
    - 调用reorder_tasks()重新排序该象限
    - 返回成功结果和奖励信息
    - _需求: 2.1-2.6_

  - [x] 4.2 实现update_task_progress()函数
    - 调用find_task()查找任务
    - 计算进度变化量（new_progress - old_progress）
    - 更新progress_percentage和updated_at
    - 如果new_progress=100%，自动调用complete_task()
    - 计算增量经验值奖励
    - 返回成功结果和奖励信息
    - _需求: 5.1-5.5_

  - [x] 4.3 实现create_task()函数
    - 调用get_max_task_order()获取最大编号
    - 分配task_order = max_order + 1
    - 生成display_number = Q{quadrant}-{task_order}
    - 设置progress_percentage=0, status='active', is_deleted=FALSE
    - 插入数据库
    - 返回成功结果和任务编号
    - _需求: 6.1-6.6_

  - [x] 4.4 实现pause_task()函数
    - 调用find_task()查找任务
    - 设置status='paused', last_reminded_date=today
    - 调用reorder_tasks()重新排序原象限
    - 调用reorder_paused_tasks()重新排序暂缓池
    - 返回成功结果
    - _需求: 7.1-7.5_

  - [x] 4.5 实现resume_paused_task()函数
    - 调用find_paused_task()查找暂缓任务
    - 调用get_max_task_order()获取目标象限最大编号
    - 设置status='active', quadrant=target_quadrant, task_order=max_order+1
    - 生成新的display_number
    - 调用reorder_paused_tasks()重新排序暂缓池
    - 返回成功结果和新编号
    - _需求: 8.1-8.6_

- [x] 5. 检查点 - 核心函数测试
  - 确保所有核心函数正常工作，ask the user if questions arise.

- [x] 6. 重写AI解析器（check_email_reply.py）
  - [x] 6.1 更新AI提示词以支持编号识别
    - 添加编号引用规则：Q1任务1、Q1-1、暂缓任务1
    - 添加6种操作类型识别：complete, update, create, pause, resume, personality_switch
    - 支持两种编号格式：Q1任务1和Q1-1
    - 返回JSON格式：operation_type, quadrant, task_number, task_name, progress
    - _需求: 4.1-4.7, 16.1-16.5_

  - [x] 6.2 实现parse_user_reply()函数
    - 调用DeepSeek API解析用户回复
    - 解析JSON结果
    - 处理多个操作（返回数组）
    - 错误处理：返回友好提示和格式示例
    - _需求: 4.1-4.7, 13.4_

  - [x] 6.3 更新process_operations()函数
    - 遍历解析结果，根据operation_type调用对应函数
    - complete → complete_task()
    - update → update_task_progress()
    - create → create_task()
    - pause → pause_task()
    - resume → resume_paused_task()
    - 收集所有操作结果和奖励
    - _需求: 2.1-2.6, 5.1-5.5, 6.1-6.6, 7.1-7.5, 8.1-8.6_

  - [x] 6.4 更新反馈邮件生成逻辑
    - 使用display_number显示任务编号
    - 显示每个操作的结果（完成/更新/新增/暂缓/恢复）
    - 显示经验值和金币奖励
    - 添加格式示例提示
    - _需求: 4.7, 13.4_

- [x] 7. 重写每日复盘邮件显示（daily_review.py）
  - [x] 7.1 更新任务查询逻辑
    - 查询条件：status='active' AND is_deleted=FALSE
    - 按quadrant ASC, task_order ASC排序
    - 调用get_paused_tasks_to_remind()获取暂缓任务
    - _需求: 9.1, 12.4_

  - [x] 7.2 实现按象限分组显示
    - 按Q1-Q4分组显示任务
    - 每个任务显示：task_order（不含Q前缀）+ 任务名 + 进度条
    - 显示象限经验值倍率
    - 如果象限无任务，显示"（暂无任务）"
    - _需求: 9.1-9.3, 9.7_

  - [x] 7.3 实现暂缓待办池显示
    - 独立分组显示暂缓任务
    - 显示任务编号（暂缓池内的task_order）
    - 显示任务名称
    - 更新显示后，批量更新last_reminded_date为今天
    - _需求: 9.4, 7.7_

  - [x] 7.4 添加回复格式示例
    - 显示6种操作格式：完成、进度、新增、暂缓、恢复、性格切换
    - 支持两种编号格式示例
    - 放在邮件底部
    - _需求: 9.5_

  - [x] 7.5 实现成长进度可视化
    - 显示当前等级、经验值、金币
    - 生成经验进度条（10个方块）
    - 计算经验值百分比
    - 显示连击天数和AI性格
    - _需求: 10.1-10.4_

  - [x] 7.6 实现解锁阶梯显示
    - 显示已解锁功能（LV1, LV3等）
    - 显示未解锁功能及所需等级
    - 计算剩余经验值
    - 估算达到下一解锁所需任务更新次数
    - _需求: 10.5-10.7_

- [x] 8. 检查点 - 集成测试
  - 确保所有功能正常工作，ask the user if questions arise.

- [ ]* 9. 单元测试（可选）
  - [ ]* 9.1 测试任务查询函数
    - 测试find_task()的各种场景
    - 测试get_max_task_order()边界情况
    - 测试find_paused_task()
    - 测试get_paused_tasks_to_remind()提醒逻辑
    - _需求: 1.1-1.5, 6.1-6.6, 7.6, 8.1_

  - [ ]* 9.2 测试任务重新排序
    - 测试reorder_tasks()连续性
    - 测试删除中间任务后的重排序
    - 测试reorder_paused_tasks()
    - _需求: 3.1-3.5_

  - [ ]* 9.3 测试任务操作函数
    - 测试complete_task()软删除和重排序
    - 测试update_task_progress()进度更新和自动完成
    - 测试create_task()编号分配
    - 测试pause_task()和resume_paused_task()
    - _需求: 2.1-2.6, 5.1-5.5, 6.1-6.6, 7.1-7.5, 8.1-8.6_

  - [ ]* 9.4 测试AI解析器
    - 测试6种操作类型识别
    - 测试两种编号格式解析
    - 测试错误处理和友好提示
    - _需求: 4.1-4.7, 16.1-16.5_

- [ ]* 10. 属性测试（可选，使用Hypothesis）
  - [ ]* 10.1 任务编号连续性属性
    - **属性1: 任务编号连续性**
    - **验证: 需求3.2, 3.5**
    - 属性：对于任何象限，删除任意任务后重排序，task_order必须从1开始连续递增
    - 生成策略：随机生成任务列表，随机删除任务，验证重排序结果

  - [ ]* 10.2 软删除不可见属性
    - **属性2: 软删除任务不可见**
    - **验证: 需求2.5**
    - 属性：任何查询活跃任务的操作，返回结果中不包含is_deleted=TRUE的任务
    - 生成策略：随机生成任务列表，随机标记部分为已删除，验证查询结果

  - [ ]* 10.3 暂缓任务提醒间隔属性
    - **属性3: 暂缓任务提醒间隔**
    - **验证: 需求17.1-17.5**
    - 属性：暂缓任务在2天内最多提醒一次
    - 生成策略：随机生成暂缓任务和last_reminded_date，验证get_paused_tasks_to_remind()结果

  - [ ]* 10.4 任务唯一标识属性
    - **属性4: 任务唯一标识**
    - **验证: 需求1.3**
    - 属性：同一用户的同一象限内，task_order必须唯一
    - 生成策略：随机生成任务操作序列，验证任何时刻都不存在重复的task_order

- [x] 11. 创建部署文档
  - 创建v4.0部署指南.md
  - 包含数据库迁移步骤
  - 包含代码部署步骤
  - 包含验证清单
  - 包含回滚方案
  - _需求: 14.1-14.6, 15.1-15.5_

## 注意事项

1. 任务标记"*"的为可选任务，可以跳过以加快MVP交付
2. 每个任务都引用了具体的需求编号，便于追溯
3. 检查点任务确保增量验证，及时发现问题
4. 数据库迁移必须首先完成，其他任务依赖新字段
5. 核心函数实现完成后再进行AI解析器和邮件显示的重写
6. 所有代码使用Python实现，保持与现有系统一致

## 实施优先级

1. 第一优先级：任务1（数据库迁移）
2. 第二优先级：任务2-4（核心函数）
3. 第三优先级：任务6-7（AI解析器和邮件显示）
4. 第四优先级：任务11（部署文档）
5. 可选：任务9-10（测试）
