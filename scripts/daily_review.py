"""
每日复盘提醒脚本 - GitHub Actions
"""
import os
import sys
import asyncio

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from github_actions_coach import send_daily_review

if __name__ == "__main__":
    success = asyncio.run(send_daily_review())
    sys.exit(0 if success else 1)
