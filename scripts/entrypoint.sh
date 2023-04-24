#!/bin/sh -e 
mkdir -p /app/logs
chown ads:ads /app/logs
mkdir -p /app/logs/API
mkdir -p /app/logs/APP
chown ads:ads /app/logs/API
chown ads:ads /app/logs/APP
runsvdir -P /etc/service &
tail -f /dev/null


