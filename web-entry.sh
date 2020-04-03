#!/bin/sh
action=""
NAME="localhost"
LISTENER="0.0.0.0"
PORT="8080"

while getopts ":dnhplsoht:" option
do
 case "${option}" in
 n) NAME=$OPTARG;;
 d) action="debug";;
 l) LISTENER=$OPTARG;;
 p) PORT=$OPTARG;;
 o) DOH_HOST=$OPTARG;;
 s) DOH_SCHEME=$OPTARG;;
 t) DOH_PORT=$OPTARG;;
 h) action = "help";;
 
 esac
done
export NAME
case $action inn
  debug)
    echo "Running in Debug mode"
    export FLASK_APP=web.py
    export FLASK_ENV=development
    flask run --host $LISTENER --port $PORT
    ;;
  help)
    echo "Usage"
    echo "$0 [-n hostname] [-d] [-l IP] [-p port] [-o host] [-t port] [-s scheme]
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
    if [ -z "$DOH_HOST" ]; then export $DOH_HOST
    if [ -z "$DOH_SCHEME" ]; then export $DOH_SCHEME
    if [ -z "$DOH_PORT" ]; then export $DOH_PORT
    echo "Running in production mode"
    exec gunicorn -w 4 -b $LISTENER:$PORT web:app
esac
