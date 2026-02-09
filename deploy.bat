@echo off
REM AI-EdgeHub Windows快速部署脚本
REM 使用方法: deploy.bat [dev|docker]

setlocal enabledelayedexpansion

set DEPLOY_MODE=%1
if "%DEPLOY_MODE%"=="" set DEPLOY_MODE=dev

echo ==========================================
echo AI-EdgeHub 部署脚本
echo 部署模式: %DEPLOY_MODE%
echo ==========================================

REM 检查Python
python --version >nul 2>&1
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    exit /b 1
)

if "%DEPLOY_MODE%"=="dev" (
    echo 开始开发环境部署...
    
    REM 后端部署
    echo 部署后端...
    cd backend
    
    if not exist "venv" (
        echo 创建Python虚拟环境...
        python -m venv venv
    )
    
    echo 激活虚拟环境并安装依赖...
    call venv\Scripts\activate.bat
    pip install --upgrade pip
    pip install -r requirements.txt
    
    if not exist ".env" (
        echo 创建配置文件...
        copy .env.example .env
        echo 请编辑 backend\.env 文件配置环境变量
    )
    
    echo ✓ 后端部署完成
    cd ..
    
    REM 前端部署
    echo 部署前端...
    cd frontend
    
    if not exist "node_modules" (
        echo 安装前端依赖...
        call npm install
    )
    
    echo ✓ 前端部署完成
    cd ..
    
    echo.
    echo ==========================================
    echo 部署完成！
    echo.
    echo 启动后端:
    echo   cd backend ^&^& venv\Scripts\activate ^&^& python run.py
    echo.
    echo 启动前端:
    echo   cd frontend ^&^& npm run dev
    echo.
    echo 访问地址:
    echo   前端: http://localhost:5173
    echo   后端API: http://localhost:8000/api/docs
    echo ==========================================
)

if "%DEPLOY_MODE%"=="docker" (
    echo 开始Docker部署...
    
    REM 检查Docker
    docker --version >nul 2>&1
    if errorlevel 1 (
        echo 错误: 未找到Docker，请先安装Docker Desktop
        exit /b 1
    )
    
    docker-compose --version >nul 2>&1
    if errorlevel 1 (
        echo 错误: 未找到Docker Compose，请先安装Docker Compose
        exit /b 1
    )
    
    REM 创建必要的目录
    if not exist "backend\logs" mkdir backend\logs
    if not exist "backend\data" mkdir backend\data
    if not exist "backend\uploads\models" mkdir backend\uploads\models
    if not exist "backend\uploads\videos" mkdir backend\uploads\videos
    if not exist "backend\uploads\alerts" mkdir backend\uploads\alerts
    
    REM 检查配置文件
    if not exist "backend\.env" (
        echo 创建后端配置文件...
        copy backend\.env.example backend\.env
        echo 请编辑 backend\.env 文件
    )
    
    REM 构建和启动
    echo 构建Docker镜像...
    docker-compose build
    
    echo 启动服务...
    docker-compose up -d
    
    echo.
    echo ==========================================
    echo Docker部署完成！
    echo.
    echo 查看状态:
    echo   docker-compose ps
    echo.
    echo 查看日志:
    echo   docker-compose logs -f
    echo.
    echo 停止服务:
    echo   docker-compose down
    echo.
    echo 访问地址:
    echo   前端: http://localhost
    echo   后端API: http://localhost:8000/api/docs
    echo ==========================================
)

endlocal
