# Happy FastAPI 项目

基于FastAPI构建的高性能API服务，使用Traefik作为API网关进行部署。

## 项目架构

本项目采用以下技术栈：

- **FastAPI**: 高性能Python Web框架
- **PostgreSQL**: 关系型数据库
- **Traefik**: API网关和负载均衡器
- **Docker & Docker Compose**: 容器化部署
- **Gunicorn & Uvicorn**: ASGI服务器
- **Alembic**: 数据库迁移工具
- **SQLModel**: ORM框架

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
├── migrations/            # 数据库迁移脚本
│   ├── versions/          # 迁移版本
│   ├── env.py             # 迁移环境配置
│   └── script.py.mako     # 迁移脚本模板
├── scripts/               # 脚本工具
│   └── db_migrate.py      # 数据库迁移工具
├── src/                   # 源代码
│   ├── core/              # 核心模块
│   ├── api/               # API路由
│   ├── models/            # 数据模型
│   ├── schemas/           # Pydantic模型
│   ├── services/          # 业务逻辑
│   ├── utils/             # 工具函数
│   └── main.py            # 应用入口
├── alembic.ini            # Alembic配置文件
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

## 数据库迁移

本项目使用Alembic进行数据库迁移管理，提供了便捷的脚本工具来执行常见的迁移操作。

### 迁移工具使用

项目提供了`scripts/db_migrate.py`脚本，用于简化数据库迁移操作：

```bash
# 显示帮助信息
python scripts/db_migrate.py -h

# 创建新的迁移脚本
python scripts/db_migrate.py create -m "迁移说明"

# 升级数据库到最新版本 --checkfirst 跳过已存在的数据库变更
python scripts/db_migrate.py upgrade --checkfirst

# 升级数据库到指定版本
python scripts/db_migrate.py upgrade -r <revision>

# 降级数据库到上一个版本
python scripts/db_migrate.py downgrade

# 降级数据库到指定版本
python scripts/db_migrate.py downgrade -r <revision>

# 显示迁移历史
python scripts/db_migrate.py history

# 显示当前版本
python scripts/db_migrate.py current

# 初始化数据库
python scripts/db_migrate.py init
```

### 手动使用Alembic

如果需要直接使用Alembic命令，可以参考以下示例：

```bash
# 创建新的迁移脚本
alembic revision --autogenerate -m "迁移说明"

# 升级数据库到最新版本
alembic upgrade head

# 降级数据库到上一个版本
alembic downgrade -1
```

### 迁移脚本管理

所有的迁移脚本都存储在`migrations/versions`目录中，每个脚本包含升级和降级的操作。在提交代码时，应该包含这些迁移脚本，以确保其他开发人员可以同步数据库结构。

### 常见数据库迁移操作

#### 1. 创建表

在迁移脚本的`upgrade()`函数中添加：

```python
def upgrade() -> None:
    op.create_table(
        "table_name",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table("table_name", schema=None) as batch_op:
        batch_op.create_index(batch_op.f("ix_table_name_id"), ["id"], unique=False)
```

在`downgrade()`函数中添加：

```python
def downgrade() -> None:
    with op.batch_alter_table("table_name", schema=None) as batch_op:
        batch_op.drop_index(batch_op.f("ix_table_name_id"))
    op.drop_table("table_name")
```

#### 2. 添加列

在迁移脚本的`upgrade()`函数中添加：

```python
def upgrade() -> None:
    with op.batch_alter_table("table_name", schema=None) as batch_op:
        batch_op.add_column(sa.Column("new_column", sa.String(length=50), nullable=True))
```

在`downgrade()`函数中添加：

```python
def downgrade() -> None:
    with op.batch_alter_table("table_name", schema=None) as batch_op:
        batch_op.drop_column("new_column")
```

#### 3. 修改列

在迁移脚本的`upgrade()`函数中添加：

```python
def upgrade() -> None:
    with op.batch_alter_table("table_name", schema=None) as batch_op:
        batch_op.alter_column("column_name",
                              existing_type=sa.String(length=50),
                              type_=sa.String(length=100),
                              existing_nullable=True)
```

在`downgrade()`函数中添加：

```python
def downgrade() -> None:
    with op.batch_alter_table("table_name", schema=None) as batch_op:
        batch_op.alter_column("column_name",
                              existing_type=sa.String(length=100),
                              type_=sa.String(length=50),
                              existing_nullable=True)
```

#### 4. 添加索引

在迁移脚本的`upgrade()`函数中添加：

```python
def upgrade() -> None:
    with op.batch_alter_table("table_name", schema=None) as batch_op:
        batch_op.create_index("idx_column_name", ["column_name"], unique=False)
```

在`downgrade()`函数中添加：

```python
def downgrade() -> None:
    with op.batch_alter_table("table_name", schema=None) as batch_op:
        batch_op.drop_index("idx_column_name")
```

#### 5. 添加外键约束

在迁移脚本的`upgrade()`函数中添加：

```python
def upgrade() -> None:
    with op.batch_alter_table("child_table", schema=None) as batch_op:
        batch_op.create_foreign_key(
            "fk_child_parent",
            "parent_table",
            ["parent_id"],
            ["id"],
            ondelete="CASCADE"
        )
```

在`downgrade()`函数中添加：

```python
def downgrade() -> None:
    with op.batch_alter_table("child_table", schema=None) as batch_op:
        batch_op.drop_constraint("fk_child_parent", type_="foreignkey")
```

#### 6. 数据迁移

在迁移脚本中添加数据迁移操作：

```python
def upgrade() -> None:
    # 创建连接
    connection = op.get_bind()

    # 执行SQL语句
    connection.execute(
        sa.text("UPDATE table_name SET column_name = 'new_value' WHERE condition = 'value'")
    )
```

#### 7. 处理枚举类型

在迁移脚本中添加枚举类型：

```python
def upgrade() -> None:
    # 创建枚举类型
    status_type = sa.Enum('ACTIVE', 'INACTIVE', 'PENDING', name='status_enum')
    status_type.create(op.get_bind())

    # 添加使用枚举类型的列
    with op.batch_alter_table("table_name", schema=None) as batch_op:
        batch_op.add_column(sa.Column('status', status_type, nullable=False))
```

在`downgrade()`函数中添加：

```python
def downgrade() -> None:
    with op.batch_alter_table("table_name", schema=None) as batch_op:
        batch_op.drop_column('status')

    # 删除枚举类型
    sa.Enum(name='status_enum').drop(op.get_bind())
```

### 最佳实践

1. **保持迁移脚本简单**：每个迁移脚本应该只做一件事，如添加一个表或修改一个字段。
2. **测试迁移脚本**：在应用到生产环境之前，确保迁移脚本在开发环境中正常工作。
3. **版本控制**：将迁移脚本纳入版本控制系统，确保团队成员可以同步数据库结构。
4. **备份数据**：在执行迁移操作之前，确保已经备份了数据库。
5. **使用事务**：Alembic默认在事务中执行迁移操作，确保操作的原子性。
6. **编写有意义的迁移说明**：在创建迁移脚本时，提供有意义的说明，以便于理解迁移的目的。
7. **定期清理**：定期清理不再需要的迁移脚本，但要确保所有环境都已经应用了这些迁移。

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