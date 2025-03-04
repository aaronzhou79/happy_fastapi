# SSL证书目录

此目录用于存放SSL证书文件，用于HTTPS加密通信。

## 开发环境自签名证书生成

对于开发环境，可以使用以下命令生成自签名证书：

```bash
# 生成私钥
openssl genrsa -out default-key.pem 2048

# 生成证书签名请求
openssl req -new -key default-key.pem -out default.csr -subj "/CN=localhost/O=Happy FastAPI/C=CN"

# 生成自签名证书
openssl x509 -req -days 365 -in default.csr -signkey default-key.pem -out default-cert.pem
```

## 生产环境证书

对于生产环境，请使用以下方式获取证书：

1. 从可信证书颁发机构(CA)购买证书
2. 使用Let's Encrypt免费证书
3. 使用组织内部的证书颁发机构

将获取的证书文件重命名为：
- `cert.pem`: 证书文件
- `key.pem`: 私钥文件

然后取消注释 `deploy/traefik/config/tls.yml` 中的证书配置部分。

## 使用Let's Encrypt自动获取证书

Traefik支持通过ACME协议自动获取Let's Encrypt证书。要启用此功能，请修改 `deploy/traefik/traefik.yml` 文件，添加以下配置：

```yaml
certificatesResolvers:
  letsencrypt:
    acme:
      email: your-email@example.com
      storage: /etc/traefik/acme.json
      httpChallenge:
        entryPoint: web
```

然后在 `deploy/docker-compose.yml` 中的API服务标签中添加：

```yaml
- "traefik.http.routers.api.tls=true"
- "traefik.http.routers.api.tls.certresolver=letsencrypt"
```

## 安全注意事项

1. 确保证书文件的权限设置正确，只允许必要的用户访问
2. 定期更新证书，避免过期
3. 使用强密码保护私钥
4. 备份证书和私钥文件