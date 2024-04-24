#!/bin/bash

uvicorn ~.PycharmProjects.basicProject.app:app --host 0.0.0.0 --port 3000 --reload &
nodemon /pj_node/app.js &
sleep 2s

ps -ef | grep 3000
ps -ef | grep 8000

sleep 3s
netstat -ntlp