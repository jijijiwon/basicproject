#!/bin/bash

python=$(ps -ef | grep 'python')
nodejs=$(ps -ef | grep 'node')
json=$(ps -ef | grep 'json-server')

second1=$(echo ${python} | cut -d " " -f2)    
second2=$(echo ${nodejs} | cut -d " " -f2)
second3=$(echo ${json} | cut -d " " -f2)


for var in $second1 $second2 $second3 
do
    echo $var
    if [ -n ${var} ]; then
        result=$(kill -9 ${var})
        echo process is killed.
    else
        echo running process not found.
    fi
done