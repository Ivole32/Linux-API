#!/bin/bash

cd "$(dirname "$(readlink -f "$0")")" || exit 1

sleep 3

echo "DEMO_MODE = True" > config.env

python3 -m uvicorn --host=0.0.0.0 --port=8080 --reload server:app
