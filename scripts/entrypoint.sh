#!/bin/sh -e 

chown ads:ads /app/logs
runsvdir -P /etc/service &
tail -f /dev/null


