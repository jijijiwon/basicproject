#!/bin/bash

python=$(netstat -ntlp | grep 3000)
nodejs=$(netstat -ntlp | grep 8000)
json=$(netstat -ntlp | grep 5000)

second1=$(echo ${python} | cut -d " " -f7 | cut -d "/" -f1)    
second2=$(echo ${nodejs} | cut -d " " -f7 | cut -d "/" -f1)
second3=$(echo ${json} | cut -d " " -f7 | cut -d "/" -f1)


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