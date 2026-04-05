#!/bin/bash
# ─── Human Life Simulator — Server Launcher ───────────────────────────────────
# Always kills whatever is holding port 7860 before starting, so you NEVER
# see "Address already in use" again.
# Usage: ./run.sh

PORT=7860

echo ">>> Freeing port $PORT..."
# Kill any process holding the port (silent if nothing there)
fuser -k ${PORT}/tcp 2>/dev/null && echo "    Killed old process on :$PORT" || echo "    Port $PORT was already free"

sleep 1

echo ">>> Starting Human Life Simulator server on http://127.0.0.1:$PORT"
echo ">>> Dashboard: http://127.0.0.1:$PORT/dashboard"
echo ""

python3 -m uvicorn server:app --reload --port $PORT
