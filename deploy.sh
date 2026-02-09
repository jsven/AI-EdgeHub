#!/bin/bash

# AI-EdgeHub 快速部署脚本
# 使用方法: ./deploy.sh [dev|prod|docker]

set -e

DEPLOY_MODE=${1:-dev}

echo "=========================================="
echo "AI-EdgeHub 部署脚本"
echo "部署模式: $DEPLOY_MODE"
echo "=========================================="

# 检查系统要求
check_requirements() {
    echo "检查系统要求..."
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        echo "错误: 未找到Python3，请先安装Python 3.8+"
        exit 1
    fi
    
    # 检查Node.js（前端部署需要）
    if [ "$DEPLOY_MODE" != "backend-only" ]; then
        if ! command -v node &> /dev/null; then
            echo "错误: 未找到Node.js，请先安装Node.js 16+"
            exit 1
        fi
    fi
    
    echo "✓ 系统要求检查通过"
}

# 开发环境部署
deploy_dev() {
    echo "开始开发环境部署..."
    
    # 后端部署
    echo "部署后端..."
    cd backend
    
    if [ ! -d "venv" ]; then
        echo "创建Python虚拟环境..."
        python3 -m venv venv
    fi
    
    echo "激活虚拟环境并安装依赖..."
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    if [ ! -f ".env" ]; then
        echo "创建配置文件..."
        cp .env.example .env
        echo "请编辑 backend/.env 文件配置环境变量"
    fi
    
    echo "✓ 后端部署完成"
    cd ..
    
    # 前端部署
    echo "部署前端..."
    cd frontend
    
    if [ ! -d "node_modules" ]; then
        echo "安装前端依赖..."
        npm install
    fi
    
    echo "✓ 前端部署完成"
    cd ..
    
    echo ""
    echo "=========================================="
    echo "部署完成！"
    echo ""
    echo "启动后端:"
    echo "  cd backend && source venv/bin/activate && python run.py"
    echo ""
    echo "启动前端:"
    echo "  cd frontend && npm run dev"
    echo ""
    echo "访问地址:"
    echo "  前端: http://localhost:5173"
    echo "  后端API: http://localhost:8000/api/docs"
    echo "=========================================="
}

# 生产环境部署
deploy_prod() {
    echo "开始生产环境部署..."
    
    # 创建部署目录
    DEPLOY_DIR="/opt/ai-edgehub"
    echo "创建部署目录: $DEPLOY_DIR"
    sudo mkdir -p $DEPLOY_DIR/{backend,frontend,logs,data,uploads}
    
    # 后端部署
    echo "部署后端..."
    sudo cp -r backend/* $DEPLOY_DIR/backend/
    cd $DEPLOY_DIR/backend
    
    sudo python3 -m venv venv
    sudo $DEPLOY_DIR/backend/venv/bin/pip install --upgrade pip
    sudo $DEPLOY_DIR/backend/venv/bin/pip install -r requirements.txt
    
    if [ ! -f ".env" ]; then
        sudo cp .env.example .env
        echo "请编辑 $DEPLOY_DIR/backend/.env 文件"
    fi
    
    # 创建systemd服务
    echo "创建systemd服务..."
    sudo tee /etc/systemd/system/ai-edgehub.service > /dev/null <<EOF
[Unit]
Description=AI-EdgeHub Backend Service
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=$DEPLOY_DIR/backend
Environment="PATH=$DEPLOY_DIR/backend/venv/bin"
ExecStart=$DEPLOY_DIR/backend/venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable ai-edgehub
    
    # 前端构建
    echo "构建前端..."
    cd frontend
    npm install
    npm run build
    sudo cp -r dist/* $DEPLOY_DIR/frontend/
    
    # 配置Nginx
    echo "配置Nginx..."
    sudo tee /etc/nginx/sites-available/ai-edgehub > /dev/null <<EOF
server {
    listen 80;
    server_name _;
    
    root $DEPLOY_DIR/frontend;
    index index.html;
    
    location / {
        try_files \$uri \$uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
    
    location /ws {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
EOF
    
    sudo ln -sf /etc/nginx/sites-available/ai-edgehub /etc/nginx/sites-enabled/
    sudo nginx -t
    sudo systemctl reload nginx
    
    echo ""
    echo "=========================================="
    echo "生产环境部署完成！"
    echo ""
    echo "启动服务:"
    echo "  sudo systemctl start ai-edgehub"
    echo ""
    echo "查看状态:"
    echo "  sudo systemctl status ai-edgehub"
    echo ""
    echo "查看日志:"
    echo "  sudo journalctl -u ai-edgehub -f"
    echo "=========================================="
}

# Docker部署
deploy_docker() {
    echo "开始Docker部署..."
    
    # 检查Docker
    if ! command -v docker &> /dev/null; then
        echo "错误: 未找到Docker，请先安装Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        echo "错误: 未找到Docker Compose，请先安装Docker Compose"
        exit 1
    fi
    
    # 创建必要的目录
    mkdir -p backend/{logs,data,uploads/{models,videos,alerts}}
    
    # 检查配置文件
    if [ ! -f "backend/.env" ]; then
        echo "创建后端配置文件..."
        cp backend/.env.example backend/.env
        echo "请编辑 backend/.env 文件"
    fi
    
    # 构建和启动
    echo "构建Docker镜像..."
    docker-compose build
    
    echo "启动服务..."
    docker-compose up -d
    
    echo ""
    echo "=========================================="
    echo "Docker部署完成！"
    echo ""
    echo "查看状态:"
    echo "  docker-compose ps"
    echo ""
    echo "查看日志:"
    echo "  docker-compose logs -f"
    echo ""
    echo "停止服务:"
    echo "  docker-compose down"
    echo ""
    echo "访问地址:"
    echo "  前端: http://localhost"
    echo "  后端API: http://localhost:8000/api/docs"
    echo "=========================================="
}

# 主函数
main() {
    check_requirements
    
    case $DEPLOY_MODE in
        dev)
            deploy_dev
            ;;
        prod)
            deploy_prod
            ;;
        docker)
            deploy_docker
            ;;
        *)
            echo "错误: 未知的部署模式: $DEPLOY_MODE"
            echo "使用方法: ./deploy.sh [dev|prod|docker]"
            exit 1
            ;;
    esac
}

main
