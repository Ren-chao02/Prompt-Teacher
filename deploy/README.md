# 部署指南

本目录包含 Prompt Teacher 项目的部署配置文件。

## 文件说明

- `nginx.conf` - Nginx 反向代理配置
- `init-db.sql` - PostgreSQL 数据库初始化脚本
- `docker-compose.prod.yml` - 生产环境 Docker Compose 配置（可选）

## 生产环境部署建议

### 1. 安全配置

- 修改 `.env` 文件中的所有默认密码
- 使用强密码（至少 16 位，包含大小写字母、数字和特殊字符）
- 配置防火墙规则，只开放必要端口（80, 443）
- 启用 HTTPS（使用 Let's Encrypt 或其他 SSL 证书）

### 2. 性能优化

- 根据服务器配置调整 Gunicorn workers 数量
- 配置数据库连接池
- 启用 Redis 缓存（可选）
- 配置 CDN 加速静态资源

### 3. 监控与日志

- 配置日志收集（如 ELK Stack）
- 设置监控告警（如 Prometheus + Grafana）
- 定期备份数据库

### 4. 高可用部署

- 使用 Docker Swarm 或 Kubernetes 进行容器编排
- 配置数据库主从复制
- 使用负载均衡器（如 Nginx、HAProxy）

## SSL/HTTPS 配置

使用 Certbot 配置 Let's Encrypt SSL 证书：

```bash
# 安装 Certbot
sudo apt-get install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo certbot renew --dry-run
```

## 故障排查

### 常见问题

1. **容器无法启动**
   - 检查日志：`./deploy.sh logs`
   - 检查端口占用：`netstat -tlnp | grep -E '80|5432|8001'`

2. **数据库连接失败**
   - 检查数据库容器状态：`docker ps`
   - 检查数据库日志：`./deploy.sh logs db`

3. **前端无法访问后端 API**
   - 检查 Nginx 配置
   - 检查后端服务状态：`./deploy.sh status`

### 日志位置

- 后端日志：`docker logs prompt-teacher-backend`
- 前端日志：`docker logs prompt-teacher-frontend`
- 数据库日志：`docker logs prompt-teacher-db`
- Nginx 日志：容器内 `/var/log/nginx/`

## 备份策略

建议配置自动备份：

```bash
# 每天凌晨 2 点自动备份
crontab -e

# 添加以下行
0 2 * * * cd /path/to/prompt-teacher && ./deploy.sh backup >> /var/log/prompt-teacher-backup.log 2>&1
```

## 更新维护

```bash
# 更新服务
./deploy.sh update

# 回滚到指定版本
git checkout <commit-hash>
./deploy.sh restart
```
