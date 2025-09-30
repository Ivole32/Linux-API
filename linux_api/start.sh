#!/bin/bash

sleep 5

echo "DEMO_MODE = False" > config.env

python3 -m uvicorn --host=0.0.0.0 --port=80 server:app
