#!/bin/bash

uvicorn pj_py.app:app --host 0.0.0.0 --port 3000 --reload &
nodemon /pj_node/app.js &
json-server --watch /pj_node/json/bikeStation_info\(23.12\).json --host 0.0.0.0 --port 5000 &
sleep 2s

ps -ef | grep 3000
ps -ef | grep 8000

sleep 3s
netstat -ntlp
