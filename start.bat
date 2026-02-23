@echo off
echo ================================
echo NDDF对偶模型计算工具 - 启动脚本
echo ================================
echo.

echo [1/2] 启动后端服务...
cd /d "%~dp0backend"
start "NDDF Backend" cmd /k "python main.py"

timeout /t 3 /nobreak > nul

echo [2/2] 启动前端服务...
cd /d "%~dp0frontend"
start "NDDF Frontend" cmd /k "npm run dev"

echo.
echo ================================
echo 服务启动完成!
echo 后端地址: http://localhost:8000
echo 前端地址: http://localhost:3000
echo ================================
pause
