#!/bin/sh
docker kill ip_responder
docker rm ip_responder
docker rmi ip_responder:latest
docker build --tag ip_responder:latest .
docker run --restart always --name ip_responder -d -p 80:8080 ip_responder:latest -n $(hostname)
