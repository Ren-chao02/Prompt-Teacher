@echo off
chcp 65001 >nul
echo ==============================================
echo 🚀 提示词教学平台 - 局域网服务器启动工具 (Windows)
echo ==============================================
echo.

REM 获取本机IP地址（Windows版本）
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /i "IPv4"') do set LOCAL_IP=%%a
set LOCAL_IP=%LOCAL_IP:~1%

if "%LOCAL_IP%"=="" (
    echo ❌ 错误：无法获取本机IP地址
    pause
    exit /b 1
)

set PORT=8001

echo ✅ 配置信息：
echo    📡 本机IP地址：%LOCAL_IP%
echo    🔌 服务端口：%PORT%
echo    🌐 访问地址：http://%LOCAL_IP%:%PORT%/
echo.
echo ⏳ 正在启动服务器...
echo.

cd /d "%~dp0"
python manage.py runserver 0.0.0.0:%PORT%

if %errorlevel% neq 0 (
    echo ❌ 服务器启动失败！
    pause
    exit /b 1
)

pause
