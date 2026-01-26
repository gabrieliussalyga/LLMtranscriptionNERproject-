#!/bin/bash

# Start Medical NER Extraction - Backend and Frontend

cd "$(dirname "$0")"

echo "Medical NER Extraction"
echo "======================"
echo ""

# Stop existing backend (uvicorn on port 8000)
BACKEND_PIDS=$(lsof -ti:8000 2>/dev/null)
if [ -n "$BACKEND_PIDS" ]; then
    echo "Stopping existing backend (port 8000)..."
    kill $BACKEND_PIDS 2>/dev/null
    sleep 1
fi

# Stop existing frontend (vite on port 5173)
FRONTEND_PIDS=$(lsof -ti:5173 2>/dev/null)
if [ -n "$FRONTEND_PIDS" ]; then
    echo "Stopping existing frontend (port 5173)..."
    kill $FRONTEND_PIDS 2>/dev/null
    sleep 1
fi

echo "Syncing Schemas..."
source .venv/bin/activate
export PYTHONPATH=$PYTHONPATH:.

# 1. Generate JSON Schema
python scripts/generate_schema_file.py > full_schema.json
if [ $? -eq 0 ]; then
    echo "✅ JSON Schema generated"
else
    echo "❌ Failed to generate JSON Schema"
    exit 1
fi

# 2. Generate TypeScript types
npx -y json-schema-to-typescript full_schema.json > frontend/src/types/generated.ts
if [ $? -eq 0 ]; then
    echo "✅ Frontend types generated"
else
    echo "❌ Failed to generate frontend types"
    exit 1
fi

echo ""
echo "Starting services..."
echo ""

# Start backend in background
echo "Starting backend on http://localhost:8000..."
uvicorn backend.main:app --reload --port 8000 &
BACKEND_PID=$!

# Start frontend in background
echo "Starting frontend on http://localhost:5173..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "Services started:"
echo "  Backend:  http://localhost:8000 (API docs: http://localhost:8000/docs)"
echo "  Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both services"

# Handle shutdown
trap "echo ''; echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" SIGINT SIGTERM

# Wait for both processes
wait