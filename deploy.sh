#!/bin/bash

# Prompt Teacher 一键部署脚本
# 用法: ./deploy.sh [命令]
# 命令: start | stop | restart | status | logs | backup | restore | init

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查 Docker 是否安装
check_docker() {
    if ! command -v docker &> /dev/null; then
        log_error "Docker 未安装，请先安装 Docker"
        log_info "安装指南: https://docs.docker.com/get-docker/"
        exit 1
    fi

    if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
        log_error "Docker Compose 未安装，请先安装 Docker Compose"
        log_info "安装指南: https://docs.docker.com/compose/install/"
        exit 1
    fi

    log_success "Docker 环境检查通过"
}

# 检查 .env 文件
check_env() {
    if [ ! -f .env ]; then
        log_warning ".env 文件不存在，正在从 .env.example 创建..."
        if [ -f .env.example ]; then
            cp .env.example .env
            log_success ".env 文件已创建，请根据需要修改配置"
        else
            log_error ".env.example 文件不存在，请手动创建 .env 文件"
            exit 1
        fi
    fi
}

# 创建必要的目录
create_directories() {
    log_info "创建必要的目录..."
    mkdir -p media staticfiles data backups
    log_success "目录创建完成"
}

# 初始化部署
init() {
    log_info "初始化部署环境..."
    check_docker
    check_env
    create_directories

    # 生成随机 SECRET_KEY
    if grep -q "your-secret-key-here" .env 2>/dev/null; then
        log_info "生成新的 SECRET_KEY..."
        SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
        if [[ "$OSTYPE" == "darwin"* ]]; then
            sed -i '' "s/your-secret-key-here/$SECRET_KEY/" .env
        else
            sed -i "s/your-secret-key-here/$SECRET_KEY/" .env
        fi
        log_success "SECRET_KEY 已生成"
    fi

    log_success "初始化完成！"
    log_info "请编辑 .env 文件配置数据库和 LLM 参数"
    log_info "然后运行: ./deploy.sh start"
}

# 启动服务
start() {
    log_info "启动 Prompt Teacher 服务..."
    check_docker
    check_env
    create_directories

    # 使用 docker compose 或 docker-compose
    if docker compose version &> /dev/null; then
        docker compose up -d --build
    else
        docker-compose up -d --build
    fi

    log_success "服务启动成功！"
    log_info "访问地址: http://localhost"
    log_info "API 文档: http://localhost/api/docs/"
    log_info "管理后台: http://localhost/admin/"
    show_status
}

# 停止服务
stop() {
    log_info "停止 Prompt Teacher 服务..."

    if docker compose version &> /dev/null; then
        docker compose down
    else
        docker-compose down
    fi

    log_success "服务已停止"
}

# 重启服务
restart() {
    log_info "重启 Prompt Teacher 服务..."
    stop
    sleep 2
    start
}

# 查看状态
show_status() {
    log_info "服务状态:"
    if docker compose version &> /dev/null; then
        docker compose ps
    else
        docker-compose ps
    fi
}

# 查看日志
logs() {
    local service=$1
    if [ -z "$service" ]; then
        if docker compose version &> /dev/null; then
            docker compose logs -f --tail=100
        else
            docker-compose logs -f --tail=100
        fi
    else
        if docker compose version &> /dev/null; then
            docker compose logs -f --tail=100 "$service"
        else
            docker-compose logs -f --tail=100 "$service"
        fi
    fi
}

# 数据备份
backup() {
    log_info "开始备份数据..."
    BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"

    # 备份数据库
    log_info "备份数据库..."
    if docker compose version &> /dev/null; then
        docker compose exec -T db pg_dump -U postgres prompt_teaching_db > "$BACKUP_DIR/database.sql"
    else
        docker-compose exec -T db pg_dump -U postgres prompt_teaching_db > "$BACKUP_DIR/database.sql"
    fi

    # 备份媒体文件
    log_info "备份媒体文件..."
    cp -r media "$BACKUP_DIR/" 2>/dev/null || log_warning "媒体目录为空，跳过备份"

    # 备份配置
    log_info "备份配置文件..."
    cp .env "$BACKUP_DIR/" 2>/dev/null || log_warning ".env 文件不存在，跳过备份"

    log_success "备份完成！备份位置: $BACKUP_DIR"
}

# 数据恢复
restore() {
    local backup_dir=$1
    if [ -z "$backup_dir" ]; then
        log_error "请指定备份目录: ./deploy.sh restore <backup_dir>"
        log_info "可用的备份:"
        ls -lt backups/ 2>/dev/null || log_warning "没有找到备份"
        exit 1
    fi

    if [ ! -d "$backup_dir" ]; then
        log_error "备份目录不存在: $backup_dir"
        exit 1
    fi

    log_warning "即将恢复数据，当前数据将被覆盖！"
    read -p "确认继续？(y/N): " confirm
    if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
        log_info "操作已取消"
        exit 0
    fi

    # 恢复数据库
    if [ -f "$backup_dir/database.sql" ]; then
        log_info "恢复数据库..."
        if docker compose version &> /dev/null; then
            docker compose exec -T db psql -U postgres prompt_teaching_db < "$backup_dir/database.sql"
        else
            docker-compose exec -T db psql -U postgres prompt_teaching_db < "$backup_dir/database.sql"
        fi
        log_success "数据库恢复完成"
    else
        log_error "数据库备份文件不存在"
    fi

    # 恢复媒体文件
    if [ -d "$backup_dir/media" ]; then
        log_info "恢复媒体文件..."
        cp -r "$backup_dir/media" ./
        log_success "媒体文件恢复完成"
    fi

    log_success "数据恢复完成！"
}

# 创建超级用户
create_superuser() {
    log_info "创建超级用户..."
    if docker compose version &> /dev/null; then
        docker compose exec backend python manage.py createsuperuser
    else
        docker-compose exec backend python manage.py createsuperuser
    fi
}

# 进入容器 shell
shell() {
    local service=${1:-backend}
    log_info "进入 $service 容器..."
    if docker compose version &> /dev/null; then
        docker compose exec "$service" sh
    else
        docker-compose exec "$service" sh
    fi
}

# 更新服务
update() {
    log_info "更新服务..."
    stop

    # 拉取最新代码
    if [ -d .git ]; then
        log_info "拉取最新代码..."
        git pull
    fi

    start
    log_success "服务更新完成！"
}

# 显示帮助
show_help() {
    cat << EOF
Prompt Teacher 一键部署脚本

用法: ./deploy.sh [命令]

命令:
  init          初始化部署环境（首次部署使用）
  start         启动所有服务
  stop          停止所有服务
  restart       重启所有服务
  status        查看服务状态
  logs [服务]   查看日志（可选: backend, frontend, db）
  backup        备份数据
  restore <目录> 恢复数据
  superuser     创建超级用户
  shell [服务]  进入容器 shell
  update        更新服务（拉取代码并重启）
  help          显示此帮助信息

示例:
  ./deploy.sh init              # 首次部署初始化
  ./deploy.sh start             # 启动服务
  ./deploy.sh logs backend      # 查看后端日志
  ./deploy.sh backup            # 备份数据
  ./deploy.sh restore backups/20240101_120000  # 恢复数据

EOF
}

# 主函数
main() {
    local command=${1:-help}

    case "$command" in
        init)
            init
            ;;
        start)
            start
            ;;
        stop)
            stop
            ;;
        restart)
            restart
            ;;
        status)
            show_status
            ;;
        logs)
            logs "$2"
            ;;
        backup)
            backup
            ;;
        restore)
            restore "$2"
            ;;
        superuser)
            create_superuser
            ;;
        shell)
            shell "$2"
            ;;
        update)
            update
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            log_error "未知命令: $command"
            show_help
            exit 1
            ;;
    esac
}

main "$@"
