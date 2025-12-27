#!/bin/bash

# Weltanschauung Startup Script
# Starts both backend and frontend servers

echo "🌌 Starting Weltanschauung..."
echo ""

# Check if virtual environment exists
if [ ! -d "backend/venv" ]; then
    echo "📦 Setting up backend..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
fi

# Start backend in background
echo "🚀 Starting backend server..."
cd backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!
cd ..

# Wait a bit for backend to start
sleep 3

# Check if node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend
    npm install
    cd ..
fi

# Start frontend
echo "🎨 Starting frontend server..."
cd frontend
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ Weltanschauung is running!"
echo ""
echo "📡 Backend:  http://localhost:8000"
echo "🎨 Frontend: http://localhost:3000"
echo ""
echo "📝 Logs:"
echo "   Backend:  tail -f backend.log"
echo "   Frontend: tail -f frontend.log"
echo ""
echo "🛑 To stop: kill $BACKEND_PID $FRONTEND_PID"
echo ""

# Keep script running
wait

