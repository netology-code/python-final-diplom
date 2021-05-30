#!/bin/sh
docker build -t web_shop .
docker-compose up -d
echo
echo ENTERING python-final-diplom_web_1 CONTAINER LOGS
docker logs -f python-final-diplom_web_1
