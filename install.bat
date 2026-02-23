@echo off
echo ================================
echo 安装NDDF对偶模型计算工具依赖
echo ================================
echo.

echo [1/2] 安装后端依赖...
cd /d "%~dp0backend"
pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

echo.
echo [2/2] 安装前端依赖...
cd /d "%~dp0frontend"
call npm install

echo.
echo ================================
echo 依赖安装完成!
echo 请运行 start.bat 启动应用
echo ================================
pause
