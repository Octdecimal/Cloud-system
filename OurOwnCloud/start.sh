#!/bin/bash

# Ensure screen is installed
apt-get update && apt-get install -y screen

# Get the container IP address
CONTAINER_IP=$(hostname -I | awk '{print $1}')
echo "Container is running on IP: $CONTAINER_IP"

# Start backend in a screen session
screen -dmS backend bash -c "cd /backend && uvicorn main:app --host 0.0.0.0 --port 8000 --reload"

# Start frontend in another screen session
screen -dmS frontend bash -c "cd /vue && npm run dev -- --host 0.0.0.0 --port 5173"

# Keep the container running
tail -f /dev/null