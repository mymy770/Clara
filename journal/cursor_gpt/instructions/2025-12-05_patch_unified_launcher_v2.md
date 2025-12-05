# Patch — Unified Launcher v2 (API + UI + Supervisor + Health Check)

## 🎯 Objectif
Un lanceur unique ultra-robuste pour Clara :

- Une seule commande : `./clara.sh`
- Nettoyage des ports 8001 (API) et 5173 (UI)
- Lancement API + UI
- Superviseur qui restart automatiquement si crash
- Health-check toutes les 3 secondes
- Logs séparés et propres
- Makefile avec commandes run / stop / logs

---

# 1. Fichier à créer : `clara.sh`

Chemin :
Clara/clara.sh

Contenu :

```bash
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

clean_ports() {
    echo "🧹 Cleaning ports..." | tee -a $SUP_LOG
    lsof -ti tcp:$API_PORT | xargs kill -9 2>/dev/null
    lsof -ti tcp:$UI_PORT | xargs kill -9 2>/dev/null
}

start_api() {
    echo "🚀 Starting API..." | tee -a $SUP_LOG
    $API_CMD >> $API_LOG 2>&1 &
    API_PID=$!
}

start_ui() {
    echo "🚀 Starting UI..." | tee -a $SUP_LOG
    cd $UI_DIR
    npm install >/dev/null 2>&1
    $UI_CMD >> ../$UI_LOG 2>&1 &
    UI_PID=$!
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

2. Donner les droits d’exécution

Cursor doit exécuter :
chmod +x clara.sh

3. Makefile à créer / remplacer

Chemin :
Clara/Makefile

Contenu :
run:
	./clara.sh

stop:
	pkill -f "uvicorn" || true
	pkill -f "vite" || true
	pkill -f "clara.sh" || true

logs:
	tail -f logs/launcher/*.log
4. Résultat final

Commande unique :
./clara.sh

→ Ports nettoyés
→ API lancée
→ UI lancée
→ Superviseur actif
→ Auto-restart
→ Logs séparés
→ Arrêt propre

Fin du patch