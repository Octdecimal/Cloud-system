#!/bin/bash

# Navigate to the backend and run uvicorn
cd /backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload &

# Navigate to the frontend and run npm
cd /vue
npm run dev
