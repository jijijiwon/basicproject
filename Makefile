start:
	./start_server.sh
stop:
	kill -9 `ps -ef | grep json-server | cut -d " " -f8`
	kill -9 `netstat -ntlp | grep node | cut -d " " -f8`
	kill -9 `ps -ef | grep uvicorn | cut -d " " -f8`