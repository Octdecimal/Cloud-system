#!/bin/bash

# Get the container IP address
CONTAINER_IP=$(hostname -I | awk '{print $1}')
echo "Container is running on IP: $CONTAINER_IP"
# Navigate to the frontend and run npm
cd /vue
npm run dev -- --host 0.0.0.0 --port 5173 &

# # Navigate to the backend and run uvicorn
# cd /backend
# uvicorn main:app --host 0.0.0.0 --port 8000 --reload

