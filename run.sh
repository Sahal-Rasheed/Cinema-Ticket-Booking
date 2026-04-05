#!/bin/bash

# start the containers
docker compose up -d

# wait for the containers to be ready
echo "Waiting for Redis to be ready..."
until docker compose exec redis redis-cli ping | grep -q "PONG"; do
  sleep 1
done

# start the fastapi server
uvicorn main:app --host 127.0.0.1 --port 8000 --reload