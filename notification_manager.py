"""
多平台通知管理器 - 支持邮件、飞书、企业微信等多种通知方式
"""

import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.header import Header
import httpx
import asyncio
from typing import List, Dict, Optional
from enum import Enum
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

class NotificationType(str, Enum):
    EMAIL = "email"
    FEISHU = "feishu"
    WECHAT_WORK = "wechat_work"
    DINGTALK = "dingtalk"
    TELEGRAM = "telegram"

@dataclass
class NotificationConfig:
    type: NotificationType
    config: Dict
    enabled: bool = True

class NotificationManager:
    def __init__(self):
        self.configs = self._load_configs()
    
    def _load_configs(self) -> List[NotificationConfig]:
        """加载通知配置"""
        configs = []
        
        # 邮件配置 - 支持多种邮箱
        email_configs = [
            # Resend (当前使用)
            {
                "type": NotificationType.EMAIL,
                "config": {
                    "provider": "resend",
                    "api_key": os.getenv("RESEND_API_KEY"),
                    "from_email": "AI督导 <coach@你的域名.com>"
                },
                "enabled": bool(os.getenv("RESEND_API_KEY"))
            },
            # 163邮箱
            {
                "type": NotificationType.EMAIL,
                "config": {
                    "provider": "smtp",
                    "smtp_server": "smtp.163.com",
                    "smtp_port": 465,
                    "username": os.getenv("EMAIL_163_USERNAME"),
                    "password": os.getenv("EMAIL_163_PASSWORD"),
                    "from_email": os.getenv("EMAIL_163_USERNAME")
                },
                "enabled": bool(os.getenv("EMAIL_163_USERNAME"))
            },
            # QQ邮箱
            {
                "type": NotificationType.EMAIL,
                "config": {
                    "provider": "smtp",
                    "smtp_server": "smtp.qq.com", 
                    "smtp_port": 465,
                    "username": os.getenv("EMAIL_QQ_USERNAME"),
                    "password": os.getenv("EMAIL_QQ_PASSWORD"),
                    "from_email": os.getenv("EMAIL_QQ_USERNAME")
                },
                "enabled": bool(os.getenv("EMAIL_QQ_USERNAME"))
            }
        ]
        
        # 飞书机器人配置
        feishu_config = {
            "type": NotificationType.FEISHU,
            "config": {
                "webhook_url": os.getenv("FEISHU_WEBHOOK_URL"),
                "secret": os.getenv("FEISHU_SECRET")
            },
            "enabled": bool(os.getenv("FEISHU_WEBHOOK_URL"))
        }
        
        # 企业微信机器人配置
        wechat_config = {
            "type": NotificationType.WECHAT_WORK,
            "config": {
                "webhook_url": os.getenv("WECHAT_WEBHOOK_URL"),
                "key": os.getenv("WECHAT_KEY")
            },
            "enabled": bool(os.getenv("WECHAT_WEBHOOK_URL"))
        }
        
        # 钉钉机器人配置
        dingtalk_config = {
            "type": NotificationType.DINGTALK,
            "config": {
                "webhook_url": os.getenv("DINGTALK_WEBHOOK_URL"),
                "secret": os.getenv("DINGTALK_SECRET")
            },
            "enabled": bool(os.getenv("DINGTALK_WEBHOOK_URL"))
        }
        
        all_configs = email_configs + [feishu_config, wechat_config, dingtalk_config]
        
        for config in all_configs:
            if config["enabled"]:
                configs.append(NotificationConfig(**config))
        
        return configs
    
    async def send_notification(self, to_user: str, subject: str, content: str) -> Dict[str, bool]:
        """发送通知到所有配置的平台"""
        results = {}
        
        for config in self.configs:
            try:
                if config.type == NotificationType.EMAIL:
                    success = await self._send_email(config, to_user, subject, content)
                elif config.type == NotificationType.FEISHU:
                    success = await self._send_feishu(config, to_user, subject, content)
                elif config.type == NotificationType.WECHAT_WORK:
                    success = await self._send_wechat(config, to_user, subject, content)
                elif config.type == NotificationType.DINGTALK:
                    success = await self._send_dingtalk(config, to_user, subject, content)
                else:
                    success = False
                
                results[f"{config.type.value}_{config.config.get('provider', 'default')}"] = success
                
            except Exception as e:
                logger.error(f"发送{config.type.value}通知失败: {e}")
                results[f"{config.type.value}_{config.config.get('provider', 'default')}"] = False
        
        return results
    
    async def _send_email(self, config: NotificationConfig, to_email: str, subject: str, content: str) -> bool:
        """发送邮件通知"""
        if config.config["provider"] == "resend":
            return await self._send_resend_email(config, to_email, subject, content)
        else:
            return await self._send_smtp_email(config, to_email, subject, content)
    
    async def _send_resend_email(self, config: NotificationConfig, to_email: str, subject: str, content: str) -> bool:
        """使用Resend发送邮件"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.resend.com/emails",
                    headers={
                        "Authorization": f"Bearer {config.config['api_key']}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "from": config.config["from_email"],
                        "to": [to_email],
                        "subject": subject,
                        "text": content
                    }
                )
                
                if response.status_code == 200:
                    logger.info(f"✅ Resend邮件发送成功: {to_email}")
                    return True
                else:
                    logger.error(f"❌ Resend邮件发送失败: {response.status_code} - {response.text}")
                    return False
        except Exception as e:
            logger.error(f"❌ Resend邮件发送异常: {e}")
            return False
    
    async def _send_smtp_email(self, config: NotificationConfig, to_email: str, subject: str, content: str) -> bool:
        """使用SMTP发送邮件（163、QQ等）"""
        try:
            # 创建邮件对象
            msg = MIMEMultipart()
            msg['From'] = Header(f"AI督导 <{config.config['from_email']}>", 'utf-8')
            msg['To'] = Header(to_email, 'utf-8')
            msg['Subject'] = Header(subject, 'utf-8')
            
            # 添加邮件正文
            msg.attach(MIMEText(content, 'plain', 'utf-8'))
            
            # 连接SMTP服务器
            server = smtplib.SMTP_SSL(config.config['smtp_server'], config.config['smtp_port'])
            server.login(config.config['username'], config.config['password'])
            
            # 发送邮件
            server.sendmail(config.config['from_email'], [to_email], msg.as_string())
            server.quit()
            
            logger.info(f"✅ SMTP邮件发送成功: {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"❌ SMTP邮件发送失败: {e}")
            return False
    
    async def _send_feishu(self, config: NotificationConfig, to_user: str, subject: str, content: str) -> bool:
        """发送飞书机器人通知"""
        try:
            # 格式化飞书消息
            message = {
                "msg_type": "text",
                "content": {
                    "text": f"📊 {subject}\n\n{content}\n\n👤 用户: {to_user}"
                }
            }
            
            # 如果配置了签名，添加签名验证
            if config.config.get("secret"):
                import time
                import hmac
                import hashlib
                import base64
                
                timestamp = str(int(time.time()))
                string_to_sign = f"{timestamp}\n{config.config['secret']}"
                hmac_code = hmac.new(
                    string_to_sign.encode("utf-8"),
                    digestmod=hashlib.sha256
                ).digest()
                sign = base64.b64encode(hmac_code).decode('utf-8')
                
                message["timestamp"] = timestamp
                message["sign"] = sign
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    config.config["webhook_url"],
                    json=message
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("StatusCode") == 0:
                        logger.info(f"✅ 飞书通知发送成功: {to_user}")
                        return True
                    else:
                        logger.error(f"❌ 飞书通知发送失败: {result}")
                        return False
                else:
                    logger.error(f"❌ 飞书通知请求失败: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ 飞书通知发送异常: {e}")
            return False
    
    async def _send_wechat(self, config: NotificationConfig, to_user: str, subject: str, content: str) -> bool:
        """发送企业微信机器人通知"""
        try:
            message = {
                "msgtype": "text",
                "text": {
                    "content": f"📊 {subject}\n\n{content}\n\n👤 用户: {to_user}"
                }
            }
            
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    config.config["webhook_url"],
                    json=message
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("errcode") == 0:
                        logger.info(f"✅ 企业微信通知发送成功: {to_user}")
                        return True
                    else:
                        logger.error(f"❌ 企业微信通知发送失败: {result}")
                        return False
                else:
                    logger.error(f"❌ 企业微信通知请求失败: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ 企业微信通知发送异常: {e}")
            return False
    
    async def _send_dingtalk(self, config: NotificationConfig, to_user: str, subject: str, content: str) -> bool:
        """发送钉钉机器人通知"""
        try:
            message = {
                "msgtype": "text",
                "text": {
                    "content": f"📊 {subject}\n\n{content}\n\n👤 用户: {to_user}"
                }
            }
            
            # 如果配置了签名，添加签名验证
            if config.config.get("secret"):
                import time
                import hmac
                import hashlib
                import base64
                import urllib.parse
                
                timestamp = str(round(time.time() * 1000))
                secret_enc = config.config["secret"].encode('utf-8')
                string_to_sign = f'{timestamp}\n{config.config["secret"]}'
                string_to_sign_enc = string_to_sign.encode('utf-8')
                hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
                sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
                
                webhook_url = f"{config.config['webhook_url']}&timestamp={timestamp}&sign={sign}"
            else:
                webhook_url = config.config["webhook_url"]
            
            async with httpx.AsyncClient() as client:
                response = await client.post(webhook_url, json=message)
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get("errcode") == 0:
                        logger.info(f"✅ 钉钉通知发送成功: {to_user}")
                        return True
                    else:
                        logger.error(f"❌ 钉钉通知发送失败: {result}")
                        return False
                else:
                    logger.error(f"❌ 钉钉通知请求失败: {response.status_code}")
                    return False
                    
        except Exception as e:
            logger.error(f"❌ 钉钉通知发送异常: {e}")
            return False

# 全局通知管理器实例
notification_manager = NotificationManager()