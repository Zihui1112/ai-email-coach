@echo off
echo ====================================
echo 发送每日复盘提醒
echo ====================================
echo.

REM 激活虚拟环境
call ai-email-coach-env\Scripts\activate.bat

REM 发送复盘提醒
python standalone_coach.py review

pause
