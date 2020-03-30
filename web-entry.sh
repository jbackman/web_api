#!/bin/sh
action=""
NAME="localhost"

while getopts ":dn:" option
do
 case "${option}" in
 n) NAME=$OPTARG;;
 d) action="debug";;
 esac
done
export NAME
if [ "$action" == "debug" ]; then
    echo "Running in Debug mode"
    export FLASK_APP=web.py
    export FLASK_ENV=development
    flask run --host 0.0.0.0 --port 8080
else
    echo "Running in production mode"
    exec gunicorn -w 4 -b 0.0.0.0:8080 web:app
fi
