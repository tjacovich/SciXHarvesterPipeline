#!/bin/sh -e 

chown ads:ads /app/logs
mkdir -p /app/logs/API
mkdir -p /app/logs/APP
python3 /app/migrate_db.py
runsvdir -P /etc/service &
tail -f /dev/null


