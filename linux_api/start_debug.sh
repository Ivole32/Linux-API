#!/bin/bash

sleep 5

echo "DEMO_MODE = True" > config.env

python3 -m uvicorn --host=0.0.0.0 --port=8080 --reload server:app
