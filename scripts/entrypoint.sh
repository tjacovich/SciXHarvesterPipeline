#!/bin/sh -e 

chown ads:ads /app/logs
mkdir -p /app/logs/API
mkdir -p /app/logs/APP
runsvdir -P /etc/service &
tail -f /dev/null


