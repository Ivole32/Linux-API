#!/usr/bin/env bash

set -e

echo "This script requires that the Docker containers are already running."

ask() {
    while true; do
        read -rp "$1 (y/n): " yn
        case $yn in
            [Yy]* ) return 0 ;;
            [Nn]* ) return 1 ;;
            * ) echo "Please answer yes or no." ;;
        esac
    done
}

# Activate environment
if [ ! -d "venv" ]; then
    echo "Virtual environment not found!"
    exit 1
fi

source ./venv/bin/activate

if ask "Start server in background?"; then
    nohup python3 -m uvicorn api.server:app \
        --host 0.0.0.0 \
        --port 8080 \
        --log-level debug \
        > api.log 2>&1 &

    echo "Server started in background."
    echo "Logs: api.log"
    exit 0
fi

echo "Starting server in the foreground..."
python3 -m uvicorn api.server:app --host 0.0.0.0 --port 8080 --log-level debug