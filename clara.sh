#!/bin/bash

API_PORT=8001
UI_PORT=5173

API_CMD="uvicorn api_server:app --reload --port $API_PORT"
UI_CMD="npm run dev"
UI_DIR="ui/chat_frontend"

LOG_DIR="logs/launcher"
mkdir -p $LOG_DIR

API_LOG="$LOG_DIR/api.log"
UI_LOG="$LOG_DIR/ui.log"
SUP_LOG="$LOG_DIR/supervisor.log"

# Variables globales pour les PIDs
API_PID=""
UI_PID=""
SUP_PID=""

clean_ports() {
    echo "🧹 Cleaning ports..." | tee -a $SUP_LOG
    lsof -ti tcp:$API_PORT | xargs kill -9 2>/dev/null
    lsof -ti tcp:$UI_PORT | xargs kill -9 2>/dev/null
}

start_api() {
    echo "🚀 Starting API..." | tee -a $SUP_LOG
    $API_CMD >> $API_LOG 2>&1 &
    API_PID=$!
    echo "API PID: $API_PID" | tee -a $SUP_LOG
}

start_ui() {
    echo "🚀 Starting UI..." | tee -a $SUP_LOG
    cd $UI_DIR
    npm install >/dev/null 2>&1
    $UI_CMD >> ../$UI_LOG 2>&1 &
    UI_PID=$!
    echo "UI PID: $UI_PID" | tee -a $SUP_LOG
    cd - >/dev/null
}

health_check() {
    while true; do
        sleep 3

        if ! kill -0 $API_PID 2>/dev/null; then
            echo "❌ API crashed — restarting..." | tee -a $SUP_LOG
            start_api
        fi

        if ! kill -0 $UI_PID 2>/dev/null; then
            echo "❌ UI crashed — restarting..." | tee -a $SUP_LOG
            start_ui
        fi
    done
}

clean_ports
start_api
start_ui

echo "✅ Clara running."
echo "🔗 UI: http://localhost:$UI_PORT"

health_check &
SUP_PID=$!

trap "echo '🛑 Stopping Clara...'; kill $API_PID $UI_PID $SUP_PID 2>/dev/null; exit" INT
wait

