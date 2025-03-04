# 故障排除指南

本文档提供了在使用Traefik作为API网关代理FastAPI服务时可能遇到的常见问题及其解决方案。

## 路径问题

### 问题1: 访问 `/api/docs` 返回 404

**症状**: 当访问 `http://localhost/api/docs` 时，返回 404 错误。

**原因**: 这通常是由于Traefik的路径前缀剥离与FastAPI的路由配置不匹配导致的。当Traefik剥离了`/api`前缀后，FastAPI不知道它应该在哪个路径下提供文档。

**解决方案**:

1. 在FastAPI应用中设置`root_path`参数:
   ```python
   app = FastAPI(
       # 其他参数...
       root_path="/api"
   )
   ```

2. 或者通过环境变量设置:
   ```yaml
   environment:
     - ROOT_PATH=/api
   ```

3. 确保Traefik配置中不要使用`stripPrefix`中间件，或者如果使用了，需要正确配置FastAPI的路由。

### 问题2: 访问 `/api/api/docs` 显示 "Failed to load API definition"

**症状**: 当访问 `http://localhost/api/api/docs` 时，Swagger UI加载，但显示 "Failed to load API definition"，无法加载 `/api/openapi.json`。

**原因**: 这通常是由于路径重复导致的。如果Traefik没有正确剥离路径前缀，或者FastAPI配置了错误的`root_path`，就会出现这种情况。

**解决方案**:

1. 确保只有一种方式处理路径前缀:
   - 要么使用Traefik的`stripPrefix`中间件
   - 要么使用FastAPI的`root_path`参数
   - 不要同时使用两者

2. 如果使用FastAPI的`root_path`，确保Traefik不剥离路径前缀:
   ```yaml
   # 在docker-compose.yml中移除这些标签
   # - "traefik.http.middlewares.api-strip.stripprefix.prefixes=/api"
   # - "traefik.http.routers.api.middlewares=api-strip@docker"
   ```

3. 检查浏览器开发者工具中的网络请求，查看OpenAPI JSON的请求URL是否正确。

## 健康检查问题

### 问题: 健康检查失败

**症状**: Traefik报告服务健康检查失败，无法路由请求。

**解决方案**:

1. 确保健康检查路径配置正确:
   ```yaml
   - "traefik.http.services.api.loadbalancer.healthcheck.path=/health"
   ```

2. 如果使用了`root_path`，可能需要调整健康检查路径:
   ```yaml
   - "traefik.http.services.api.loadbalancer.healthcheck.path=/api/health"
   ```

3. 检查FastAPI应用中的健康检查端点是否正确实现:
   ```python
   @app.get("/health")
   async def health_check():
       return {"status": "health"}
   ```

## HTTPS问题

### 问题: HTTPS证书错误

**症状**: 浏览器显示证书错误或不信任警告。

**解决方案**:

1. 对于开发环境，可以使用自签名证书，并在浏览器中手动接受风险。

2. 对于生产环境，使用Let's Encrypt或其他可信CA的证书:
   ```yaml
   certificatesResolvers:
     letsencrypt:
       acme:
         email: your-email@example.com
         storage: /etc/traefik/acme.json
         httpChallenge:
           entryPoint: web
   ```

3. 确保证书文件权限正确:
   ```bash
   chmod 600 /path/to/certificates/*
   ```

## 调试技巧

1. **查看Traefik日志**:
   ```bash
   docker-compose logs -f traefik
   ```

2. **查看FastAPI服务日志**:
   ```bash
   docker-compose logs -f api
   ```

3. **检查Traefik仪表盘**:
   访问 `http://localhost:8080` 查看路由、中间件和服务配置。

4. **使用curl测试API**:
   ```bash
   curl -v http://localhost/api/health
   ```

5. **检查Docker网络**:
   ```bash
   docker network inspect deploy_app-network
   ```

## 常见配置错误

1. **路径前缀重复**:
   - Traefik剥离了`/api`前缀
   - FastAPI也配置了`root_path="/api"`
   - 结果: 路径被处理两次

2. **健康检查路径错误**:
   - 健康检查路径应该是相对于服务的路径，不包含Traefik路由前缀

3. **CORS配置不正确**:
   - 确保CORS中间件配置了正确的允许源和方法

4. **网络配置问题**:
   - 确保所有服务都在同一个Docker网络中
   - 确保服务名称在网络中正确解析