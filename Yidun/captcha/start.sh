#!/bin/bash
for((i=1;i<=10;));do
uwsgi --ini uwsgi.ini >/root/wangyi-chptcha/logs/`date +%y%m%d`.log  2>&1 &
sleep 24h
uwsgi --stop uwsgi.pid>/root/wangyi-chptcha/logs/`date +%y%m%d`.log 2>&1 &
echo `date`
done
