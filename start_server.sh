#!/bin/bash

uvicorn pj_py.App:app --host 0.0.0.0 --port 3000 --reload &
nodemon pj_node/App.js &
json-server --watch pj_node/json/BikeStation.json --host 0.0.0.0 --port 5000 &
sleep 2s

ps -ef | grep 3000
ps -ef | grep 8000

sleep 3s
netstat -ntlp
