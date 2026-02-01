"""
AI邮件督导系统 - 主应用文件
通过邮件交互实现智能任务管理和督导
"""

import os
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum

import uvicorn
from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, validator
import httpx
from supabase import create_client, Client
from notification_manager import notification_manager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 环境变量配置
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
RESEND_API_KEY = os.getenv("RESEND_API_KEY")
RESEND_WEBHOOK_SECRET = os.getenv("RESEND_WEBHOOK_SECRET")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

# 数据模型
class TaskStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    BACKLOG = "backlog"

class Persona(str, Enum):
    TOXIC = "toxic"
    WARM = "warm"
    NEUTRAL = "neutral"

@dataclass
class TaskUpdate:
    task_name: str
    progress_percentage: Optional[int] = None
    quadrant: Optional[int] = None
    action: str = "update"  # 'update', 'create', 'backlog'

@dataclass
class ParseResult:
    task_updates: List[TaskUpdate]
    is_plan_modification: bool = False
    is_backlog_request: bool = False
    confidence_score: float = 0.8

class EmailData(BaseModel):
    from_email: EmailStr
    subject: str
    content: str
    received_at: datetime
    message_id: str

class Task(BaseModel):
    id: Optional[str] = None
    user_email: EmailStr
    task_name: str
    progress_percentage: int = 0
    quadrant: Optional[int] = None
    status: TaskStatus = TaskStatus.ACTIVE
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    stalled_days: int = 0

class UserConfig(BaseModel):
    user_email: EmailStr
    persona: Persona = Persona.NEUTRAL
    daily_edit_count: int = 0
    max_daily_edits: int = 2
    timezone: str = "UTC"

# 初始化FastAPI应用
app = FastAPI(title="AI邮件督导系统", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化Supabase客户端
try:
    if SUPABASE_URL and SUPABASE_KEY:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        logger.info("✅ Supabase客户端初始化成功")
    else:
        logger.error("❌ Supabase配置缺失")
        supabase = None
except Exception as e:
    logger.error(f"❌ Supabase客户端初始化失败: {e}")
    supabase = None

# 邮件防抖器
class EmailDebouncer:
    def __init__(self):
        self.pending_emails: Dict[str, Dict] = {}
    
    async def should_process_email(self, user_email: str, email_id: str) -> bool:
        """检查是否应该处理邮件（防抖机制）"""
        current_time = datetime.utcnow()
        
        if user_email in self.pending_emails:
            last_email = self.pending_emails[user_email]
            time_diff = (current_time - last_email["timestamp"]).total_seconds()
            
            if time_diff < 10:  # 测试时改为10秒，生产环境改回600
                # 取消之前的处理任务
                last_email["cancelled"] = True
                logger.info(f"取消处理用户 {user_email} 的上一封邮件")
        
        # 记录新邮件
        self.pending_emails[user_email] = {
            "email_id": email_id,
            "timestamp": current_time,
            "cancelled": False
        }
        
        # 等待10分钟，如果期间没有新邮件则处理
        await asyncio.sleep(10)  # 测试时改为10秒，生产环境改回600
        
        # 检查是否被取消
        if self.pending_emails.get(user_email, {}).get("cancelled", True):
            return False
        
        return True

# LLM解析器
class LLMParser:
    def __init__(self):
        self.deepseek_url = "https://api.deepseek.com/v1/chat/completions"
    
    async def parse_reply(self, email_content: str, user_email: str) -> ParseResult:
        """使用DeepSeek LLM解析用户邮件内容"""
        
        prompt = f"""
你是一个任务管理助手，需要从用户的邮件中提取任务信息。

用户邮件内容：
{email_content}

请分析邮件内容，提取以下信息并以JSON格式返回：
{{
    "task_updates": [
        {{
            "task_name": "任务名称",
            "progress_percentage": 进度百分比(0-100),
            "quadrant": 象限分类(1-4),
            "action": "update/create/backlog"
        }}
    ],
    "is_plan_modification": 是否在修改计划(true/false),
    "is_backlog_request": 是否要求暂缓任务(true/false),
    "confidence_score": 解析置信度(0-1)
}}

象限说明：
Q1(1): 重要且紧急
Q2(2): 重要但不紧急  
Q3(3): 不重要但紧急
Q4(4): 不重要且不紧急

暂缓关键词：暂缓、以后再说、先放一放、不急等
修改计划关键词：改变计划、重新安排、调整任务等
"""

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.deepseek_url,
                    headers={
                        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "deepseek-chat",
                        "messages": [
                            {"role": "user", "content": prompt}
                        ],
                        "temperature": 0.1
                    }
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    
                    # 尝试解析JSON
                    try:
                        parsed_data = json.loads(content)
                        task_updates = [TaskUpdate(**task) for task in parsed_data["task_updates"]]
                        
                        return ParseResult(
                            task_updates=task_updates,
                            is_plan_modification=parsed_data.get("is_plan_modification", False),
                            is_backlog_request=parsed_data.get("is_backlog_request", False),
                            confidence_score=parsed_data.get("confidence_score", 0.8)
                        )
                    except json.JSONDecodeError:
                        logger.error(f"LLM返回的JSON格式无效: {content}")
                        return ParseResult(task_updates=[], confidence_score=0.0)
                
                else:
                    logger.error(f"DeepSeek API调用失败: {response.status_code}")
                    return ParseResult(task_updates=[], confidence_score=0.0)
                    
        except Exception as e:
            logger.error(f"LLM解析出错: {str(e)}")
            return ParseResult(task_updates=[], confidence_score=0.0)

# 数据库同步器
class DatabaseSyncer:
    async def sync_task_updates(self, updates: List[TaskUpdate], user_email: str) -> None:
        """同步任务更新到数据库"""
        try:
            for update in updates:
                if update.action == "create":
                    await self.create_new_task(update, user_email)
                elif update.action == "update":
                    await self.update_existing_task(update, user_email)
                elif update.action == "backlog":
                    await self.move_to_backlog(update.task_name, user_email)
                    
        except Exception as e:
            logger.error(f"数据库同步失败: {str(e)}")
            raise
    
    async def create_new_task(self, task: TaskUpdate, user_email: str) -> Task:
        """创建新任务"""
        if not supabase:
            raise Exception("Supabase客户端未初始化")
            
        task_data = {
            "user_email": user_email,
            "task_name": task.task_name,
            "progress_percentage": task.progress_percentage or 0,
            "quadrant": task.quadrant,
            "status": TaskStatus.ACTIVE.value,
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        result = supabase.table("tasks").insert(task_data).execute()
        logger.info(f"创建新任务: {task.task_name} for {user_email}")
        return Task(**result.data[0])
    
    async def update_existing_task(self, task: TaskUpdate, user_email: str) -> Task:
        """更新现有任务"""
        update_data = {"updated_at": datetime.utcnow().isoformat()}
        
        if task.progress_percentage is not None:
            update_data["progress_percentage"] = task.progress_percentage
            # 如果进度达到100%，标记为完成
            if task.progress_percentage == 100:
                update_data["status"] = TaskStatus.COMPLETED.value
        
        if task.quadrant is not None:
            update_data["quadrant"] = task.quadrant
        
        result = supabase.table("tasks").update(update_data).eq(
            "user_email", user_email
        ).eq("task_name", task.task_name).execute()
        
        if result.data:
            logger.info(f"更新任务: {task.task_name} for {user_email}")
            return Task(**result.data[0])
        else:
            # 任务不存在，创建新任务
            return await self.create_new_task(task, user_email)
    
    async def move_to_backlog(self, task_name: str, user_email: str) -> None:
        """将任务移入待办池"""
        supabase.table("tasks").update({
            "status": TaskStatus.BACKLOG.value,
            "updated_at": datetime.utcnow().isoformat()
        }).eq("user_email", user_email).eq("task_name", task_name).execute()
        
        logger.info(f"任务移入待办池: {task_name} for {user_email}")
    
    async def check_daily_edit_limit(self, user_email: str) -> bool:
        """检查每日编辑次数限制"""
        result = supabase.table("user_configs").select("daily_edit_count, max_daily_edits").eq(
            "user_email", user_email
        ).execute()
        
        if result.data:
            config = result.data[0]
            return config["daily_edit_count"] >= config["max_daily_edits"]
        
        return False
    
    async def increment_daily_edit_count(self, user_email: str) -> None:
        """增加每日编辑次数"""
        # 先尝试更新
        result = supabase.table("user_configs").select("daily_edit_count").eq(
            "user_email", user_email
        ).execute()
        
        if result.data:
            new_count = result.data[0]["daily_edit_count"] + 1
            supabase.table("user_configs").update({
                "daily_edit_count": new_count,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("user_email", user_email).execute()
        else:
            # 创建新用户配置
            supabase.table("user_configs").insert({
                "user_email": user_email,
                "daily_edit_count": 1,
                "persona": Persona.NEUTRAL.value,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }).execute()

# 邮件生成器
class EmailGenerator:
    async def generate_feedback_email(self, user_email: str, updates: List[TaskUpdate]) -> str:
        """生成反馈邮件"""
        # 获取用户配置
        user_config = await self.get_user_config(user_email)
        
        # 获取用户所有任务
        tasks = await self.get_user_tasks(user_email)
        
        # 生成邮件内容
        email_content = await self.format_email_content(user_config, tasks, updates)
        
        return email_content
    
    async def get_user_config(self, user_email: str) -> UserConfig:
        """获取用户配置"""
        result = supabase.table("user_configs").select("*").eq(
            "user_email", user_email
        ).execute()
        
        if result.data:
            return UserConfig(**result.data[0])
        else:
            # 创建默认配置
            default_config = {
                "user_email": user_email,
                "persona": Persona.NEUTRAL.value,
                "daily_edit_count": 0,
                "max_daily_edits": 2,
                "timezone": "UTC"
            }
            supabase.table("user_configs").insert(default_config).execute()
            return UserConfig(**default_config)
    
    async def get_user_tasks(self, user_email: str) -> List[Task]:
        """获取用户任务列表"""
        result = supabase.table("tasks").select("*").eq(
            "user_email", user_email
        ).eq("status", TaskStatus.ACTIVE.value).execute()
        
        return [Task(**task) for task in result.data]
    
    async def format_progress_bar(self, progress: int) -> str:
        """格式化进度条"""
        filled = int(progress / 10)
        empty = 10 - filled
        bar = "■" * filled + "□" * empty
        return f"进度：[{bar}] {progress}%"
    
    async def format_email_content(self, config: UserConfig, tasks: List[Task], updates: List[TaskUpdate]) -> str:
        """格式化邮件内容"""
        # 根据persona调整语气
        if config.persona == Persona.TOXIC:
            greeting = "又来汇报了？看看你这次又搞砸了什么..."
            encouragement = "别总是半途而废，坚持一下会死吗？"
        elif config.persona == Persona.WARM:
            greeting = "亲爱的，感谢你的更新！让我们一起看看你的进展～"
            encouragement = "你已经做得很棒了，继续保持这个节奏！"
        else:
            greeting = "收到你的任务更新，以下是当前状态："
            encouragement = "继续努力，保持专注！"
        
        content = f"""
{greeting}

📊 任务进度更新：
"""
        
        # 显示更新的任务
        for update in updates:
            if update.progress_percentage is not None:
                progress_bar = await self.format_progress_bar(update.progress_percentage)
                content += f"• {update.task_name}\n  {progress_bar}\n"
        
        content += "\n🎯 明日四象限清单：\n"
        
        # 按象限分类显示任务
        quadrants = {1: "Q1 重要紧急", 2: "Q2 重要不紧急", 3: "Q3 不重要紧急", 4: "Q4 不重要不紧急"}
        
        for q_num, q_name in quadrants.items():
            q_tasks = [t for t in tasks if t.quadrant == q_num and t.status == TaskStatus.ACTIVE]
            if q_tasks:
                content += f"\n{q_name}：\n"
                for task in q_tasks:
                    progress_bar = await self.format_progress_bar(task.progress_percentage)
                    content += f"• {task.task_name}\n  {progress_bar}\n"
        
        # 待办池推荐
        backlog_tasks = await self.get_backlog_recommendations(config.user_email)
        if backlog_tasks:
            content += "\n📝 待办池推荐：\n"
            for task in backlog_tasks[:2]:  # 只推荐2个
                content += f"• {task.task_name} - 要重新开始吗？\n"
        
        content += f"\n{encouragement}\n\n---\n回复此邮件更新你的任务进度吧！"
        
        return content
    
    async def get_backlog_recommendations(self, user_email: str) -> List[Task]:
        """获取待办池推荐"""
        result = supabase.table("tasks").select("*").eq(
            "user_email", user_email
        ).eq("status", TaskStatus.BACKLOG.value).limit(3).execute()
        
        return [Task(**task) for task in result.data]
    
    async def generate_daily_review_email(self, user_email: str, tasks: List[Task]) -> str:
        """生成每日复盘邮件"""
        config = await self.get_user_config(user_email)
        
        if config.persona == Persona.TOXIC:
            greeting = "又到了每日复盘时间，看看你今天都干了些什么..."
        elif config.persona == Persona.WARM:
            greeting = "亲爱的，辛苦了一天！让我们一起回顾今天的成果吧～"
        else:
            greeting = "今日复盘时间，请回顾你的任务完成情况："
        
        content = f"""
{greeting}

📊 今日任务清单：
"""
        
        completed_count = 0
        total_count = len(tasks)
        
        for task in tasks:
            progress_bar = await self.format_progress_bar(task.progress_percentage)
            status_icon = "✅" if task.progress_percentage == 100 else "⏳"
            content += f"{status_icon} {task.task_name}\n   {progress_bar}\n"
            
            if task.progress_percentage == 100:
                completed_count += 1
        
        completion_rate = (completed_count / total_count * 100) if total_count > 0 else 0
        
        content += f"\n📈 完成率: {completion_rate:.0f}% ({completed_count}/{total_count})\n"
        
        content += "\n💭 请回复此邮件告诉我：\n"
        content += "1. 今天完成了哪些任务？进度如何？\n"
        content += "2. 明天计划做什么？\n"
        content += "3. 有哪些任务需要暂缓到待办池？\n"
        
        return content
    
    async def generate_weekly_report(self, user_email: str, week_tasks: List[Task]) -> str:
        """生成周度统计报告"""
        config = await self.get_user_config(user_email)
        
        if config.persona == Persona.TOXIC:
            greeting = "一周又过去了，来看看你这周的战绩如何..."
        elif config.persona == Persona.WARM:
            greeting = "这一周你辛苦了！让我们一起看看你的进步～"
        else:
            greeting = "本周统计报告："
        
        # 统计数据
        total_tasks = len(week_tasks)
        completed_tasks = len([t for t in week_tasks if t.status == TaskStatus.COMPLETED])
        completion_rate = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # 按象限统计
        q1_tasks = len([t for t in week_tasks if t.quadrant == 1])
        q2_tasks = len([t for t in week_tasks if t.quadrant == 2])
        q3_tasks = len([t for t in week_tasks if t.quadrant == 3])
        q4_tasks = len([t for t in week_tasks if t.quadrant == 4])
        
        content = f"""
{greeting}

📊 本周数据概览：
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• 总任务数: {total_tasks}
• 已完成: {completed_tasks}
• 完成率: {completion_rate:.1f}%

📈 象限分布：
• Q1 (重要紧急): {q1_tasks} 个任务
• Q2 (重要不紧急): {q2_tasks} 个任务
• Q3 (不重要紧急): {q3_tasks} 个任务
• Q4 (不重要不紧急): {q4_tasks} 个任务

"""
        
        # 根据完成率给出反馈
        if completion_rate >= 80:
            if config.persona == Persona.TOXIC:
                feedback = "哟，这周表现还不错嘛，难得看你这么努力！"
            elif config.persona == Persona.WARM:
                feedback = "太棒了！你这周的表现非常出色，继续保持！"
            else:
                feedback = "本周完成率优秀，继续保持。"
        elif completion_rate >= 50:
            if config.persona == Persona.TOXIC:
                feedback = "勉强及格吧，下周能不能再努力点？"
            elif config.persona == Persona.WARM:
                feedback = "你已经做得很好了，下周我们一起加油！"
            else:
                feedback = "本周完成率良好，仍有提升空间。"
        else:
            if config.persona == Persona.TOXIC:
                feedback = "这周是在摸鱼吗？下周再这样就别怪我不客气了！"
            elif config.persona == Persona.WARM:
                feedback = "这周可能有些困难，没关系，下周我们重新开始！"
            else:
                feedback = "本周完成率偏低，建议调整任务规划。"
        
        content += f"💬 本周点评：\n{feedback}\n"
        content += "\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
        content += "下周继续加油！💪"
        
        return content
    
    async def send_email(self, to_email: str, subject: str, content: str) -> bool:
        """发送邮件（使用多平台通知管理器）"""
        try:
            results = await notification_manager.send_notification(to_email, subject, content)
            
            # 检查是否至少有一个平台发送成功
            success_count = sum(1 for success in results.values() if success)
            total_count = len(results)
            
            if success_count > 0:
                logger.info(f"✅ 通知发送成功: {success_count}/{total_count} 个平台")
                logger.info(f"   发送结果: {results}")
                return True
            else:
                logger.error(f"❌ 所有平台通知发送失败: {results}")
                return False
                
        except Exception as e:
            logger.error(f"❌ 通知发送异常: {str(e)}")
            return False

# 全局实例
debouncer = EmailDebouncer()
llm_parser = LLMParser()
db_syncer = DatabaseSyncer()
email_generator = EmailGenerator()

# Webhook处理器
class WebhookHandler:
    async def verify_webhook_signature(self, payload: bytes, signature: str) -> bool:
        """验证webhook签名"""
        # 开发环境跳过验证
        if not RESEND_WEBHOOK_SECRET or RESEND_WEBHOOK_SECRET == "whsec_你从resend获取的实际secret":
            logger.warning("⚠️ 开发模式：跳过webhook签名验证")
            return True
        
        expected_signature = hmac.new(
            RESEND_WEBHOOK_SECRET.encode(),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(f"sha256={expected_signature}", signature)
    
    async def extract_email_data(self, webhook_data: dict) -> EmailData:
        """从webhook数据中提取邮件信息"""
        data = webhook_data.get("data", {})
        
        return EmailData(
            from_email=data.get("from", {}).get("email", ""),
            subject=data.get("subject", ""),
            content=data.get("text", ""),
            received_at=datetime.utcnow(),
            message_id=data.get("message_id", "")
        )

webhook_handler = WebhookHandler()

# API路由
@app.post("/inbound-email")
async def handle_inbound_email(request: Request, background_tasks: BackgroundTasks):
    """处理入站邮件webhook"""
    try:
        # 获取原始请求体
        payload = await request.body()
        signature = request.headers.get("resend-signature", "")
        
        # 验证签名
        if not await webhook_handler.verify_webhook_signature(payload, signature):
            raise HTTPException(status_code=401, detail="签名验证失败")
        
        # 解析JSON数据
        webhook_data = await request.json()
        
        # 提取邮件数据
        email_data = await webhook_handler.extract_email_data(webhook_data)
        
        # 添加后台任务处理邮件
        background_tasks.add_task(process_email, email_data)
        
        return {"status": "success", "message": "邮件已接收，正在处理中"}
        
    except Exception as e:
        logger.error(f"处理webhook失败: {str(e)}")
        raise HTTPException(status_code=500, detail="内部服务器错误")

async def process_email(email_data: EmailData):
    """处理邮件的后台任务"""
    try:
        user_email = str(email_data.from_email)
        
        # 防抖检查
        if not await debouncer.should_process_email(user_email, email_data.message_id):
            logger.info(f"邮件被防抖机制跳过: {user_email}")
            return
        
        # 使用LLM解析邮件内容
        parse_result = await llm_parser.parse_reply(email_data.content, user_email)
        
        if parse_result.confidence_score < 0.5:
            logger.warning(f"LLM解析置信度过低: {parse_result.confidence_score}")
            # 可以发送确认邮件给用户
            return
        
        # 检查是否是计划修改
        if parse_result.is_plan_modification:
            if await db_syncer.check_daily_edit_limit(user_email):
                # 发送拒绝邮件
                await send_rejection_email(user_email)
                return
            else:
                await db_syncer.increment_daily_edit_count(user_email)
        
        # 同步任务更新到数据库
        await db_syncer.sync_task_updates(parse_result.task_updates, user_email)
        
        # 生成并发送反馈邮件
        feedback_content = await email_generator.generate_feedback_email(
            user_email, parse_result.task_updates
        )
        
        await email_generator.send_email(
            user_email,
            "📊 任务进度反馈",
            feedback_content
        )
        
        logger.info(f"邮件处理完成: {user_email}")
        
    except Exception as e:
        logger.error(f"处理邮件异常: {str(e)}")

async def send_rejection_email(user_email: str):
    """发送拒绝修改计划的邮件"""
    config = await email_generator.get_user_config(user_email)
    
    if config.persona == Persona.TOXIC:
        content = """
哎呀呀，又想改计划了？

你今天已经改了2次计划了，够了！三天打鱼两天晒网的毛病什么时候能改？

计划就是用来执行的，不是用来天天修改的装饰品。专心把现有的任务做完，别总想着换来换去。

明天再来折腾吧！

---
你的毒舌AI督导
"""
    elif config.persona == Persona.WARM:
        content = """
亲爱的，我理解你想要调整计划的想法～

不过今天你已经修改了2次计划了，为了帮助你培养执行力，我们每天最多只能修改2次哦。

专注于当前的任务，相信你一定能做得很好！明天我们再来调整计划吧。

加油！你是最棒的！

---
你的暖心AI督导
"""
    else:
        content = """
今日计划修改次数已达上限（2次）。

为了培养执行力和专注度，建议专心完成现有任务。

明日可重新调整计划。

---
AI督导系统
"""
    
    await email_generator.send_email(
        user_email,
        "⚠️ 计划修改次数已达上限",
        content
    )

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

def process_webhook_sync(body: str, headers: dict) -> dict:
    """同步处理webhook请求（用于云函数）"""
    try:
        import json
        from datetime import datetime
        
        # 解析请求数据
        if isinstance(body, str):
            webhook_data = json.loads(body)
        else:
            webhook_data = body
        
        # 提取邮件数据
        data = webhook_data.get("data", {})
        email_data = EmailData(
            from_email=data.get("from", {}).get("email", ""),
            subject=data.get("subject", ""),
            content=data.get("text", ""),
            received_at=datetime.utcnow(),
            message_id=data.get("message_id", "")
        )
        
        # 异步处理邮件（在同步环境中运行）
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(process_email(email_data))
        finally:
            loop.close()
        
        return {"status": "success", "message": "邮件处理完成"}
        
    except Exception as e:
        logger.error(f"同步处理webhook失败: {str(e)}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)