@echo off
echo ====================================
echo 启动AI邮件督导系统 (POP3模式)
echo ====================================
echo.

REM 激活虚拟环境
call ai-email-coach-env\Scripts\activate.bat

REM 运行邮件督导 (POP3版本)
python simple_email_coach_pop3.py

pause
