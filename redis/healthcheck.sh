#!/bin/sh

# Attempt to ping Redis
pas=$(cat /run/secrets/redis_health_password)
response=$(redis-cli -u redis://health:"$pas"@127.0.0.1:6379 ping | grep PONG)

# Check the response
if [ "$response" != "PONG" ]; then
  echo "Health check failed: $response"
  exit 1
else
  echo "Redis responded: $response"
  exit 0
fi
