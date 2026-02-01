@echo off
echo ====================================
echo 推送代码到GitHub
echo ====================================
echo.

echo 请先在GitHub创建仓库，然后输入仓库地址
echo 例如: https://github.com/你的用户名/ai-email-coach.git
echo.

set /p REPO_URL="请输入GitHub仓库地址: "

echo.
echo 开始推送...
echo.

REM 添加所有文件
git add .

REM 提交
git commit -m "AI邮件督导系统 - 完整版"

REM 设置主分支
git branch -M main

REM 添加远程仓库
git remote remove origin 2>nul
git remote add origin %REPO_URL%

REM 推送
git push -u origin main

echo.
echo ====================================
echo 推送完成！
echo ====================================
echo.
echo 下一步：
echo 1. 访问你的GitHub仓库
echo 2. 进入 Settings - Secrets and variables - Actions
echo 3. 添加5个Secrets（参考 GitHub Actions完整部署指南.md）
echo 4. 进入 Actions 标签测试workflows
echo.

pause
