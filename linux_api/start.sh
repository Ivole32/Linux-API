#!/bin/bash

sleep 5

echo "DEMO_MODE = False" > config.env

./venv/bin/python -m uvicorn --host=0.0.0.0 --port=80 server:app
