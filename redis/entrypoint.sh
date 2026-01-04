#!/bin/sh
set -e

APP_PASS="$(cat /run/secrets/redis_password)"
ADMIN_PASS="$(cat /run/secrets/redis_admin_password)"
HEALTH_PASS="$(cat /run/secrets/redis_health_password)"

# проверки
[ -n "$APP_PASS" ] || { echo "Teacher password missing"; exit 1; }
[ -n "$ADMIN_PASS" ] || { echo "Admin password missing"; exit 1; }
[ -n "$HEALTH_PASS" ] || { echo "Health password missing"; exit 1; }

# генерация ACL
sed \
  -e "s|{{APPLICATION_PASSWORD}}|$APP_PASS|g" \
  -e "s|{{ADMIN_PASSWORD}}|$ADMIN_PASS|g" \
  -e "s|{{HEALTH_PASSWORD}}|$HEALTH_PASS|g" \
  /usr/local/etc/redis/users.acl.tpl \
  > /usr/local/etc/redis/users.acl

chmod 600 /usr/local/etc/redis/users.acl

exec redis-server /usr/local/etc/redis/redis.conf
