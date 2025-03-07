# 第一阶段：依赖安装
FROM dockerhub.sz-alion.com/python:3.12-slim AS builder

# 设置工作目录
WORKDIR /happy_app

# 设置镜像源
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list.d/debian.sources \
    && sed -i 's|security.debian.org/debian-security|mirrors.ustc.edu.cn/debian-security|g' /etc/apt/sources.list.d/debian.sources

# 安装依赖
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc python3-dev supervisor curl \
    && rm -rf /var/lib/apt/lists/*

# 创建必要的目录并设置权限
RUN mkdir -p /var/logs/supervisor && \
    chown -R root:root /var/logs/supervisor && \
    chmod 755 /var/logs/supervisor

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn uvicorn


ENV TZ=Asia/Shanghai

RUN mkdir -p /var/logs/fastapi_server

# 复制配置文件
COPY deploy/fastapi_server.conf /etc/supervisor/conf.d/
COPY deploy/gunicorn.conf.py ./deploy/gunicorn.conf.py
COPY deploy/supervisor.conf ./deploy/supervisor.conf

# 复制项目文件
COPY src/ ./src/
COPY .env.production .env

# 设置环境变量
ENV PYTHONPATH=/happy_app \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000

# 创建非root用户
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /happy_app && \
    chown -R appuser:appuser /var/logs/supervisor && \
    chown -R appuser:appuser /var/logs/fastapi_server

# # 切换到非root用户
# USER appuser

# 健康检查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# 暴露端口
EXPOSE ${PORT}

# 启动命令
CMD ["/usr/bin/supervisord", "-n", "-c", "/happy_app/deploy/supervisor.conf"]


