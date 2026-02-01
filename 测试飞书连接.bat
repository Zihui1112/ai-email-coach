@echo off
echo ====================================
echo 测试飞书连接
echo ====================================
echo.

REM 激活虚拟环境
call ai-email-coach-env\Scripts\activate.bat

REM 测试飞书
python standalone_coach.py test

pause
