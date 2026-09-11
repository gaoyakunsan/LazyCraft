#!/bin/bash

# 自签证书生成脚本
# 使用方法: ./generate-ssl-cert.sh

CERT_DIR="./ssl"
DOMAIN="localhost"
DAYS=3650  # 证书有效期10年
CERT_FILE="$CERT_DIR/server.crt"
KEY_FILE="$CERT_DIR/server.key"

# 创建ssl目录
mkdir -p $CERT_DIR

# 检查证书是否已存在
if [ -f "$CERT_FILE" ] || [ -f "$KEY_FILE" ]; then
    echo "⚠️  检测到已存在的SSL证书文件："
    [ -f "$CERT_FILE" ] && echo "  - $CERT_FILE"
    [ -f "$KEY_FILE" ] && echo "  - $KEY_FILE"
    echo ""
    read -p "是否覆盖现有证书？(y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "已取消，未生成新证书。"
        exit 0
    fi
    
    # 备份旧证书
    BACKUP_DIR="${CERT_DIR}_backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    [ -f "$CERT_FILE" ] && cp "$CERT_FILE" "$BACKUP_DIR/" && echo "已备份旧证书到: $BACKUP_DIR/server.crt"
    [ -f "$KEY_FILE" ] && cp "$KEY_FILE" "$BACKUP_DIR/" && echo "已备份旧私钥到: $BACKUP_DIR/server.key"
    echo ""
fi

echo "正在生成自签SSL证书..."

# 生成私钥和证书
openssl req -x509 -nodes -days $DAYS \
  -newkey rsa:2048 \
  -keyout $KEY_FILE \
  -out $CERT_FILE \
  -subj "/C=CN/ST=Beijing/L=Beijing/O=LazyCraft/OU=IT/CN=$DOMAIN" \
  -addext "subjectAltName=DNS:localhost,DNS:*.localhost,IP:127.0.0.1,IP:42.193.120.207"

# 设置权限
chmod 600 $KEY_FILE
chmod 644 $CERT_FILE

echo "✅ SSL证书生成完成！"
echo "证书路径: $CERT_FILE"
echo "私钥路径: $KEY_FILE"
echo ""
echo "注意: 这是自签证书，浏览器会显示不安全警告，这是正常的。"
echo "在生产环境中，请使用CA签发的正式证书。"
echo ""
if [ -f "$CERT_FILE" ] && [ -f "$KEY_FILE" ]; then
    echo "⚠️  如果nginx正在运行，请重启nginx容器以使新证书生效："
    echo "   docker-compose restart nginx"
fi

