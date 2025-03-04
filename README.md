# 账套管理

在需要进行账套管理的MODEL中添加TenantMixin
```python
class Demo(DemoBase, TenantMixin, DateTimeMixin, DatabaseModel, table=True):
    """DEMO表"""
    __tablename__: Literal["demo"] = "demo"

    # Relationships
    demo_items: list["DemoItem"] = Relationship(back_populates="demo")
```

需要前端在请求时，携带账套ID
增加请求头：
    X-Tenant-Id: 租户ID

# Happy FastAPI 项目

基于FastAPI构建的高性能API服务，使用Traefik作为API网关进行部署。

## 项目架构

本项目采用以下技术栈：

- **FastAPI**: 高性能Python Web框架
- **PostgreSQL**: 关系型数据库
- **Traefik**: API网关和负载均衡器
- **Docker & Docker Compose**: 容器化部署
- **Gunicorn & Uvicorn**: ASGI服务器

## 目录结构

```
happy_fastapi/
├── data/                  # 数据存储目录
│   └── postgres/          # PostgreSQL数据
├── deploy/                # 部署配置
│   ├── traefik/           # Traefik配置
│   │   ├── config/        # 动态配置
│   │   ├── certs/         # SSL证书
│   │   └── traefik.yml    # 主配置文件
│   ├── docker-compose.yml # Docker Compose配置
│   ├── gunicorn.conf.py   # Gunicorn配置
│   ├── supervisor.conf    # Supervisor配置
│   └── fastapi_server.conf # FastAPI服务配置
├── logs/                  # 日志目录
├── src/                   # 源代码
│   ├── core/              # 核心模块
│   ├── api/               # API路由
│   ├── models/            # 数据模型
│   ├── schemas/           # Pydantic模型
│   ├── services/          # 业务逻辑
│   ├── utils/             # 工具函数
│   └── main.py            # 应用入口
└── Dockerfile             # Docker构建文件
```

## 部署指南

### 前置条件

- Docker 和 Docker Compose
- 域名（可选，用于生产环境）
- SSL证书（可选，用于HTTPS）

### 开发环境部署

1. 克隆仓库

```bash
git clone https://github.com/yourusername/happy_fastapi.git
cd happy_fastapi
```

2. 创建必要的目录

```bash
mkdir -p data/postgres logs/traefik logs/fastapi_server
```

3. 启动服务

```bash
cd deploy
docker-compose up -d
```

4. 访问服务

- API服务: http://localhost/api
- API文档: http://localhost/api/docs
- Traefik仪表盘: http://localhost:8080

### 生产环境部署

1. 修改配置

编辑 `deploy/traefik/traefik.yml` 文件，启用HTTPS重定向：

```yaml
entryPoints:
  web:
    address: ":80"
    http:
      redirections:
        entryPoint:
          to: websecure
          scheme: https
```

2. 配置域名和SSL证书

将SSL证书放置在 `deploy/traefik/certs` 目录下，并更新 `deploy/traefik/config/dynamic_conf.yml` 中的TLS配置。

3. 修改docker-compose.yml中的域名配置

将 `api.example.com` 替换为您的实际域名。

4. 启动服务

```bash
cd deploy
docker-compose up -d
```

## API网关功能

Traefik作为API网关提供以下功能：

1. **路由转发**: 将请求路由到相应的服务
2. **负载均衡**: 在多个服务实例之间分配流量
3. **SSL终止**: 处理HTTPS连接
4. **请求限流**: 防止API滥用
5. **路径重写**: 支持API版本控制和路径规范化
6. **健康检查**: 监控服务健康状态
7. **中间件支持**: 提供CORS、压缩、安全头等功能

## 扩展指南

### 水平扩展

要水平扩展API服务，可以增加服务实例数量：

```bash
docker-compose up -d --scale api=3
```

Traefik将自动发现新实例并进行负载均衡。

### 添加新服务

1. 在 `docker-compose.yml` 中添加新服务定义
2. 配置Traefik标签以启用路由
3. 在 `deploy/traefik/config/dynamic_conf.yml` 中添加相应的路由和中间件配置

## 监控和日志

- Traefik日志: `logs/traefik/`
- FastAPI服务日志: `logs/fastapi_server/`
- 数据库日志: 通过Docker日志查看 `docker logs postgres`

## 故障排除

1. 检查服务状态: `docker-compose ps`
2. 查看服务日志: `docker-compose logs -f [service_name]`
3. 检查网络连接: `docker network inspect deploy_app-network`
4. 验证健康检查: 访问 `http://localhost/health`

## 安全注意事项

1. 在生产环境中禁用Traefik的不安全API访问
2. 使用强密码保护数据库
3. 定期更新依赖和Docker镜像
4. 配置适当的请求限流以防止DoS攻击
5. 使用HTTPS加密所有通信
