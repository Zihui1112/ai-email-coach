"""
处理用户回复脚本 - GitHub Actions
"""
import os
import sys
import asyncio

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from standalone_coach import process_user_reply

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ 缺少回复内容参数")
        sys.exit(1)
    
    reply_content = sys.argv[1]
    success = asyncio.run(process_user_reply(reply_content))
    sys.exit(0 if success else 1)
