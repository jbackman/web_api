#!/bin/sh
action=""
NAME="localhost"
LISTENER="0.0.0.0"
PORT="8080"

while getopts "n:l:p:o:t:s:dh" option; do
  echo ${OPTARG}	
  case "${option}" in
    n) export NAME=$OPTARG;;
    l) export LISTENER=$OPTARG;;
    p) export PORT=$OPTARG;;
    o) export DOHHOST=$OPTARG;;
    t) export DOHPORT=$OPTARG;;
    s) export DOHSCHEME=$OPTARG;;
    d) action="debug";;
    h) action="help";;
 esac
done
case $action in
  debug)
    echo "Running in Debug mode"
    export FLASK_APP=web.py
    export FLASK_ENV=development
    flask run --host $LISTENER --port $PORT
    ;;
  help)
    echo "Usage"
    echo "$0 [-n hostname] [-d] [-l IP] [-p port] [-o host] [-t port] [-s scheme]"
    echo "   -n hostname to display"
    echo "   -d debug mode"
    echo "   -l listening IP (default 0.0.0.0)"
    echo "   -p listening port (default 8080)"
    echo "   -o DNS over HTTP host"
    echo "   -t DNS over HTTP port"
    echo "   -s DNS over HTTP scheme (http or https)"
    echo
    ;;
  *)
    echo "Running in production mode"
    exec gunicorn -w 4 -b $LISTENER:$PORT web:app
esac
