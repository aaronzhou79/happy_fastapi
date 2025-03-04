# 部署指南

本目录包含Happy FastAPI项目的部署配置文件。

## 目录结构

```
deploy/
├── traefik/                # Traefik配置
│   ├── config/             # 动态配置
│   │   ├── dynamic_conf.yml # 路由和中间件配置
│   │   └── tls.yml         # TLS配置
│   ├── certs/              # SSL证书
│   └── traefik.yml         # 主配置文件
├── docker-compose.yml      # Docker Compose配置
├── gunicorn.conf.py        # Gunicorn配置
├── supervisor.conf         # Supervisor配置
├── fastapi_server.conf     # FastAPI服务配置
└── postgresql.conf         # PostgreSQL配置
```

## 快速开始

1. 确保已安装Docker和Docker Compose

```bash
docker --version
docker-compose --version
```

2. 创建必要的目录

```bash
mkdir -p ../logs/traefik ../logs/fastapi_server ../data/postgres
```

3. 启动服务

```bash
docker-compose up -d
```

4. 查看服务状态

```bash
docker-compose ps
```

## 配置说明

### Traefik配置

Traefik作为API网关，负责路由请求到相应的服务。主要配置文件：

- `traefik/traefik.yml`: 全局配置
- `traefik/config/dynamic_conf.yml`: 路由和中间件配置
- `traefik/config/tls.yml`: TLS和证书配置

### FastAPI服务配置

FastAPI服务通过Gunicorn和Uvicorn运行，相关配置：

- `gunicorn.conf.py`: Gunicorn配置
- `fastapi_server.conf`: Supervisor管理FastAPI服务的配置

### 数据库配置

PostgreSQL数据库配置：

- `postgresql.conf`: PostgreSQL服务器配置

## 环境变量

可以通过环境变量自定义配置：

- `POSTGRES_USER`: PostgreSQL用户名
- `POSTGRES_PASSWORD`: PostgreSQL密码
- `POSTGRES_DB`: PostgreSQL数据库名
- `TZ`: 时区设置

## 扩展服务

要水平扩展API服务，可以增加服务实例数量：

```bash
docker-compose up -d --scale api=3
```

## 生产环境部署

对于生产环境，建议进行以下配置：

1. 启用HTTPS
   - 配置SSL证书
   - 启用HTTP到HTTPS的重定向

2. 安全设置
   - 禁用Traefik的不安全API访问
   - 使用强密码
   - 配置适当的请求限流

3. 监控和日志
   - 配置日志轮转
   - 设置监控告警

## 故障排除

1. 检查容器日志

```bash
docker-compose logs -f [service_name]
```

2. 检查网络连接

```bash
docker network inspect deploy_app-network
```

3. 验证健康检查

```bash
curl http://localhost/health
```

## 备份和恢复

### 数据库备份

```bash
docker exec postgres pg_dump -U root happy_code > backup.sql
```

### 数据库恢复

```bash
cat backup.sql | docker exec -i postgres psql -U root happy_code
```